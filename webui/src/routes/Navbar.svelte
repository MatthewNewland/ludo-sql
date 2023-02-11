<script lang="ts">
  import { page } from "$app/stores"
  import { localSettings } from "$lib/store/settings"

  type LinkDef = {
    href: string
    title: string
    matcher?: (value: string) => boolean
  }

  const matches = (linkDef: LinkDef, value: string) => {
    if (linkDef.matcher) {
      return linkDef.matcher(value)
    }

    return linkDef.href === value
  }

  $: startMatches = startLinks.map((linkDef) =>
    matches(linkDef, $page.url.pathname)
  )

  const startLinks: LinkDef[] = [
    {
      href: "/",
      title: "Home",
    },
    {
      href: "/pages/new",
      title: "New",
    },
    {
      href: "/pages",
      title: "Pages",
      matcher(value: string) {
        return value.startsWith(this.href) && value !== "/pages/new"
      },
    },
    {
      href: "/settings",
      title: "Settings",
    },
    {
      href: "/login",
      title: "Login",
    },
  ]
</script>

<nav
  class="sticky top-0 z-10 bg-white p-6 border-b dark:bg-slate-900 dark:border-slate-800 flex flex-row items-center"
>
  <button
    class="text-4xl material-icons"
    on:click={() => ($localSettings.menuOpen = !$localSettings.menuOpen)}
  >
    menu
  </button>
  <ul
    class="flex flex-row justify-between md:max-w-[700px] lg:max-w-[900px] xl:max-w-[1200px] mx-auto w-full"
  >
    {#each startLinks as linkDef, i}
      <li>
        <a
          class="text-teal-600 font-semibold"
          class:underline={startMatches[i]}
          class:font-bold={startMatches[i]}
          href={linkDef.href}
        >
          {linkDef.title}
        </a>
      </li>
    {/each}
  </ul>
</nav>
