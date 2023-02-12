<script lang="ts">
  import { pageStore } from "$lib/store/page"
  import { onMount } from "svelte"

  onMount(async () => {
    await pageStore.load()
  })
</script>

<h1 class="text-xl font-bold">All Pages:</h1>

<section class="grid gap-2">
  {#each $pageStore as page}
    <article class="p-4 rounded shadow border dark:border-slate-800">
      <header>
        <h3 class="text-lg font-semibold">
          <a href="/pages/{page.id}">
            {page.friendly_title}
          </a>
        </h3>
      </header>
      <section class="max-h-56 overflow-ellipsis">
        {@html page.content}
      </section>
    </article>
  {/each}
</section>
