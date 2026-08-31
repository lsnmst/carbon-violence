"""
sales.py

Adaptation of scrapers/export_sales.py (antiboredom's "offset-archive" project)
for the carbon-violence repository.

Differences from the original:
  1. It also extracts the “beneficiary” column (Retirement Beneficiary / Account Holder),
     missing from the original script, to match the header in sales.json:
     ["id", "date", "beneficiary", "details", "total", "type"]
  2. Filter the transactions, keeping only those whose (registry, id) match
     to a project in data.json with “abuses”: “Reported”.
  3. Merge it with the existing sales.json file (removing duplicates) instead of overwriting
     everything from scratch, so also keep the lines manually added in the past.

    python export_reported_sales.py \
        --data-json path/o/url/a/data.json \
        --sales-json path/o/url/a/sales.json \
        --out static/sales.json

Requires: pandas, requests, beautifulsoup4, openpyxl (per leggere il .xlsx di Verra)
    pip install pandas requests beautifulsoup4 openpyxl

"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

ZIP_URL_BASE = "https://gspp.berkeley.edu"
# The page has moved from the URL used by the original script
ZIP_URL_HOME = ZIP_URL_BASE + "/berkeley-carbon-trading-project/offsets-database"

# type code -> Registry name used in data.json
TYPE_TO_REGISTRY = {
    0: "gold",   # Gold Standard
    1: "verra",  # Verra / VCS
    2: "acr",    # American Carbon Registry
    3: "car",    # Climate Action Reserve
}

# Aliases found in data.json that refer to the same registry
# (e.g., “gold_standard” instead of “gold”). They map directly to the type code.
REGISTRY_ALIASES = {
    "gold_standard": 0,
    "goldstandard": 0,
    "gold standard": 0,
}

# For Verra and Gold, project IDs are numeric (e.g., 2887, 11484) and 
# are compared as integers. For ACR and CAR, they are alphanumeric with
# a prefix (e.g., “ACR0102,” “CAR1957”) and should be compared as strings.
NUMERIC_ID_TYPES = {0, 1}

HEADERS = ["id", "date", "beneficiary", "details", "total", "type"]


# ---------------------------------------------------------------------------
# Download + parsing 
# ---------------------------------------------------------------------------

def find_registry_files_url():
    """
    Find the link to the “raw registry files” in a robust way by searching through
    all the <a> tags on the page for an href that contains “registry-files”
    (case-insensitive), rather than relying on the exact text of the link 
    ((which Berkeley has changed several times: "Download the raw registry
    files", "Raw registry here files, vXXXX-XX", ecc.)
    """
    resp = requests.get(ZIP_URL_HOME)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    candidates = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"registry.?files", href, re.IGNORECASE):
            candidates.append(href)

    if not candidates:
        raise RuntimeError(
            "No links to ‘raw registry files’ were found on the page "
            f"{ZIP_URL_HOME}. The page layout may have "
            "changed again: check the page manually."
        )

    href = candidates[0]
    if href.startswith("http"):
        return href
    return ZIP_URL_BASE + href


def download_raw():
    url = find_registry_files_url()
    print(f"URL found: {url}")

    local_name = "sales_data" + Path(url).suffix 
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Scaricato in {local_name}")
    return local_name


def inspect_workbook(fname):
    """
    Diagnostic utility: prints the name of each sheet and its columns.
    Useful in case Berkeley changes the file structure again in the future.
    """
    sheets = pd.read_excel(fname, sheet_name=None, nrows=3)
    for name, df in sheets.items():
        print(f"\n=== Sheet: {name!r} ===")
        print("Columns:", list(df.columns))
        print(df.head(2).to_string())


def fix_mojibake(text):
    """
    This corrects the mojibake present in the Verra/ACR/CAR source data:
    text that was originally in UTF-8 but was decoded using
    the Mac OS Roman encoding somewhere upstream (e.g., “√ß” instead of 
    "ç", "√â" instead of  "É"). This is corrected by re-encoding as mac_roman 
    and re-decoding as UTF-8.
    """
    if not isinstance(text, str) or not text:
        return text

    try:
        import ftfy  
        return ftfy.fix_text(text)
    except ImportError:
        pass

    if "√" not in text:
        return text
    try:
        return text.encode("mac_roman").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


def _select_and_rename(df, colmap):
    """colmap: dict {original column: final column}. It keeps only the
    required columns (some may be missing from the sheet; they are
    filled with NaN) and renames them according to colmap."""
    for src in colmap:
        if src not in df.columns:
            df[src] = pd.NA
    df = df[list(colmap.keys())].rename(columns=colmap)
    return df


def parse_gold(sheets):
    print("Gold Standard (sheet 'Gold Retirements')")
    df = sheets["Gold Retirements"].copy()

    if "Credit Status" in df.columns:
        df = df[df["Credit Status"].astype(str).str.strip().eq("Retired")]

    df = _select_and_rename(
        df,
        {
            "GSID": "id",
            "Retirement Date": "date",
            "Using Entity": "beneficiary",
            "Note": "details",
            "Quantity": "total",
        },
    )
    df["type"] = 0
    return df


def parse_acr(sheets):
    print("ACR (foglio 'ACR Retirements')")
    df = sheets["ACR Retirements"].copy()

    if "Status of Credits" in df.columns:
        df = df[df["Status of Credits"].astype(str).str.strip().eq("Retired")]

    df = _select_and_rename(
        df,
        {
            "Project Id": "id",
            "Status Effective (GMT)": "date",
            "Retired On Behalf Of": "beneficiary",
            "Purpose of Retirement": "details",
            "Quantity of Credits": "total",
        },
    )
    df["type"] = 2
    return df


def parse_car(sheets):
    print("CAR (sheet 'CAR Retirements')")
    df = sheets["CAR Retirements"].copy()

    df = _select_and_rename(
        df,
        {
            "Project ID": "id",
            "Status Effective": "date",
            "Account Holder": "beneficiary",
            "Retirement Reason Details": "details",
            "Quantity of Offset Credits": "total",
        },
    )
    df["type"] = 3
    return df


def parse_verra(sheets):
    print("Verra (sheet 'Verra VCUS')")
    df = sheets["Verra VCUS"].copy()

    # Il foglio contiene sia le emissioni (issuance) sia i ritiri
    # (retirement) sulla stessa riga: teniamo solo le righe
    # effettivamente ritirate.
    df = df[df["Retirement/Cancellation Date"].notna()]

    df = _select_and_rename(
        df,
        {
            "ID": "id",
            "Retirement/Cancellation Date": "date",
            "Retirement Beneficiary": "beneficiary",
            "Retirement Details": "details",
            "Quantity Issued": "total",
        },
    )
    df["type"] = 1
    return df


PARSERS = {
    0: parse_gold,
    1: parse_verra,
    2: parse_acr,
    3: parse_car,
}

REQUIRED_SHEETS = {
    "Gold Retirements",
    "Verra VCUS",
    "ACR Retirements",
    "CAR Retirements",
}


def combine_data(xlsx_path):
    print("Reading the workbook (wait few minutes)...")
    sheets = pd.read_excel(xlsx_path, sheet_name=list(REQUIRED_SHEETS))

    all_dfs = [parser(sheets) for parser in PARSERS.values()]
    all_df = pd.concat(all_dfs, ignore_index=True)
    all_df = all_df[HEADERS]

    all_df["date"] = pd.to_datetime(
        all_df["date"], format="mixed", errors="coerce", utc=True
    )

    all_df.dropna(subset=["id", "date", "total", "type"], inplace=True)
    all_df["beneficiary"] = all_df["beneficiary"].fillna("").apply(fix_mojibake)
    all_df["details"] = all_df["details"].fillna("").apply(fix_mojibake)
    all_df["date"] = all_df["date"].dt.strftime("%Y-%m-%d")

    def norm_id(row):
        if row["type"] in NUMERIC_ID_TYPES:
            try:
                return int(float(row["id"]))
            except (ValueError, TypeError):
                return None
        return str(row["id"]).strip()

    all_df["id"] = all_df.apply(norm_id, axis=1)
    all_df.dropna(subset=["id"], inplace=True)

    return all_df


# ---------------------------------------------------------------------------
# Filter on “Reported” projects
# ---------------------------------------------------------------------------

def load_json(path_or_url):
    if str(path_or_url).startswith("http"):
        return requests.get(path_or_url).json()
    with open(path_or_url, encoding="utf-8") as f:
        return json.load(f)


def reported_ids_by_type(data_json_path):
    """
    Returns a set of tuples (type, id) for all projects in data.json
    where abuses == “Reported,” using TYPE_TO_REGISTRY to convert
    the ‘registry’ field to the “type” code used by sales.json.
    """
    data = load_json(data_json_path)
    wanted = set()
    skipped_registries = set()

    registry_to_type = {v: k for k, v in TYPE_TO_REGISTRY.items()}

    for project in data:
        if project.get("abuses") != "Reported":
            continue

        registry = (project.get("registry") or "").strip().lower()
        raw_id = (project.get("registry_id") or "").strip()

        type_code = registry_to_type.get(registry)
        if type_code is None:
            type_code = REGISTRY_ALIASES.get(registry)
        if type_code is None:
            skipped_registries.add(registry)
            continue

        if type_code in NUMERIC_ID_TYPES:
            try:
                proj_id = int(raw_id)
            except ValueError:
                continue
        else:
            proj_id = raw_id.strip()
            if not proj_id:
                continue

        wanted.add((type_code, proj_id))

    if skipped_registries:
        print(
            "Records with `abuses=Reported` but not covered by Berkeley "
            f"database (ignored): {sorted(skipped_registries)}"
        )

    return wanted


def filter_reported(all_df, wanted_ids):
    mask = all_df.apply(lambda r: (r["type"], r["id"]) in wanted_ids, axis=1)
    return all_df[mask].copy()


# ---------------------------------------------------------------------------
# Merge with the existing sales.json
# ---------------------------------------------------------------------------

def merge_with_existing(new_df, sales_json_path):
    existing = load_json(sales_json_path)
    existing_df = pd.DataFrame(existing["values"], columns=existing["headers"])
    existing_df = existing_df[HEADERS]

    combined = pd.concat([existing_df, new_df], ignore_index=True)
    combined.drop_duplicates(
        subset=["id", "date", "beneficiary", "details", "total", "type"],
        inplace=True,
    )
    combined.sort_values("date", ascending=False, inplace=True)
    return combined


def save_sales_json(df, out_path):
    values = df[HEADERS].values.tolist()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"headers": HEADERS, "values": values}, f, ensure_ascii=False)
    print(f"Salvato {len(values)} transazioni in {out_path}")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data-json",
        default="https://raw.githubusercontent.com/lsnmst/carbon-violence/refs/heads/main/static/data.json",
        help="Path or URL to data.json",
    )
    ap.add_argument(
        "--sales-json",
        default="https://raw.githubusercontent.com/lsnmst/carbon-violence/refs/heads/main/static/sales.json",
        help="Path or URL to an existing sales.json file to be updated (merged)",
    )
    ap.add_argument(
        "--out",
        default="static/sales.json",
        help="Where to save the updated sales.json file",
    )
    ap.add_argument(
        "--xlsx",
        default=None,
        help="Path to a previously downloaded VROD registry file (.xlsx); skip the download",
    )
    ap.add_argument(
        "--inspect",
        action="store_true",
        help="Download (or use --xlsx) and print only the file structure "
        "(sheets/columns), without parsing or filtering. Use this if Berkeley "
        "changes the format again.",
    )
    args = ap.parse_args()

    xlsx_path = args.xlsx or download_raw()

    if args.inspect:
        inspect_workbook(xlsx_path)
        return

    if Path(xlsx_path).suffix.lower() != ".xlsx":
        raise SystemExit(
            f"The downloaded file ({xlsx_path}) is not an .xlsx file: "
            "the Berkeley format may have changed again. Run it first with "
            "--inspect to view the structure."
        )

    all_df = combine_data(xlsx_path)
    print(f"Total transactions (retirements) retrieved from the Berkeley database: {len(all_df)}")

    wanted_ids = reported_ids_by_type(args.data_json)
    print(f"Projects (registry, id) with “abuses=Reported” covered: {len(wanted_ids)}")

    reported_df = filter_reported(all_df, wanted_ids)
    print(f"Transactions filtered by “Reported” projects: {len(reported_df)}")

    final_df = merge_with_existing(reported_df, args.sales_json)
    save_sales_json(final_df, args.out)


if __name__ == "__main__":
    main()