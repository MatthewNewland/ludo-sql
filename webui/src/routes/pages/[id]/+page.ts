import { browser } from "$app/environment"
import type { PageLoad } from "./$types"
import { apiClient, type Page } from "$lib/store/page"

export const load = (async ({ params }) => {
  let data: Page = {
    title: "",
    friendly_title: "",
    content: ""
  }

  let previousVersions: Page[] = []

  if (browser) {
    data = await apiClient.get(`${params.id}`).json<Page>()
    previousVersions = await apiClient.get(`${params.id}/versions`).json<Page[]>()
  }

  return {
    page: data,
    previousVersions
  }
}) satisfies PageLoad