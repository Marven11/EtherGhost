<script setup>
import Header from "./components/Header.vue"
import { store, popupsRef, currentSettings } from "./assets/store"
import Popups from "@/components/Popups.vue"
import { getDataOrPopupError } from "./assets/utils";


setTimeout(async () => {
  let settings = await getDataOrPopupError("/settings")
  for(let key of Object.keys(settings)) {
    currentSettings[key] = settings[key]
  }
}, 0)

</script>

<template>
  <div id="root" :data-theme="store.theme">
    <!-- modified button from https://www.svgrepo.com/collection/dazzle-line-icons/ -->
    <Header />
    <main>
      <router-view></router-view>
      <!-- <WebshellEditorMain session="b9ffbeaa-2906-4865-ad7f-1818896dfe8c" /> -->
    </main>
  </div>
  <Popups ref="popupsRef" />
</template>

<style scoped>
#root {
  display: flex;
  align-items: center;
  flex-direction: column;
  height: 100vh;
}


main {
  height: 50vh;
  width: 90%;
  flex-grow: 1;
  margin-top: 50px;
}
</style>
