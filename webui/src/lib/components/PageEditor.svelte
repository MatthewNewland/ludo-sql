<script lang="ts">
  import { createEventDispatcher } from "svelte"
  import type { Page } from "$lib/store/page"
  let page: Page = {
    title: "",
    friendly_title: "",
    content: ""
  }

  const dispatch = createEventDispatcher()

  export { page as value }

  const handleSave = async () => {
    dispatch("save")
  }
</script>

<form class="grid grid-cols-2 gap-2" on:submit|preventDefault>
  <label for="friendly_title">Friendly Title</label>
  <input type="text" bind:value={page.friendly_title} />
  <label for="title">Slug title:</label>
  <input type="text" bind:value={page.title} />
  <label for="content" class="col-span-2">Content:</label>
  <textarea cols="30" rows="10" class="col-span-2" bind:value={page.content} />
  <button type="submit" class="border col-span-2" on:click={handleSave}>
    Save
  </button>
</form>
