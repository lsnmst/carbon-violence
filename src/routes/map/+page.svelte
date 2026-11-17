<script>
  import { onMount } from "svelte";
  import { Map, TileLayer, GeoJSON } from "sveaflet";
  import L from "leaflet";
  import { points } from "./points.js";
  import { base } from "$app/paths";

  let dataById = new globalThis.Map();
  let dataByName = new globalThis.Map();
  let dataLoaded = false;

  function normalizeId(value) {
    return String(value ?? "")
      .trim()
      .toUpperCase()
      .replace(/^(ECO|GLD)/, "");
  }

  function normalizeName(value) {
    return String(value ?? "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  onMount(async () => {
    try {
      const response = await fetch(`${base}/data.json`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`Errore HTTP: ${response.status}`);
      }

      const records = await response.json();

      if (!Array.isArray(records)) {
        throw new Error("data.json non contiene un array");
      }

      const indexById = new globalThis.Map();
      const indexByName = new globalThis.Map();

      for (const item of records) {
        const id = normalizeId(item.registry_id);
        const name = normalizeName(item.name);

        if (id) {
          if (!indexById.has(id)) {
            indexById.set(id, []);
          }
          indexById.get(id).push(item);
        }

        if (name) {
          indexByName.set(name, item);
        }
      }

      dataById = indexById;
      dataByName = indexByName;
      dataLoaded = true;

      console.log("Record caricati:", records.length);
      console.log("Chiavi ID:", dataById.size);
      console.log("Chiavi nome:", dataByName.size);
    } catch (error) {
      console.error("Errore caricamento data.json:", error);
    }
  });

  function onEachFeature(feature, layer) {
    const p = feature.properties || {};

    layer.bindPopup(() => {
      const id = normalizeId(p.ID);
      const name = normalizeName(p.name);

      const matches = dataById.get(id) || [];
      const extra = matches[0] || dataByName.get(name) || {};

      let popupContent = `
        <span><b>${p.name || ""}</b></span>
        <br />
        <span>Project area: ${p.area ?? "N/A"} Ha</span>
        <hr>
        <p>
          Project ID:
          <a href="${p.link || "#"}" target="_blank"
             rel="noopener noreferrer">${p.ID ?? ""}</a>
        </p>
      `;

      if (extra.abuseuno_id && extra.abuseuno_url) {
        popupContent += `
          <hr><p>Documents:<br/><br/>
            <a href="${extra.abuseuno_url}" target="_blank"
               rel="noopener noreferrer">
              ${extra.abuseuno_id}
            </a>
          </p>
        `;
      }

      if (extra.abusedue_id && extra.abusedue_url) {
        popupContent += `
          <p>
            <a href="${extra.abusedue_url}" target="_blank"
               rel="noopener noreferrer">
              ${extra.abusedue_id}
            </a>
          </p>
        `;
      }

      return popupContent;
    });
  }
</script>

<div class="map-container">
  <div class="land-project-container">
    <div class="help">
      <div class="number">16,059,840</div>
      <br />Total area (in hectares) occupied by projects where occurrences of
      physical, economic, psychological and epistemic violence have been
      exposed.<br /><br />An area equivalent to: <b>Suriname</b><br /><br /><br
      /><br /><br />Last update 20th May 2026
    </div>
  </div>
  <div class="land-project-container">
    <div class="help">
      <div class="number">27 out of 27</div>
      <br />Number of Global South countries in relation to the total number of
      countries where violence was exposed.<br />Of the total number of projects
      investigated, 25% are exclusively managed by organisations and companies
      with their registered office in the Global North. Otherwise, it is
      possible to recognise among those involved subsidiaries, investors,
      validation and verification bodies all based in the Global North.
    </div>
  </div>
</div>

<div style="width: 100%;height: 500px;">
  <Map options={{ center: [0, 0], zoom: 2 }}>
    <TileLayer
      url={"https://api.mapbox.com/styles/v1/comuni-dados/ckbktovto0w4r1jnye9da9hs7/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiY29tdW5pLWRhZG9zIiwiYSI6ImNqdWxlaHRqbjIycjE0M3BpamY3a3c4aWUifQ.HGizp_QckKQVjAZnnw8qAg"}
      options={{
        maxZoom: 7,
        attribution: "",
      }}
    />
    {#if dataLoaded}
      <GeoJSON
        json={[points]}
        options={{
          style(feature) {
            return feature.properties && feature.properties.style;
          },
          onEachFeature,
          pointToLayer(feature, latlng) {
            return L.circleMarker(latlng, {
              radius: 4,
              fillColor: "#ff780000",
              color: "#000",
              weight: 3,
              opacity: 0.8,
              fillOpacity: 0.8,
            });
          },
        }}
      />
    {/if}
  </Map>
</div>

<style>
  table {
    border-collapse: collapse;
    width: 100%;
  }
  th {
    font-weight: normal;
    text-align: left;
  }
  td,
  th {
    border-bottom: 1px solid #000;
    padding: 10px;
    vertical-align: top;
  }
  th {
    /* white-space: nowrap; */
  }
  td {
    overflow-wrap: anywhere;
  }
  .project-container {
    display: grid;
    grid-template-columns: 200px minmax(0, 1fr);
    margin-top: 1rem;
  }
  .map-project-container {
    display: grid;
    grid-template-columns: 200px minmax(0, 1fr);
    margin-top: 1rem;
    padding: 10px;
  }
  .land-project-container {
    display: grid;
    grid-template-columns: 300px minmax(0, 1fr);
    margin-top: 1rem;
    padding: 10px;
  }
  .number {
    font-size: 1.75em;
    font-weight: bold;
  }
  .filters {
    margin-right: 1rem;
    padding-right: 1rem;
    border-right: 1px solid var(--fg);
  }
  .filter,
  .help {
    margin-bottom: 1.5rem;
  }
  .help {
    font-size: 0.9em;
  }
  label,
  select,
  input,
  button {
    display: block;
    width: 100%;
    padding: 3px;
    margin-top: 5px;
  }
  label {
    padding: 0;
  }
  button[type="submit"] {
    background-color: var(--theme1);
  }
  .reset {
    border: 1px var(--theme1) solid;
    cursor: pointer;
  }

  .pagination {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  .pagination button {
    display: inline-block;
    width: auto;
  }
  @media (max-width: 768px) {
    .project-container {
      display: grid;
      grid-template-columns: 100%;
      margin-top: 1rem;
    }
    .land-project-container {
      display: grid;
      grid-template-columns: 100%;
      margin-top: 1rem;
    }
    .filters {
      margin-right: 0;
      padding-right: 0;
      border-right: none;
    }
  }
</style>
