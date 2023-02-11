<script lang="ts">
  import { text } from "svelte/internal"

  let dialogElement: HTMLDialogElement

  interface DialogAction {
    buttonText: string
    action: () => void
  }

  export function showModal() {
    dialogElement.showModal()
  }

  let resolveWith: (value: any) => void

  export function resolve(value: any) {
    dialogElement.close()
    resolveWith(value)
  }

  export function prompt() {
    showModal()
    return new Promise<any>((resolve) => {
      resolveWith = resolve
    })
  }

  let clazz = "w-1/2 h-1/3"

  export { clazz as class }

  export let message = "Heads up!"
  export let body = "Are you sure?"
</script>

<dialog
  bind:this={dialogElement}
  on:close
  class="relative dark:bg-slate-800 dark:text-slate-50 {clazz}"
>
  <button
    class="absolute top-2 right-2 material-icons"
    on:click={() => dialogElement.close()}
  >
    close
  </button>
  <header>
    <slot name="message">
      <h3 class="text-xl font-bold">{message}</h3>
    </slot>
  </header>
  <section>
    <slot>
      {body}
    </slot>
  </section>
  <footer class="absolute bottom-2">
    <slot name="actions">
      <button
        class="px-2 py-1 bg-slate-600"
        on:click={() => resolve(false)}
      >
        Cancel
      </button>
      <button
        class="px-2 py-1 bg-blue-600"
        on:click={() => resolve(true)}
      >
        OK
      </button>
    </slot>
  </footer>
</dialog>
