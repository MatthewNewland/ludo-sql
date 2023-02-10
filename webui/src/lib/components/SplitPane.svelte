<script lang="ts">
  import { onMount } from "svelte"
  export let minWidth = 30
  export let splitterWidth = 10
  export let pos = 30
  let mousePos: number
  let delta = 0
  let isMouseDown = false
  let containerWidth: number
  let previousLeftPaneSize: number
  let leftPaneSize: number
  let rightPaneSize: number

  onMount(() => {
    let percentage = (pos / 100) * containerWidth - splitterWidth / 2
    leftPaneSize = percentage
    rightPaneSize = containerWidth - percentage - splitterWidth / 2
  })

  function handleMouseMove(e: MouseEvent) {
    if (isMouseDown) {
      delta = mousePos - e.clientX
      leftPaneSize =
        previousLeftPaneSize - delta <= minWidth
          ? minWidth
          : previousLeftPaneSize - delta >= containerWidth - splitterWidth - minWidth
          ? containerWidth - splitterWidth - minWidth
          : previousLeftPaneSize - delta

      rightPaneSize = containerWidth - leftPaneSize - splitterWidth
    }
  }

  function handleMouseDown(e: MouseEvent) {
    mousePos = e.clientX
    previousLeftPaneSize = leftPaneSize
    isMouseDown = true
  }

  function handleMouseUp() {
    isMouseDown = false
  }

  $: if (
    leftPaneSize &&
    rightPaneSize & containerWidth &&
    leftPaneSize + rightPaneSize !== containerWidth - splitterWidth
  ) {
    const leftRatio = leftPaneSize / (leftPaneSize + rightPaneSize - splitterWidth / 2)
    leftPaneSize = containerWidth * leftRatio - splitterWidth / 2
    rightPaneSize = containerWidth - leftPaneSize - splitterWidth / 2
  }
</script>

<svelte:window on:mousemove={handleMouseMove} on:mouseup={handleMouseUp} />

<section
  bind:clientWidth={containerWidth}
  class={isMouseDown ? "disable-select" : ""}
>
  <div style="width:{leftPaneSize}px" id="left">
    <slot name="left" />
    {#if isMouseDown}
      <div class="window-hook" />
    {/if}
  </div>
  <div
    on:mousedown={handleMouseDown}
    id="splitter"
    style="width:{splitterWidth}px"
  />
  <div style="width:{rightPaneSize}px" id="right">
    <slot name="right" />
    {#if isMouseDown}
      <div class="window-hook" />
    {/if}
  </div>
</section>

<style lang="postcss">
  section {
    width: 100%;
    display: flex;
    /* border: 1px solid black; */
  }

  #left {
    height: 100%;
  }

  #right {
    height: 100%;
  }

  #splitter {
    height: 100%;
    /* @apply bg-gray-500; */
    @apply bg-black;
    cursor: col-resize;
  }

  div.window-hook {
    height: 100%;
    width: 100%;
    z-index: 5000;
    position: absolute;
    top: 0;
    left: 0;
  }

  .disable-select,
  .disable-select * {
    user-select: none; /* supported by Chrome and Opera */
    -webkit-user-select: none; /* Safari */
    -khtml-user-select: none; /* Konqueror HTML */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* Internet Explorer/Edge */
    cursor: col-resize;
  }
</style>
