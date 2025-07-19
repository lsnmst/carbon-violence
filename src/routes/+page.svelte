<script>
  import { tick } from "svelte";
  import Project from "$lib/Project.svelte";
  import { registryNames } from "$lib/registries.js";
  import { abuseNames } from "$lib/registries.js";
  import { violenceTypes } from "$lib/registries.js";
  import { page } from "$app/stores";
  import { base } from "$app/paths";

  export let data;

  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  let q = data.q;
  let start = data.start;
  let count = data.count;
  let sortKey = data.sortKey;
  let methodologyFilter = data.methodologyFilter;
  let projectTypeFilter = data.projectTypeFilter;
  let registryFilter = data.registryFilter;
  let abusesFilter = data.abusesFilter;
  let violenceFilter = data.violenceFilter;
  let sortOrder = data.sortOrder;
  let methodologies = data.methodologies;
  let abuses = data.abuses;
  let violence = data.violence;
  let projectTypes = data.projectTypes;
  let form;
  let loading = false;
  let showFilters = !isMobile;
  let shouldAutoFocus = false;

  $: offsetsSlice = data.offsetsSlice;
  $: total = data.total;

  const sortKeys = [
    { key: "name", text: "Name" },
    { key: "total_credits", text: "Total Credits Issued" },
  ];

  async function subForm() {
    start = 0;
    await tick();
    form.requestSubmit();
  }

  function clearForm() {
    q = "";
    start = 0;
    count = 50;
    projectTypeFilter = null;
    methodologyFilter = null;
    registryFilter = null;
    abusesFilter = null;
    violenceFilter = null;
    sortKey = "total_credits";
    sortOrder = "desc";
  }

  async function nextPage() {
    start += count;
    if (start > total) start = total - count;
    await tick();
    form.requestSubmit();
  }

  async function prevPage() {
    start -= count;
    if (start < 0) start = 0;
    await tick();
    form.requestSubmit();
  }
</script>

<div class="project-container">
  <form class="filters" method="GET" action="{base}/" bind:this={form}>
    <div class="help">
      <!--       Information from the <a href="https://offsetarchive.labr.io/">Offset project</a> has been scraped from the four major carbon
      registries. Each entry describes a project that has been approved as an
      offset by one of these registries. 
 -->
      <!--       <span
        >Carbon Violence is an initiative to link carbon offset projects cloned
        from the <a href="https://offsetarchive.labr.io/">Offset Archive</a> to occurrences
        of (physical, economic, psychological, epistemic) violence whose local communities
        living in the project areas have been identified as casualties</span
      >
 -->
      <span
        >Carbon Violence exposes occurrences of physical, economic,
        psychological and epistemic violence in the areas where carbon
        offsetting projects registered to the voluntary offset market are
        implemented</span
      >
      <span>
        <br /><br /><a
          href="{base}/about"
          class:active={$page.url.pathname === "/about"}><i>Read more..</i></a
        >
      </span>
    </div>
    <div class="filter">
      <input
        type="text"
        placeholder="Search"
        name="q"
        autofocus={shouldAutoFocus}
        bind:value={q}
        on:keyup={() => {
          start = 0;
          form.requestSubmit();
          shouldAutoFocus = true;
        }}
        on:blur={() => {
          shouldAutoFocus = false;
        }}
      />
      <div class="toggle-filters-holder">
        <a
          href="#"
          class="toggle-filters"
          on:click|preventDefault={() => {
            showFilters = !showFilters;
          }}
        >
          {#if showFilters}Hide filters{:else}Show filters{/if}
        </a>
      </div>
    </div>

    <div class="all-filters" style="display: {showFilters ? 'block' : 'none'}">
      <div class="filter">
        <label for="sort">Sort by</label>
        <select name="sort" id="sort" bind:value={sortKey} on:change={subForm}>
          {#each sortKeys as s}
            <option value={s.key}>
              {s.text}
            </option>
          {/each}
        </select>

        <select name="sortOrder" bind:value={sortOrder} on:change={subForm}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>

      <div class="filter">
        <label for="abs">Casualties</label>
        <select
          name="abuses"
          id="abs"
          bind:value={abusesFilter}
          class="long-select"
          on:change={subForm}
        >
          <option value={null}>-</option>
          {#each Object.keys(abuses).sort() as w}
            <option value={w}>
              <!-- {w} ({abuses[w]}) -->
              {w}
            </option>
          {/each}
        </select>
      </div>

      <div class="filter">
        <label for="vio">Violence</label>
        <select
          name="violence"
          id="vio"
          bind:value={violenceFilter}
          class="long-select"
          on:change={subForm}
        >
          <option value={null}>All Violence Types</option>
          {#each Object.keys(violenceTypes).sort() as v}
            <option value={v}>
              {violenceTypes[v]}
            </option>
          {/each}
        </select>
      </div>

      <div class="filter">
        <label for="meth">Registry</label>
        <select
          name="registry"
          id="reg"
          bind:value={registryFilter}
          class="long-select"
          on:change={subForm}
        >
          <option value={null}>All Registries</option>
          {#each Object.keys(registryNames).sort() as r}
            <option value={r}>
              {registryNames[r]}
            </option>
          {/each}
        </select>
      </div>

      <!--       
      <div class="filter">
        <label for="meth">Methodologies</label>
        <select
          name="methodology"
          id="meth"
          bind:value={methodologyFilter}
          class="long-select"
          on:change={subForm}
        >
          <option value={null}>All Methodologies</option>
          {#each Object.keys(methodologies).sort() as m}
            <option value={m}>
              {m} ({methodologies[m]})
            </option>
          {/each}
        </select>
      </div>
 -->

      <div class="filter">
        <label for="ptype">Project Type</label>
        <select
          name="projectType"
          id="ptype"
          bind:value={projectTypeFilter}
          class="long-select"
          on:change={subForm}
        >
          <option value={null}>All Project Types</option>
          {#each Object.keys(projectTypes).sort() as t}
            <option value={t}>
              {t} ({projectTypes[t]})
            </option>
          {/each}
        </select>
      </div>

      <div class="filter">
        <button class="reset" on:click={clearForm}>Reset</button>
        <!-- <button type="submit">Apply</button> -->
      </div>
      <input type="hidden" name="start" bind:value={start} />
    </div>
  </form>

  <div class="offsets">
    {#if loading}
      <div>Loading...</div>
    {:else}
      <div class="pagination">
        <div class="page-counts">
          {#if total > 0}
            {start + 1} to {start + Math.min(count, total)} of {total}
          {:else}
            No results found.
          {/if}
        </div>
        <div class="page-buttons">
          {#if start > 0}
            <button on:click={prevPage}>Prev</button>
          {/if}
          {#if start + count < total}
            <button on:click={nextPage}>Next</button>
          {/if}
        </div>
      </div>
      <div class="offsets-inner">
        {#each offsetsSlice as offset (offset.id)}
          <Project {offset} {q} />
        {/each}
      </div>
      <div class="pagination">
        <div class="page-counts">
          {#if total > 0}
            {start + 1} to {start + Math.min(count, total)} of {total}
          {:else}
            No results found.
          {/if}
        </div>
        <div class="page-buttons">
          {#if start > 0}
            <button on:click={prevPage}>Prev</button>
          {/if}
          {#if start + count < total}
            <button on:click={nextPage}>Next</button>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .project-container {
    display: grid;
    grid-template-columns: 200px minmax(0, 1fr);
    margin-top: 1rem;
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
  .offsets {
    min-width: 0;
  }
  .offsets-inner {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
    grid-gap: 1rem;
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
  .toggle-filters-holder {
    display: none;
  }

  @media (max-width: 768px) {
    .project-container {
      grid-template-columns: 1fr;
    }
    .offsets-inner {
      grid-template-columns: 100%;
    }
    .filters {
      margin-right: 0px;
      padding-right: 0px;
      border-right: none;
    }
    .toggle-filters-holder {
      display: block;
      margin-top: 3px;
      text-align: right;
      font-size: 0.8em;
    }
  }
</style>
