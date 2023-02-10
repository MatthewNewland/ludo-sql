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
  class="mr-auto ml-auto md:ml-[22rem] md:max-w-[700px] lg:max-w-[900px] xl:max-w-[1200px] 2xl:max-w-[1900px] py-6 h-full"
>
  <slot />
</main>
