<script setup>
import Header from './components/Header.vue'
import WebshellEditorMain from './components/WebshellEditorMain.vue'
import HomeMain from './components/HomeMain.vue'
import TerminalMain from './components/TerminalMain.vue'
import FileBrowserMain from './components/FileBrowserMain.vue'
</script>

<template>
  <div id="root">
    <!-- modified button from https://www.svgrepo.com/collection/dazzle-line-icons/ -->
    <Header />
    <main>
      <WebshellEditorMain session="42127cd3-6226-4472-abe6-4568d53fe50a" />
      <!-- <HomeMain/> -->
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
