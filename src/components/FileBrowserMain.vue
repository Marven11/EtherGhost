<script setup>
import IconRun from "./icons/iconRun.vue"
import IconDirectory from "./icons/iconDirectory.vue"
import IconFile from "./icons/iconFile.vue"
import IconSymlinkFile from "./icons/iconSymlinkFile.vue"
import IconSymlinkDirectory from "./icons/iconSymlinkDirectory.vue"
import IconUnknownFile from "./icons/iconUnknownFile.vue"
import { ref, shallowRef, watch } from "vue";
import ClickMenu from "./ClickMenu.vue"
import { Codemirror } from 'vue-codemirror'
import { getDataOrPopupError, postDataOrPopupError, addPopup } from "@/assets/utils"
import { store } from "@/assets/store"

// --- CodeMirror Stuff

import { javascript } from '@codemirror/lang-javascript'
import { php } from '@codemirror/lang-php'
import { python } from '@codemirror/lang-python'
import { html } from '@codemirror/lang-html'
import { css } from '@codemirror/lang-css'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView } from "@codemirror/view"
import { StreamLanguage } from "@codemirror/language"
import { shell } from "@codemirror/legacy-modes/mode/shell"

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

// ###########
// --- PWD ---
// ###########

// variable we maintain, pwd might be different when user modify 
// the input and do not hit enter
// we will add a watcher to this ref to automatically refresh it
const userPwd = ref("") // pwd of user input
let pwd = ref("")

async function initFetch() {
  pwd.value = await getDataOrPopupError(`/session/${props.session}/get_pwd`)
}

setTimeout(initFetch, 0)

async function onUserInputPwd(event) {
  event.preventDefault()
  pwd.value = userPwd.value
}

// ####################
// --- Folder entry ---
// ####################

// "dir", "file", "link-dir", "link-file", "unknown"
const entryIcons = {
  "dir": IconDirectory,
  "file": IconFile,
  "link-dir": IconSymlinkDirectory,
  "link-file": IconSymlinkFile,
  "unknown": IconUnknownFile
}

async function changeDir(entry) {
  let newPwd = await getDataOrPopupError("/utils/changedir", {
    params: {
      folder: pwd.value,
      entry: entry
    }
  })
  pwd.value = newPwd
}

async function viewFile(newFilename) {
  let { text: fileContent, encoding: encoding } = await getDataOrPopupError(`/session/${props.session}/get_file_contents`, {
    params: {
      current_dir: pwd.value,
      filename: newFilename
    }
  })
  filename.value = newFilename
  userFilename.value = newFilename
  codeMirrorContent.value = fileContent
  fileEncoding.value = encoding
}

async function onDoubleClickEntry(event) {
  const element = event.currentTarget
  const entry = entries.value[element.dataset.entryIndex]
  if (["dir", "link-dir"].includes(entry.entryType)) {
    changeDir(entry.name)
  } else if (["file", "link-file"].includes(entry.entryType)) {
    viewFile(entry.name)
  } else {
    addPopup("red", "未知文件类型", `文件${entry.name}类型未知，无法打开`)
  }
}

watch(pwd, async (newPwd, oldPwd) => {
  let newEntries = await getDataOrPopupError(`/session/${props.session}/list_dir`, {
    params: {
      current_dir: newPwd
    }
  })
  entries.value = newEntries.map(entry => {
    return {
      name: entry.name,
      entryType: entry.entry_type,
      icon: entryIcons[entry.entry_type],
      permission: entry.permission,
      filesize: entry.filesize,
    }
  })
  userPwd.value = pwd.value
})

// something like this:
// {
//       name: String,
//       entryType: one of ["dir", "file", "link-dir", "link-file", "unknown"],
//       icon: Icon compoment,
//       permission: sth like "755",
//       filesize: Number, size in bytes,
//     }
const entries = shallowRef([

])

// ###############################
// --- Folder entry click menu ---
// ###############################

const clickMenuTop = ref(0)
const clickMenuLeft = ref(0)
const showClickMenu = ref(false)
const menuItemsAll = [
  {
    "name": "open_file",
    "text": "打开文件",
    "icon": IconFile,
    "color": "white",
    "entry_type": ["file", "link-file"]
  },
  {
    "name": "open_dir",
    "text": "打开文件夹",
    "icon": IconDirectory,
    "color": "white",
    "entry_type": ["dir", "link-dir"]
  },
]


const menuItems = shallowRef([
])

let clickMenuEntry = undefined

function onRightClickEntry(event) {
  event.preventDefault()
  const element = event.currentTarget
  const entry = entries.value[element.dataset.entryIndex]
  clickMenuLeft.value = event.clientX;
  clickMenuTop.value = event.clientY;
  menuItems.value = menuItemsAll.filter(item => item.entry_type.includes(entry.entryType))
  clickMenuEntry = entry
  showClickMenu.value = true
}

function onClickMenuItem(item) {
  if (item.name == "open_file") {
    viewFile(clickMenuEntry.name)
    addPopup("blue", "提示", `可以双击打开文件`)
  } else if (item.name == "open_dir") {
    changeDir(clickMenuEntry.name)
  }
  else {
    addPopup("blue", "TODO", `还没实现${item.name}`)
  }
}


// ##################################
// --- File editor and CodeMirror ---
// ##################################

const userFilename = ref("")
let filename = ref("")
let fileEncoding = ref("")

const fileExtension = ref("")

const codeMirrorView = shallowRef()
const codeMirrorContent = ref("")
const codeMirrorTheme = EditorView.theme({
  "&": {
    "background-color": "var(--background-color-2)",
    "font-size": "24px",
  },
}, { dark: true })

const codeMirrorExtensions = shallowRef([codeMirrorTheme, oneDark])

function codeMirrorReady(payload) {
  codeMirrorView.value = payload.view
}

watch(fileExtension, (newFileExtension, _) => {
  let extensions = [codeMirrorTheme, oneDark];
  if (["js", "mjs"].includes(newFileExtension)) {
    extensions.push(javascript())
  }
  else if (["html", "htm"].includes(newFileExtension)) {
    extensions.push(html())
  }
  else if (["css"].includes(newFileExtension)) {
    extensions.push(css())
  }
  else if (["php", "php7", "php5", "phar"].includes(newFileExtension)) {
    extensions.push(php())
  }
  else if (["py"].includes(newFileExtension)) {
    extensions.push(python())
  }
  else if (["sh"].includes(newFileExtension)) {
    extensions.push(StreamLanguage.define(shell))
  }
  else {
    console.log("Extension not supported", newFileExtension)
  }
  codeMirrorExtensions.value = extensions
})
watch(filename, (newFilename, _) => {
  if (newFilename.indexOf(".") == "") {
    return ""
  }
  let dotPosition = newFilename.lastIndexOf(".") + 1
  fileExtension.value = newFilename.substring(dotPosition)
})

async function saveFile() {
  let success = await postDataOrPopupError(`/session/${props.session}/put_file_contents`, {
    text: codeMirrorContent.value,
    encoding: fileEncoding.value,
    filename: filename.value,
    current_dir: pwd.value
  })
  if(success) {
    addPopup("green", "保存成功", `文件${filename.value}已经成功保存`)
  }else{
    addPopup("red", "保存失败", `文件${filename.value}保存失败`)
  }
}

// #################
// --- Utilities ---
// #################

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


</script>

<template>
  <form action="" class="filepath-input" @submit="onUserInputPwd">
    <input v-model="userPwd" id="filepath-input" type="text" placeholder="/var/www/html">
    <div class="icon-run" @click="onUserInputPwd">
      <IconRun />
    </div>
  </form>
  <div class="file-panel">
    <div class="folder-panel">
      <div class="folder-entry" v-for="[entryIndex, entry] in entries.entries()" @dblclick="onDoubleClickEntry"
        @click.right="onRightClickEntry" :data-entry-index="entryIndex">
        <div class="folder-entry-icon">
          <component :is="entry.icon"></component>
        </div>
        <div class="folder-entry-info">
          <p class="folder-entry-name">
            {{ entry.name }}
          </p>
          <div class="folder-entry-meta">
            {{ readableFilePerm(entry.permission) }} {{ readableFileSize(entry.filesize) }}
          </div>
        </div>

      </div>
    </div>
    <div class="file-content-panel">
      <div class="files-title">
        <input type="text" name="filename" id="files-title-filename" placeholder="passwd" v-model="userFilename">
      </div>
      <div class="files-content">
        <codemirror v-model="codeMirrorContent" placeholder="Content goes here..." :autofocus="true"
          :indent-with-tab="true" :tab-size="4" :extensions="codeMirrorExtensions" @ready="codeMirrorReady" />
      </div>
      <div class="files-control">
        <div class="file-control-left">
          <p>文件编码: </p>
          <input type="text" name="encoding" id="files-control-encoding" v-model="fileEncoding">
        </div>
        <div class="file-control-right">
          <button @click="saveFile">保存</button>
        </div>
      </div>
    </div>
  </div>
  <transition>
    <div v-if="showClickMenu">
      <ClickMenu :top="clickMenuTop" :left="clickMenuLeft" :menuItems="menuItems" @remove="(_) => showClickMenu = false"
        @clickItem="onClickMenuItem" />
    </div>
  </transition>
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
  width: 30%;
  flex-grow: 1;
  margin-right: 30px;
  height: 100%;
  border-radius: 20px;
  background-color: var(--background-color-2);
  padding-top: 20px;
  overflow: scroll;
  flex-shrink: 0;
}

.folder-entry {
  display: flex;
  height: 80px;
  padding-right: 50px;
  align-items: center;
  flex-direction: row;
  user-select: none;
  font-variant-ligatures: none;
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
  width: 60%;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.files-title {
  height: 70px;
  width: 100%;
  flex-shrink: 0;
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
  padding-top: 20px;
  padding-bottom: 20px;
  background-color: var(--background-color-2);
  overflow: auto;
}

.files-control {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: var(--background-color-2);
  margin-top: 20px;
  border-radius: 20px;
  padding-left: 20px;
  padding-right: 20px;
  color: var(--font-color-white);
  flex-shrink: 0;
  justify-content: space-between;
}

.file-control-left,
.file-control-right {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.files-control input,
.files-control button {
  width: 100px;
  height: 40px;
  background-color: var(--background-color-3);
  font-size: 16px;
  color: var(--font-color-white);
}

.files-control button {
  border-radius: 20px;
  border: none;
}

.files-control button:hover {
  background-color: #ffffff15;
}

svg {
  width: 40px;
  stroke: var(--font-color-white);
}
</style>
