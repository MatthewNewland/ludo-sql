<script lang="ts">
  export let href = ""
</script>

<li>
  {#if href}
    <a
      {href}
      class="hover:underline"
    >
      <slot />
    </a>
  {:else}
    <button
      class="hover:underline"
      on:click
    >
      <slot />
    </button>
  {/if}
</li>