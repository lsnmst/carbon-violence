<script>
  import "./styles.css";
  import { page } from "$app/stores";
  import { base } from '$app/paths';
</script>

<svelte:head>
  <title>Offset Archive</title>
</svelte:head>

<header>
  <a class="logo" href="/"><img src="/logo.gif" alt="Offset logo" />Offset Archive</a>
  <div class="subhead">A repository of carbon offset projects & sales</div>
  <nav>
    <a href="{base}/" class:active={$page.url.pathname === "/"}>Projects</a>
    <a href="{base}/sales" class:active={$page.url.pathname === "/sales"}>Sales</a>
    <!-- <a -->
    <!--   href="/methodologies" -->
    <!--   class:active={$page.url.pathname === "/methodologies"}>Methodologies</a -->
    <!-- > -->
    <a href="{base}/about" class:active={$page.url.pathname === "/about"}>About</a>
  </nav>
</header>

<main>
  <slot />
</main>