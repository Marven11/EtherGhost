<script setup>
import IconRun from "./icons/iconRun.vue"
import IconDirectory from "./icons/iconDirectory.vue"
import IconFile from "./icons/iconFile.vue"
import IconSymlinkFile from "./icons/iconSymlinkFile.vue"
import IconSymlinkDirectory from "./icons/iconSymlinkDirectory.vue"
import IconUnknownFile from "./icons/iconUnknownFile.vue"
import { ref, shallowRef } from "vue";
import { requestDataOrPopupError } from "@/assets/utils"
import Popups from "./Popups.vue"

const props = defineProps({
  session: String,
})
// "dir", "file", "link-dir", "link-file", "unknown"
const entryIcons = {
  "dir": IconDirectory,
  "file": IconFile,
  "link-dir": IconSymlinkDirectory,
  "link-file": IconSymlinkFile,
  "unknown": IconUnknownFile
}


// {
//     name: ".",
//     icon: IconDirectory,
//     perm: "rwxrwxrwx",
//     size: "4KB",
//   },
const entries = shallowRef([

])
const popupsRef = ref(null)
const userPwd = ref("") // pwd of user input

// pwd we maintain, might be different when user modify 
// the input and do not hit enter
let pwd = undefined

function readableFileSize(fileSize) {
  if (fileSize == -1) {
    return "? KB"
  }
  let units = ["B", "KiB", "MiB", "GiB", "TiB"]
  for (let unit of units) {
    if (fileSize <= 1024 || unit == "TiB") {
      return `${Math.round(fileSize)} ${unit}`
    }
    fileSize /= 1024
  }
}

function readableFilePerm(filePerm) {
  let result = ""
  for (let chr of filePerm) {
    let x = Number(chr)
    for (let [permIndex, permChr] of Array.from("rwx").entries()) {
      if (x & Math.pow(2, 2 - permIndex)) {
        result += permChr
      } else {
        result += "-"
      }
    }
  }
  return result
}

async function initFetch() {
  pwd = await requestDataOrPopupError(`/session/${props.session}/get_pwd`, popupsRef)
  userPwd.value = pwd
  let newEntries = await requestDataOrPopupError(`/session/${props.session}/list_dir`, popupsRef, {
    params: {
      current_dir: pwd
    }
  })
  entries.value = newEntries.map(entry => {
    return {
      name: entry.name,
      icon: entryIcons[entry.entry_type],
      perm: readableFilePerm(entry.permission),
      size: readableFileSize(entry.filesize),
    }
  })
}

setTimeout(initFetch, 0)
</script>

<template>
  <form action="" class="filepath-input" @submit="onExecuteCommand">
    <input v-model="userPwd" id="filepath-input" type="text" placeholder="/var/www/html">
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
      <div class="files-title">
        <input type="text" name="filename" id="files-title-filename" placeholder="passwd">
      </div>
      <div class="files-content">
        <!-- code mirror will live here -->
      </div>
      <div class="files-property">
        <p>文件编码: </p>
        <input type="text" name="encoding" id="files-property-encoding">
      </div>
    </div>
  </div>
  <Popups ref="popupsRef" />
</template>

<style scoped>
.filepath-input {
  display: flex;
  height: 60px;
}

input[type="text"] {
  font-size: 30px;
  text-indent: 10px;
  color: var(--font-color-white);
  border: none;
  outline: none;
  border-radius: 20px;
}

.filepath-input input {
  background-color: var(--background-color-2);
  margin-right: 20px;
  flex-grow: 1;
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
  margin-top: 20px;
}

.folder-panel {
  min-width: max-content;
  flex-grow: 1;
  margin-right: 30px;
  height: 100%;
  border-radius: 20px;
  background-color: var(--background-color-2);
  padding-top: 20px;
}

.folder-entry {
  display: flex;
  height: 80px;
  align-items: center;
  flex-direction: row;
  user-select: none;
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
  min-width: 350px;
  flex-grow: 3;
  display: flex;
  flex-direction: column;
}

.files-title {
  height: 70px;
  width: 100%;
}

.files-title input {
  border: none;
  outline: none;
  height: 100%;
  width: 100%;
  background-color: var(--background-color-2);
  font-size: 30px;
}

.files-content {
  flex-grow: 1;
  margin-top: 20px;
  border-radius: 20px;
  padding: 20px;
  background-color: var(--background-color-2);
}

.files-property {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: var(--background-color-2);
  margin-top: 20px;
  border-radius: 20px;
  padding-left: 20px;
  color: var(--font-color-white);

}

.files-property input {
  width: 100px;
  height: 40px;
  background-color: var(--background-color-3);
  font-size: 16px;
}

svg {
  width: 40px;
  stroke: var(--font-color-white);
}
</style>
