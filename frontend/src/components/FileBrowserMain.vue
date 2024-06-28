<script setup>
import IconRun from "./icons/iconRun.vue"
import IconDirectory from "./icons/iconDirectory.vue"
import IconFile from "./icons/iconFile.vue"
import IconFileDownload from "./icons/iconFileDownload.vue"
import IconFileNew from "./icons/iconFileNew.vue"
import IconFileUpload from "./icons/iconFileUpload.vue"
import IconFileUnknown from "./icons/iconFileUnknown.vue"
import IconPenSquare from "./icons/iconPenSquare.vue"
import IconLoad from "./icons/iconLoad.vue"
import IconSymlinkFile from "./icons/iconSymlinkFile.vue"
import IconSymlinkDirectory from "./icons/iconSymlinkDirectory.vue"
import IconDelete from "./icons/iconDelete.vue"

import { ref, shallowRef, watch } from "vue";
import ClickMenu from "./ClickMenu.vue"
import HoverForm from "./HoverForm.vue"
import HoverStatus from "./HoverBox.vue"
import InputBox from "./InputBox.vue"
import { Codemirror } from 'vue-codemirror'
import { getDataOrPopupError, postDataOrPopupError, addPopup, joinPath } from "@/assets/utils"
import { store } from "@/assets/store"

// --- CodeMirror Stuff
import { EditorView } from "@codemirror/view"
import { oneDark } from '@codemirror/theme-one-dark'

import { css } from '@codemirror/lang-css'
import { cpp } from '@codemirror/lang-cpp'
import { html } from '@codemirror/lang-html'
import { java } from '@codemirror/lang-java'
import { javascript } from '@codemirror/lang-javascript'
import { markdown } from '@codemirror/lang-markdown'
import { php } from '@codemirror/lang-php'
import { python } from '@codemirror/lang-python'
import { yaml } from '@codemirror/lang-yaml'


import { shell } from "@codemirror/legacy-modes/mode/shell"
import { StreamLanguage } from "@codemirror/language"

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

function onUserInputPwd(event) {
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
  "unknown": IconFileUnknown
}

async function changeDir(entry) {
  let newPwd = await getDataOrPopupError("/utils/join_path", {
    params: {
      folder: pwd.value,
      entry: entry
    }
  })
  pwd.value = newPwd
}

async function listDir(newPwd) {
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


async function viewNewFile(newFilename) {
  filename.value = newFilename
  userFilename.value = newFilename
  codeMirrorContent.value = ""
  fileEncoding.value = "utf-8"
}

async function downloadFile(folder, filename) {
  let filepath = await getDataOrPopupError("/utils/join_path", {
    params: {
      folder: folder,
      entry: filename
    }
  })
  let content = await getDataOrPopupError(`/session/${props.session}/download_file`, {
    params: {
      filepath: filepath
    }
  })
  let url = window.URL.createObjectURL(new Blob([atob(content)], { type: 'application/octet-stream' }));
  let fileLink = document.createElement('a');
  fileLink.href = url;
  fileLink.download = filename;
  fileLink.click();
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
  listDir(newPwd)
  userPwd.value = newPwd
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

// ##############################
// --- Upload File Hover Form ---
// ##############################

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

const showUploadFileHoverForm = ref(false)

async function checkUploadStatus(stopSignal) {
  while (!stopSignal.signal) {
    await sleep(300)
    let result = await getDataOrPopupError(`/session/${props.session}/file_upload_status`)
    uploadingFiles.value = result
    console.log(result)
    if (result.length == 0) {
      return;
    }
  }
}

async function submitUploadFile(form) {
  if (form == undefined) {
    return;
  }
  let stopSignal = { signal: false }
  let uploadFileCoro = postDataOrPopupError(`/session/${props.session}/upload_file`, form, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  let checkUploadsCoro = checkUploadStatus(stopSignal)
  let resp
  try {
    [resp, _] = await Promise.all([uploadFileCoro, checkUploadsCoro])
  } catch (e) {
    stopSignal.signal = true;
  }
  if (!resp) {
    addPopup("red", "上传失败", "因未知原因上传失败")
  }
  await listDir(pwd.value)
}

// ###############################
// --- Folder entry click menu ---
// ###############################

const clickMenuY = ref(0)
const clickMenuX = ref(0)
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
    "name": "new_file",
    "text": "新建文件",
    "icon": IconFileNew,
    "color": "white",
    "entry_type": ["empty", "file", "link-file"]
  },
  {
    "name": "upload_file",
    "text": "上传文件",
    "icon": IconFileUpload,
    "color": "white",
    "entry_type": ["empty", "file", "link-file", "dir", "link-dir"]
  },
  {
    "name": "download_file",
    "text": "下载文件",
    "icon": IconFileDownload,
    "color": "white",
    "entry_type": ["file", "link-file"]
  },
  {
    "name": "rename_file",
    "text": "重命名",
    "icon": IconPenSquare,
    "color": "white",
    "entry_type": ["file", "link-file", "dir", "link-dir"]
  },
  {
    "name": "delete_file",
    "text": "删除文件",
    "icon": IconDelete,
    "color": "red",
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

function confirmNewFile() {
  showInputBox.value = true
  inputBoxTitle.value = "新建文件"
  inputBoxNote.value = "输入文件的文件名"
  inputBoxRequireInput.value = true
  inputBoxCallback = async filename => {
    if (!filename) {
      showInputBox.value = false

    }
    let success = await postDataOrPopupError(`/session/${props.session}/put_file_contents`, {
      text: "",
      encoding: "utf-8",
      filename: filename,
      current_dir: pwd.value
    })
    if (success) {
      addPopup("green", "新建文件成功", `文件${filename}已经成功新建`)
    } else {
      addPopup("red", "新建失败", `文件${filename}新建失败`)
    }
    await listDir(pwd.value)

    viewNewFile(filename)
    showInputBox.value = false
  }
}

function confirmUploadFile() {
  showUploadFileHoverForm.value = true
}

function confirmRenameFile(filename) {
  showInputBox.value = true
  inputBoxTitle.value = "重命名文件"
  inputBoxNote.value = `输入新的文件名${filename}`
  inputBoxRequireInput.value = true
  inputBoxCallback = async new_filename => {
    if (new_filename) {
      let result = await getDataOrPopupError(`/session/${props.session}/move_file`, {
        params: {
          filepath: (await joinPath(pwd.value, filename)),
          new_filepath: (await joinPath(pwd.value, new_filename))
        }
      })
      if (result) {
        addPopup("green", "重命名成功", `文件${filename}已经重命名`)
      } else {
        addPopup("red", "重命名失败", `文件${filename}重命名失败`)
      }
      listDir(pwd.value)
    }
    showInputBox.value = false
  }
}


function confirmDeleteFile(filename) {
  showInputBox.value = true
  inputBoxTitle.value = "删除文件"
  inputBoxNote.value = `真的要删除文件${filename}吗`
  inputBoxRequireInput.value = false
  inputBoxCallback = async result => {
    if (result) {
      let result = await getDataOrPopupError(`/session/${props.session}/delete_file`, {
        params: {
          current_dir: pwd.value,
          filename: filename
        }
      })
      if (result) {
        addPopup("green", "删除成功", `文件${filename}已经删除`)
      } else {
        addPopup("red", "删除失败", `文件${filename}删除失败`)
      }
      listDir(pwd.value)
    }
    showInputBox.value = false
  }
}

function onClickMenuItem(item) {
  if (item.name == "open_file") {
    viewFile(clickMenuEntry.name)
    addPopup("blue", "提示", `可以双击打开文件`)
  } else if (item.name == "open_dir") {
    changeDir(clickMenuEntry.name)
  } else if (item.name == "new_file") {
    confirmNewFile()
  } else if (item.name == "upload_file") {
    confirmUploadFile()
  } else if (item.name == "download_file") {
    downloadFile(pwd.value, clickMenuEntry.name)
  } else if (item.name == "rename_file") {
    confirmRenameFile(clickMenuEntry.name)
  } else if (item.name == "delete_file") {
    confirmDeleteFile(clickMenuEntry.name)
  }
  else {
    addPopup("blue", "TODO", `还没实现${item.name}`)
  }
}

function onRightClickEntry(event) {
  event.preventDefault()
  const element = event.currentTarget
  const entry = entries.value[element.dataset.entryIndex]
  clickMenuX.value = event.clientX;
  clickMenuY.value = event.clientY;
  menuItems.value = menuItemsAll.filter(item => item.entry_type.includes(entry.entryType))
  clickMenuEntry = entry
  showClickMenu.value = true
}

function onRightClickEmpty(event) {
  event.preventDefault()
  clickMenuX.value = event.clientX;
  clickMenuY.value = event.clientY;
  menuItems.value = menuItemsAll.filter(item => item.entry_type.includes("empty"))
  clickMenuEntry = undefined
  showClickMenu.value = true
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
  let highlightings = [
    { suffix: ["cpp"], extension: () => cpp() },
    { suffix: ["css"], extension: () => css() },
    { suffix: ["html", "htm"], extension: () => html() },
    { suffix: ["java"], extension: () => java() },
    { suffix: ["js", "mjs"], extension: () => javascript() },
    { suffix: ["md"], extension: () => markdown() },
    { suffix: ["sh"], extension: () => StreamLanguage.define(shell) },
    { suffix: ["php", "php7", "php5", "phar"], extension: () => php() },
    { suffix: ["py"], extension: () => python() },
    { suffix: ["yaml"], extension: () => yaml() },
  ]
  let selectedHighlights = highlightings.filter(item => item.suffix.includes(newFileExtension))
  if (selectedHighlights.length) {
    extensions.push(selectedHighlights[0].extension())
  } else {
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
  filename.value = userFilename.value
  let success = await postDataOrPopupError(`/session/${props.session}/put_file_contents`, {
    text: codeMirrorContent.value,
    encoding: fileEncoding.value,
    filename: filename.value,
    current_dir: pwd.value
  })
  if (success) {
    addPopup("green", "保存成功", `文件${filename.value}已经成功保存`)
  } else {
    addPopup("red", "保存失败", `文件${filename.value}保存失败`)
  }
  await listDir(pwd.value)

}

// input box 

const showInputBox = ref(false)
const inputBoxTitle = ref("")
const inputBoxNote = ref("")
const inputBoxRequireInput = ref(false)
let inputBoxCallback = ref(undefined)

// uploadProgress

const uploadingFiles = ref([])

console.log(uploadingFiles.value)

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
    <div class="filepath-icon" @click="onUserInputPwd">
      <IconRun />
    </div>
    <div class="filepath-icon" @click="() => {
    listDir(pwd);
    userPwd = pwd;
  }">
      <IconLoad />
    </div>
  </form>
  <div class="file-panel">
    <div class="folder-panel scrollbar" @click.right.stop="onRightClickEmpty">
      <div class="folder-entry" v-for="[entryIndex, entry] in entries.entries()" @dblclick="onDoubleClickEntry"
        @click.right.stop="onRightClickEntry" :data-entry-index="entryIndex">
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
      <div class="files-content scrollbar">
        <codemirror v-model="codeMirrorContent" placeholder="Content goes here..." :autofocus="true"
          :indent-with-tab="true" :tab-size="4" :extensions="codeMirrorExtensions" @ready="codeMirrorReady" />
      </div>
      <div class="files-control">
        <div class="file-control-left">
          <p>文件编码: </p>
          <input type="text" name="encoding" id="files-control-encoding" v-model="fileEncoding">
        </div>
        <div class="file-control-right">
          <button class="button" @click="saveFile">保存</button>
        </div>
      </div>
    </div>
  </div>
  <transition>
    <div v-if="showClickMenu">
      <ClickMenu :mouse_x="clickMenuX" :mouse_y="clickMenuY" :menuItems="menuItems" @remove="(_) => showClickMenu = false"
        @clickItem="onClickMenuItem" />
    </div>
  </transition>

  <transition>
    <InputBox v-if="showInputBox" :title="inputBoxTitle" :note="inputBoxNote" :requireInput="inputBoxRequireInput"
      @result="inputBoxCallback" />
  </transition>

  <transition>
    <HoverForm title="上传文件" :callback="(result) => { submitUploadFile(result); showUploadFileHoverForm = false }"
      v-if="showUploadFileHoverForm">
      <input type="hidden" name="folder" :value="pwd">
      <div class="input-box-line">
        <div class="input-file">
          <input type="file" name="file" id="file">
        </div>
      </div>
    </HoverForm>
  </transition>

  <transition>
    <HoverStatus v-if="uploadingFiles.length != 0">
      <div class="upload-progress">
        <h1>上传进度</h1>
        <div class="upload-progress-file" v-for="file in uploadingFiles">
          <div class="upload-progress-percentage">
            <p>
              {{ Math.floor(file.percentage * 100) }}%
            </p>
          </div>

          <p class="upload-progress-filename">
            {{ file.file }}
          </p>
        </div>
      </div>
    </HoverStatus>
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
  flex-grow: 1;
}

.filepath-icon {
  height: 60px;
  width: 60px;
  margin-left: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color-2);
  border-radius: 20px;
  transition: all 0.3s ease;
  opacity: 1;
}

.filepath-icon:hover {
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
  overflow: overlay;
  flex-shrink: 0;
  transition: background 1s ease;
}

.folder-entry {
  display: flex;
  height: 80px;
  padding-right: 50px;
  align-items: center;
  flex-direction: row;
  user-select: none;
  font-variant-ligatures: none;
  transition: background 0.3s ease;
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

.files-control input {
  height: 40px;
  width: 100px;
  background-color: var(--background-color-3);
  font-size: 16px;
  color: var(--font-color-white);
}

.upload-progress {
  padding: 20px;
  color: var(--font-color-white);
}

.upload-progress p {
  margin: 0;
}

.upload-progress-file {
  background-color: #00000015;
  height: 100px;
  border-radius: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 20px;
}

.upload-progress-filename {
  font-size: 24px;
}

.upload-progress-percentage {
  margin-right: 20px;
  font-size: 36px;
  width: 130px;
  background-color: #00000015;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70px;
  border-radius: 20px;
}

svg {
  width: 40px;
  stroke: var(--font-color-white);
}
</style>
