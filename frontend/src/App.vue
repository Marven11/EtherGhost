<script setup>
import Header from "./components/Header.vue"
import { store, popupsRef, currentSettings } from "./assets/store"
import Popups from "@/components/Popups.vue"
import { getDataOrPopupError } from "./assets/utils";
import { ref } from "vue";


setTimeout(async () => {
  let settings = await getDataOrPopupError("/settings")
  for (let key of Object.keys(settings)) {
    currentSettings[key] = settings[key]
  }
  // evil hack to ensure color transition enabled after theme color being set
  setTimeout(() => store.theme_background_transition = true, 100)
}, 0)

</script>

<template>
  <div id="root" :data-theme="store.theme">
    <!-- modified button from https://www.svgrepo.com/collection/dazzle-line-icons/ -->
    <Header />
    <main>
      <router-view></router-view>
    </main>
  </div>
  <Popups ref="popupsRef" />
</template>

<style scoped>
#root {
  display: flex;
  align-items: center;
  flex-direction: column;
  height: 95vh;
}


main {
  height: 50vh;
  width: 90%;
  flex-grow: 1;
  margin-top: 30px;
  display: flex;
  flex-direction: column;
}
</style>
