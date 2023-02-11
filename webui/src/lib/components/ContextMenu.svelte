<script lang="ts">
  import { createEventDispatcher } from "svelte"
  import type { Page } from "$lib/store/page"
  import Menu from "./Menu.svelte"

  let show = false
  let pos = { x: 0, y: 0 }

  export async function showMenu(e: MouseEvent) {
    if (show) {
      show = false
      await new Promise((res) => setTimeout(res, 100))
    }

    pos.x = e.clientX
    pos.y = e.clientY
    show = true
  }

  export function closeMenu() {
    show = false
  }

  const dispatch = createEventDispatcher()
</script>

{#if show}
  <Menu {...pos} on:click={closeMenu} on:clickoutside={closeMenu}>
    <slot>
      <ul>
        <li><button on:click={() => dispatch("cut")}>Cut</button></li>
        <li><button on:click={() => dispatch("paste")}>Paste</button></li>
      </ul>
    </slot>
  </Menu>
{/if}
