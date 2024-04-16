<script setup>
import Header from "./components/Header.vue"
import WebshellEditorMain from "./components/WebshellEditorMain.vue"
import HomeMain from "./components/HomeMain.vue"
import TerminalMain from "./components/TerminalMain.vue"
import FileBrowserMain from "./components/FileBrowserMain.vue"
import { ref } from "vue"
import { store } from "./assets/store"

</script>

<template>
  <div id="root">
    <!-- modified button from https://www.svgrepo.com/collection/dazzle-line-icons/ -->
    <Header />
    <main>
      <router-view></router-view>
      <!-- <WebshellEditorMain session="b9ffbeaa-2906-4865-ad7f-1818896dfe8c" /> -->
    </main>
  </div>
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
