<script setup>
import Header from "./components/Header.vue"
import HoverForm from "./components/HoverForm.vue"
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
  setTimeout(() => store.header_background_transition = true, 100)
}, 0)

const showHoverForm = ref(true)

</script>

<template>
  <div id="root" :data-theme="store.theme">
    <!-- modified button from https://www.svgrepo.com/collection/dazzle-line-icons/ -->
    <Header />
    <main>
      <!-- <router-view></router-view> -->
      <HoverForm :callback="(result) => { console.log(result); showHoverForm = false }" v-if="showHoverForm">
        <div class="input-box-line">
          <input type="text" name="text" id="text">
        </div>
        <div class="input-box-line">
          <p>上传文件</p>
          <div class="input-file">
            <input type="file" name="file" id="file">
          </div>
        </div>
      </HoverForm>
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
