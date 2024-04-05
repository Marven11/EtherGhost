<script setup>
import IconRun from "./icons/iconRun.vue"
import IconDirectory from "./icons/iconDirectory.vue"
import IconFile from "./icons/iconFile.vue"
import IconSymlinkFile from "./icons/iconSymlinkFile.vue"
import IconSymlinkDirectory from "./icons/iconSymlinkDirectory.vue"
import IconUnknownFile from "./icons/iconUnknownFile.vue"
import { ref, shallowRef } from "vue";

const terminalOutput = ref("");

const entries = shallowRef([
  {
    name: ".",
    icon: IconDirectory,
    perm: "rwxrwxrwx",
    size: "4KB",
  },
  {
    name: "passwd",
    icon: IconFile,
    perm: "rw-r--r--",
    size: "4KB",
  },
])

</script>

<template>
  <form action="" class="filepath-input" @submit="onExecuteCommand">
    <input id="filepath-input" type="text" placeholder="/var/www/html">
    <div class="icon-run" @click="onExecuteCommand">
      <IconRun />
    </div>
  </form>
  <div class="file-panel">
    <div class="folder-panel">
      <div class="folder-entry" v-for="entry in entries">
        <div class="folder-entry-icon">
          <component :is="entry.icon"></component>
        </div>
        <div class="folder-entry-info">
          <p class="folder-entry-name">
            {{ entry.name }}
          </p>
          <div class="folder-entry-meta">
            {{ entry.perm }} {{ entry.size }}
          </div>
        </div>

      </div>
    </div>
    <div class="file-content-panel">

    </div>
  </div>
</template>

<style scoped>
.filepath-input {
  display: flex;
  height: 60px;
}

.filepath-input input {
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  border: none;
  border-radius: 20px;
  margin-right: 20px;
  outline: none;
  flex-grow: 1;
  font-size: 30px;
  text-indent: 10px;
}

.icon-run {
  height: 60px;
  width: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color-2);
  border-radius: 20px;
  transition: all 0.3s ease;
  opacity: 1;
}

.icon-run:hover {
  background-color: var(--background-color-3);
  outline: 2px solid var(--font-color-grey);
}

.file-panel {
  display: flex;
  height: 85%;
  flex-grow: 1;
  justify-content: space-between;
}

.folder-panel {
  margin-top: 20px;
  width: 49%;
  height: 100%;
  flex-grow: 1;
  border-radius: 20px;
  background-color: var(--background-color-2);
  padding-top: 20px;
}

.folder-entry {
  display: flex;
  height: 80px;
  align-items: center;
  flex-direction: row;
}

.folder-entry:hover {
  background-color: #00000015;
}

.folder-entry-icon {
  margin: 0px 20px;
}

.folder-entry-info {
  display: flex;
  flex-direction: column;
}

.folder-entry-name {
  color: var(--font-color-white);
  font-size: 30px;
  margin: 0;
}

.folder-entry-meta {
  color: var(--font-color-grey);

}


.file-content-panel {
  width: 49%;
  flex-grow: 1;

}

svg {
  width: 40px;
  stroke: var(--font-color-white);
}
</style>
