import { writable } from "svelte/store"
import ky from "ky"
import type { Options as KyOptions } from "ky"
import { browser } from "$app/environment"

export const apiClient = ky.create({
  prefixUrl: "http://localhost:8000/api/pages",
  credentials: "include",
})

export interface Page {
  id?: number
  title: string
  friendly_title: string
  content: string
}

export type PageWithChildren = Page & {
  children: PageWithChildren[]
}

const createPageStore = () => {
  const pageStore = writable<Page[]>([])

  return {
    ...pageStore,
    async load() {
      const pageResult = await apiClient.get("").json<Page[]>()
      pageStore.set(pageResult)
    },

    async savePage(page: Page, parentId?: number) {
      const method = page.id ? "patch" : "post"
      const url = method === "post" ? "" : `${page.id!}`
      let options: KyOptions = { method, json: page }
      if (parentId) {
        options.searchParams = { parent_id: parentId }
      }
      await apiClient(url, options)
      await this.load()
    },

    async deletePage(page: Page) {
      await apiClient.delete(`${page.id!}`)
      await this.load()
    },

    async movePageToNewParent(page: Page, newParent: Page) {
      const searchParams = {
        parent_id: newParent.id!
      }

      await apiClient.put(`move/${page.id}`, { searchParams })
      await this.load()
    }
  }
}

export const pageStore = createPageStore()

const createPageTree = () => {
  const pageTree = writable<PageWithChildren[]>([])

  return {
    ...pageTree,
    async load() {
      const result = await apiClient.get("tree").json<PageWithChildren[]>()
      pageTree.set(result)
    },
  }
}

export const pageTree = createPageTree()

if (browser) {
  pageStore.subscribe(async () => {
    await pageTree.load()
  })
}
