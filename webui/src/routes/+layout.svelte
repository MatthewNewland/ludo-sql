<script lang="ts">
  import "./app.css"
  import Navbar from "./Navbar.svelte"
  import Sidebar from "./Sidebar.svelte"
</script>

<svelte:head>
  <link
    href="https://fonts.googleapis.com/icon?family=Material+Icons"
    rel="stylesheet"
  />
</svelte:head>

<Navbar />
<Sidebar />
<main
  class="mr-auto ml-auto md:ml-[22rem] py-6"
>
  <slot />
</main>
