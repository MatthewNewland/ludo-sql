import { derived, writable } from "svelte/store"
import ky from "ky"
import { browser } from "$app/environment"

export const authClient = ky.create({
  prefixUrl: "http://localhost:8000/auth",
  credentials: "include",
})

export interface User {
  id?: number
  username: string
  email: string
  password?: string
}

const createUserStore = () => {
  const userStore = writable<User>()

  return {
    ...userStore,

    async logIn(login: User) {
      const userResult = await authClient
        .post("login", { json: login })
        .json<User>()
      userStore.set(userResult)
    },
  }
}

export const user = createUserStore()

if (browser) {
  authClient
    .get("user")
    .then((res) => res.json<User>())
    .then((data) => user.set(data))
}

export const loggedIn = derived(user, ($user) => !!$user)
