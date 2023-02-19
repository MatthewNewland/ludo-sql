<script lang="ts">
  import type { Asset } from "$lib/store/assets"
  export let value: Asset
  const imageExtensions = new Set([".jpg", ".png", ".bmp"])
</script>

{#if imageExtensions.has(value.extension)}
  <img class="object-cover md:w-1/2 lg:w-2/3" src="http://localhost:8000/api/assets/view/{value.id}" alt={value.alt_text} />
{/if}
