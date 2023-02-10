<script lang="ts">
  import { page } from "$app/stores"
  import type { PageData } from "./$types"
  export let data: PageData
</script>

<section>
  <h1 class="text-2xl font-bold">
    {data.page.friendly_title ?? data.page.title}
  </h1>
  <div class="whitespace-pre-line">
    {@html data.page.content}
  </div>
</section>
