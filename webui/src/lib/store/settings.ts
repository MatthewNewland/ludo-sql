import { writable } from "svelte/store"
import { browser } from "$app/environment"

export interface LocalSettings {
  darkMode: boolean
}

const initialSettings: LocalSettings = {
  darkMode: false,
}

export const localSettings = writable<LocalSettings>(structuredClone(initialSettings))

if (browser) {
  const storedSettingsRaw = localStorage.getItem("localSettings")
  if (storedSettingsRaw) {
    let storedSettings = JSON.parse(storedSettingsRaw) as LocalSettings
    localSettings.set(storedSettings)
  }

  const rootElement = document.querySelector(":root")
  localSettings.subscribe((value) => {
    rootElement?.classList.toggle("dark", value.darkMode)
    localStorage.setItem("localSettings", JSON.stringify(value))
  })
}
