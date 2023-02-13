<script lang="ts">
  import { page } from "$app/stores"
  import { pageStore, type PageWithChildren } from "$lib/store/page"
  import { clipboard } from "$lib/store/clipboard"
  import Dialog from "./Dialog.svelte"
  import ContextMenu from "./ContextMenu.svelte"

  let clazz: string = ""
  export { clazz as class }
  export let tree: PageWithChildren[]
  export let depth = 0
  let expanded: boolean[] = tree.map(() => false)
  let dialog: Dialog

  const handleDelete = async (pwc: PageWithChildren) => {
    const result = await dialog.prompt()
    if (result) {
      await pageStore.deletePage(pwc)
    }
  }

  let menuPage: PageWithChildren
  let contextMenu: ContextMenu

  const handleTreeNodeContextMenu = (e: MouseEvent, pwc: PageWithChildren) => {
    menuPage = pwc
    contextMenu.showMenu(e)
  }

  const handleContextMenuCut = () => {
    $clipboard.cutPage = menuPage
    contextMenu.closeMenu()
  }

  const handleContextMenuPaste = () => {
    contextMenu.closeMenu()
    if (!$clipboard.cutPage) {
      return
    }

    pageStore.movePageToNewParent($clipboard.cutPage, menuPage)
  }
</script>

<ul class:ml-5={depth > 0} class="flex flex-col gap-1 w-full pr-4 {clazz}">
  {#each tree as pwc, i}
    <li
      class="flex flex-row justify-between group rounded {Number.parseInt(
        $page.params.id
      ) === pwc.id
        ? 'font-bold bg-gray-300 dark:bg-slate-700'
        : ''}"
      on:contextmenu|preventDefault={(e) => handleTreeNodeContextMenu(e, pwc)}
    >
      <div class="flex flex-row gap-2 items-center">
        {#if !!pwc.children.length}
          <button
            class="material-icons"
            on:click={() => (expanded[i] = !expanded[i])}
          >
            {expanded[i] ? "expand_less" : "expand_more"}
          </button>
        {:else}
          <span class="material-icons">article</span>
        {/if}
        <a
          href="/pages/{pwc.id}"
          class:font-bold={!!pwc.children.length && !expanded[i]}
        >
          {pwc.friendly_title ?? pwc.title}
        </a>
      </div>
      <div
        class="flex flex-row gap-2 items-center invisible group-hover:visible"
      >
        <a class="material-icons" href="/pages/new?parentId={pwc.id}">add</a>
        <a class="material-icons" href="/pages/{pwc.id}/edit">edit</a>
        <button class="material-icons" on:click={() => handleDelete(pwc)}
          >delete</button
        >
      </div>
    </li>
    <li>
      {#if !!pwc.children.length && expanded[i]}
        <svelte:self tree={pwc.children} depth={depth + 1} />
      {/if}
    </li>
  {/each}
</ul>

<Dialog bind:this={dialog} class="w-1/3 h-1/4">
  <p>Are you sure you want to delete this page?</p>
</Dialog>

<ContextMenu
  bind:this={contextMenu}
  on:cut={handleContextMenuCut}
  on:paste={handleContextMenuPaste}
>
  <ul>
    <li><button on:click={handleContextMenuCut}>Cut</button></li>
    <li><button on:click={handleContextMenuPaste}>Paste</button></li>
  </ul>
</ContextMenu>
