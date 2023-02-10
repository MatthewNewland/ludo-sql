import { browser } from "$app/environment"
import type { PageLoad } from "./$types"
import { apiClient, type Page } from "$lib/store/page"

export const load = (async ({ params }) => {
  let data: Page = {
    title: "",
    friendly_title: "",
    content: ""
  }

  if (browser) {
    data = await apiClient.get(`${params.id}`).json<Page>()
  }

  return {
    page: data
  }
}) satisfies PageLoad