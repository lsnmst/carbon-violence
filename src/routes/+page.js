let offsetData;
let loaded = false;
const methodologies = {};
const abuses = {};
const violence = {};
const projectTypes = {};
import { base } from '$app/paths';

async function loadData(fetch) {
  if (loaded) {
    return true;
  }

  let response = await fetch(`${base}/data.json`);
  offsetData = await response.json();

  offsetData.forEach((p, i) => {
    p.id = i;

    if (!p.name) p.name = "No name";
    if (!p.description) p.description = "No description";
    if (!p.abuse_descr) p.abuse_descr = 'No casualties reported to the archive. If you want to report an occourence, please follow the <a href="https://ee-eu.kobotoolbox.org/x/YzOtiWsK"> link</a>';
    if (!p.abuseuno_id) p.abuseuno_id = "-";
    if (!p.abuseuno_url) p.abuseuno_url = null;
    if (!p.violence) p.violence = null;


    const pAbuses = p.abuses
      ? p.abuses.split(";").map((m) => m.trim())
      : ["Unknown"];
    const pViolence = p.violence
      ? p.violence.split(";").map((m) => m.trim())
      : ["Unknown"];
    const pMethodologies = p.methodology
      ? p.methodology.split(";").map((m) => m.trim())
      : ["Unknown"];
    const pTypes = p.project_type
      ? p.project_type.split(";").map((m) => m.trim())
      : ["Unknown"];


    pAbuses.forEach((w) => {
      abuses[w] = abuses[w] ? abuses[w] + 1 : 1;
    });

    pViolence.forEach((v) => {
      violence[v] = violence[v] ? violence[v] + 1 : 1;
    });

    pMethodologies.forEach((m) => {
      methodologies[m] = methodologies[m] ? methodologies[m] + 1 : 1;
    });

    pTypes.forEach((t) => {
      projectTypes[t] = projectTypes[t] ? projectTypes[t] + 1 : 1;
    });

  });
  loaded = true;
}

export async function load({ url, fetch }) {
  await loadData(fetch);
  let start = url.searchParams.get("start") || 0;
  start = +start;
  if (start < 0 || !start) start = 0;

  let count = url.searchParams.get("count") || 50;
  count = +count;
  if (count < 0 || !count) count = 50;

  let sortKey = url.searchParams.get("sort") || "total_credits";
  let sortOrder = url.searchParams.get("sortOrder") || "desc";

  let methodologyFilter = url.searchParams.get("methodology") || null;

  let projectTypeFilter = url.searchParams.get("projectType") || null;

  let registryFilter = url.searchParams.get("registry") || null;

  let abusesFilter = url.searchParams.get("abuses") || null;

  let violenceFilter = url.searchParams.get("violence") || null;


  let q = url.searchParams.get("q") || "";

  const offsets = [...offsetData]
    .sort((a, b) => {
      const comp = sortOrder === "asc" ? 1 : -1;
      if (a[sortKey] < b[sortKey]) {
        return -1 * comp;
      }
      if (a[sortKey] > b[sortKey]) {
        return 1 * comp;
      }
      return a.id - b.id;
    })
    .filter((p) => {
      if (q == "") {
        return true;
      }

      return (
        p.registry_id == q ||
        p.name.toLowerCase().indexOf(q.toLowerCase()) > -1 ||
        p.description.toLowerCase().indexOf(q.toLowerCase()) > -1
      );
    })
    .filter((p) => {
      if (methodologyFilter === null) return true;

      return p.methodology == methodologyFilter;
    })
    .filter((p) => {
      if (projectTypeFilter === null) return true;

      return p.project_type == projectTypeFilter;
    })
    .filter((p) => {
      if (registryFilter === null) return true;

      return p.registry == registryFilter;
    })
    .filter((p) => {
      if (abusesFilter === null) return true;

      return p.abuses == abusesFilter;
    })
    .filter((p) => {
      if (!violenceFilter) return true;
      if (!p.violence) return false;
      return p.violence.split(",").map((v) => v.trim()).includes(violenceFilter);
    });

  const offsetsSlice = offsets.slice(start, start + count);

  return {
    total: offsets.length,
    offsetsSlice,
    start,
    count,
    q,
    sortKey,
    methodologyFilter,
    projectTypeFilter,
    registryFilter,
    abusesFilter,
    violenceFilter,
    methodologies,
    abuses,
    violence,
    projectTypes,
    sortOrder,
  };
}
