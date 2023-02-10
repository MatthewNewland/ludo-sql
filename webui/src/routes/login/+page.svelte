<script lang="ts">
  import { goto } from "$app/navigation"
  import { user, type User } from "$lib/store/auth"
  import { pageStore } from "$lib/store/page"

  let userLogin: User = {
    username: "",
    email: "",
    password: ""
  }

  const handleLogin = async () => {
    await user.logIn(userLogin)
    await pageStore.load()
    goto("/")
  }
</script>

<form class="grid grid-cols-2 gap-2" on:submit={handleLogin}>
  <label for="username">Username:</label>
  <input type="text" bind:value={userLogin.username} />
  <label for="password">Password:</label>
  <input type="password" bind:value={userLogin.password} />
  <button type="submit" class="col-span-2 border">Login</button>
</form>
