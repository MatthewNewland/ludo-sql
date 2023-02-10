<script lang="ts">
  import { pageStore, type Page } from "$lib/store/page"
  import { page } from "$app/stores"
  import PageEditor from "$lib/components/PageEditor.svelte"

  const initialPage: Page = {
    title: "",
    friendly_title: "",
    content: "",
  }

  let newPage: Page = structuredClone(initialPage)

  const handleSave = async () => {
    let parentId: number | undefined = parseInt(
      $page.url.searchParams.get("parentId") ?? ""
    )
    if (!parentId) {
      parentId = undefined
    }
    await pageStore.savePage(newPage, parentId)
    newPage = structuredClone(initialPage)
  }
</script>

<PageEditor bind:value={newPage} on:save={handleSave} />
