import { writable } from "svelte/store"
import type { Page } from "./page"

export interface Clipboard {
  cutPage?: Page
}

export const clipboard = writable<Clipboard>({})
