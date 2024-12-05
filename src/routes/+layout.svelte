<script>
  import "./styles.css";
  import { page } from "$app/stores";
  import { base } from '$app/paths';
</script>

<svelte:head>
  <title>Carbon Violence</title>
</svelte:head>

<header>
  <a class="logo" href="{base}/"><img src="{base}/logo.gif" alt="Offset logo" />Carbon Violence</a>
  <div class="subhead">A repository of carbon <span style=" ">offsetting's casualties</span></div>
  <nav>
    <a href="{base}/" class:active={$page.url.pathname === "/"}>casualties</a>

    <a href="{base}/sales" class:active={$page.url.pathname === "/sales"}>bloody credits</a>

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