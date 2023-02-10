<script lang="ts">
  import PageEditor from "$lib/components/PageEditor.svelte"
  import { pageStore } from "$lib/store/page"
  import type { PageData } from "../$types"

  export let data: PageData
</script>

<PageEditor
  value={data.page}
  on:save={async () => {
    await pageStore.savePage(data.page)
    history.back()
  }}
/>
