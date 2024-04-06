<script setup>
import Header from './components/Header.vue'
import WebshellEditorMain from './components/WebshellEditorMain.vue'
import HomeMain from './components/HomeMain.vue'
import TerminalMain from './components/TerminalMain.vue'
import FileBrowserMain from './components/FileBrowserMain.vue'
</script>

<template>
  <div id="root">
    <Header />
    <main>
      <WebshellEditorMain />
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
