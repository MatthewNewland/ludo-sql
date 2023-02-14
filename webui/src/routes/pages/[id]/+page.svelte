<script lang="ts">
  import { onMount } from "svelte"
  import type { Page } from "$lib/store/page";
  import type { PageData } from "./$types"
  export let data: PageData

  let page: Page = data.page

  // onMount(() => {
  //   page = data.page
  // })
  const count = data.previousVersions.length
</script>

<section>
  <header class="flex flex-row justify-between mr-40">
    <h1 class="text-2xl font-bold">
      {page.friendly_title ?? page.title}
    </h1>
    {#if data.previousVersions.length}
      <div class="flex flex-row gap-2 items-center">
        <label for="selectedVersion">Selected Version:</label>
        <select bind:value={page}>
          <option value={data.page}>
            Current Version - "{page.friendly_title}"
          </option>
          {#each data.previousVersions as version, i}
            <option value={version}>
              Version {count - i}: {version.friendly_title}
            </option>
          {/each}
        </select>
      </div>
    {/if}
  </header>
  <div class="whitespace-pre-line">
    {@html page.content}
  </div>
</section>
