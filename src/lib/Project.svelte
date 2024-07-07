<script>
  import { registryNames } from "$lib/registries.js";
  import { abuseNames } from "$lib/registries.js";
  export let offset;
  export let q;

  function highlight(input, q) {
    if (!q) return input;
    return input.replace(new RegExp(q, "gi"), (match) => {
      return `<span class="hl">${match}</span>`;
    });
  }
</script>

<div class="project">
  <div class="meta">
    <div class="item">
      <span class="label">Total Credits:</span>
      <span class="value">{offset.total_credits.toLocaleString()}</span>
    </div>

    <div class="item">
      <span class="label">Location:</span>
      <span class="value">{offset.location}</span>
    </div>

    <div class="item">
      <span class="label">Developer:</span>
      <span class="value">{offset.developer}</span>
    </div>

    <div class="item">
      <span class="label">Status:</span>
      <span class="value">{offset.status}</span>
    </div>

    <div class="item">
      <span class="label">Methodology:</span>
      <span class="value">{offset.methodology}</span>
    </div>

    <div class="item">
      <span class="label">Type:</span>
      <span class="value">{offset.project_type}</span>
    </div>

    <div class="item">
      <span class="label">Registry:</span>
      <span class="value">{registryNames[offset.registry]}</span>
    </div>

    <div class="item">
      <span class="label">ID:</span>
      <span class="value"
        ><a href={offset.registry_url} target="_blank">{offset.registry_id}</a
        ></span
      >
    </div>

<!--     <div class="item">
      <span class="label">Casualties:</span>
      <span class="value">{offset.abuses}</span
      >
    </div>
 -->  </div>

  <div class="body">
    <h3>{@html highlight(offset.name, q)}</h3>
    <div class="desc">{@html highlight(offset.description, q)}</div>
    <div class="casu">{@html highlight(offset.abuse_descr, q)}</div>

    <div class="metacasu">
      <div style="margin-left: 0.3rem;" class="">
        <span class="valuecasu"
          >Documents:<br /><a href={offset.abuseuno_url} target="_blank">{offset.abuseuno_id}</a
          ></span
        >
      </div>
    </div>
  </div>
</div>

<style>
  :global(.hl) {
    background-color: var(--theme1);
  }

  h3 {
    margin: 0;
    /* border-bottom: 1px solid var(--fg); */
  }

  .meta {
    width: 30%;
    /* padding-top: 1.3rem; */
    font-size: 0.8rem;
  }

  .metacasu {
    width: 100%;
    margin-top: 1.3rem;
    font-size: 0.9rem;
    color: rgb(204, 11, 11);
  }


  .body {
    width: 70%;
  }

  .meta {
    text-align: right;
    padding-right: 1rem;
  }

  .valuecasu a {
    color: rgb(204, 11, 11);
  }

  .label {
    color: #999;
  }

  .item {
    border-bottom: 1px solid #ccc;
    /* margin-bottom: 0.3rem; */
    padding: 0.3rem;
  }

  .desc {
    margin-top: 0.1rem;
  }

  .casu {
    margin-top: 0.8rem;
    margin-left: 0.3rem;
    color: rgb(204, 11, 11);
    font-weight: 500;
  }

  .project {
    display: flex;
    flex-direction: row;
    padding: 1rem;
    border: 1px solid var(--fg);
    word-wrap: break-word;
  }
</style>
