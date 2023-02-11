<script>
  import PageTree from "$lib/components/PageTree.svelte"
  import { pageTree } from "$lib/store/page"
  import { localSettings } from "$lib/store/settings"
</script>

<nav
  class="absolute top-13 left-0 w-0 md:w-80 border-r h-full dark:border-slate-800 {$localSettings.menuOpen
    ? 'visible'
    : 'invisible'}"
>
  <PageTree class="p-6 h-full" tree={$pageTree} />
</nav>
