<script lang="ts">
  import { localSettings } from "$lib/store/settings"
</script>

<label for="dark-mode" class="flex flex-row gap-2 items-center">
  Dark Mode:
  <input type="checkbox" bind:checked={$localSettings.darkMode} />
</label>
