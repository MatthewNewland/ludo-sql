<script lang="ts">
  import { onMount, setContext, createEventDispatcher } from "svelte"
  import { fade } from "svelte/transition"
  import { menuKey } from "./menu"

  export let x: number
  export let y: number

  $: (() => {
    if (!menuEl) return
    const rect = menuEl.getBoundingClientRect()
    x = Math.min(window.innerWidth - rect.width, x)
    if (y > window.innerHeight) {
      y -= rect.height
    }
  })(),
    x,
    y

  let menuEl: HTMLDivElement
  const dispatch = createEventDispatcher()

  setContext(menuKey, {
    dispatchClick: () => dispatch("click"),
  })

  function onPageClick(e: MouseEvent) {
    if (e.target === menuEl || menuEl.contains(e.target as Node)) {
      return
    }
    dispatch("clickoutside")
  }
</script>

<svelte:window on:click={onPageClick} />

<div
  transition:fade={{ duration: 100 }}
  bind:this={menuEl}
  style="top: {y}px; left: {x}px;"
  class="fixed grid dark:bg-slate-800 w-40 px-4 py-2"
>
  <slot />
</div>
