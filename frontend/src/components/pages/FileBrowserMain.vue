<script setup>
import IconRun from "@/components/icons/iconRun.vue"
import IconDirectory from "@/components/icons/iconDirectory.vue"
import IconFile from "@/components/icons/iconFile.vue"
import IconFileDownload from "@/components/icons/iconFileDownload.vue"
import IconFileNew from "@/components/icons/iconFileNew.vue"
import IconFileUpload from "@/components/icons/iconFileUpload.vue"
import IconFileUnknown from "@/components/icons/iconFileUnknown.vue"
import IconPenSquare from "@/components/icons/iconPenSquare.vue"
import IconLoad from "@/components/icons/iconLoad.vue"
import IconSymlinkFile from "@/components/icons/iconSymlinkFile.vue"
import IconSymlinkDirectory from "@/components/icons/iconSymlinkDirectory.vue"
import IconDelete from "@/components/icons/iconDelete.vue"

import { ref, shallowRef, watch } from "vue";
import ClickMenu from "@/components/ClickMenu.vue"
import HoverForm from "@/components/HoverForm.vue"
import HoverStatus from "@/components/HoverBox.vue"
import InputBox from "@/components/InputBox.vue"
import { Codemirror } from 'vue-codemirror'
import { getDataOrPopupError, postDataOrPopupError, addPopup, joinPath, ClickMenuManager, readableFileSize } from "@/assets/utils"
import { store } from "@/assets/store"

// --- CodeMirror Stuff
import { EditorView } from "@codemirror/view"
import { oneDark } from '@codemirror/theme-one-dark'
import { noctisLilac } from 'thememirror';

import { css } from '@codemirror/lang-css'
import { cpp } from '@codemirror/lang-cpp'
import { html } from '@codemirror/lang-html'
import { java } from '@codemirror/lang-java'
import { javascript } from '@codemirror/lang-javascript'
import { markdown } from '@codemirror/lang-markdown'
import { php } from '@codemirror/lang-php'
import { python } from '@codemirror/lang-python'
import { xml } from '@codemirror/lang-xml'
import { yaml } from '@codemirror/lang-yaml'


import { shell } from "@codemirror/legacy-modes/mode/shell"
import { StreamLanguage } from "@codemirror/language"
import IconTerminal from "@/components/icons/iconTerminal.vue"
import { useRouter } from "vue-router"

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const router = useRouter()

// ###########
// --- PWD ---
// ###########

// variable we maintain, pwd might be different when user modify 
// the input and do not hit enter
// we will add a watcher to this ref to automatically refresh it
const userPwd = ref("") // pwd of user input
let pwd = ref("")

setTimeout(async () => {
  pwd.value = await getDataOrPopupError(`/session/${props.session}/get_pwd`)
}, 0)

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

  let stopSignal = { signal: false }
  let downloadCoro = getDataOrPopupError(`/session/${props.session}/download_file`, {
    params: {
      folder: folder,
      filename: filename
    }
  })
  let checkDownloadsCoro = checkDownloadStatus(stopSignal)
  let content, _;
  try {
    [content, _] = await Promise.all([downloadCoro, checkDownloadsCoro])
  } catch (e) {
    stopSignal.signal = true;
    throw e
  }
  let url = `/utils/fetch_downloaded_file/${content.file_id}`;
  window.open(url, "_blank")

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
// --- File Transfer Hover Form ---
// ##############################

const uploadingFiles = ref([])
const downloadingFiles = ref([])

setTimeout(async () => {
  let result = await getDataOrPopupError(`/session/${props.session}/file_upload_status`)
  uploadingFiles.value = result
}, 0)

setTimeout(async () => {
  let result = await getDataOrPopupError(`/session/${props.session}/file_download_status`)
  downloadingFiles.value = result
}, 0)

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

const showUploadFileHoverForm = ref(false)

async function checkUploadStatus(stopSignal) {
  while (!stopSignal.signal) {
    await sleep(300)
    let result = await getDataOrPopupError(`/session/${props.session}/file_upload_status`)
    console.log(result)
    uploadingFiles.value = result
    if (result.length == 0) {
      return;
    }
  }
  // 最后再刷新一次，保证去除上传失败的文件
  let result = await getDataOrPopupError(`/session/${props.session}/file_upload_status`)
  uploadingFiles.value = result
}

async function checkDownloadStatus(stopSignal) {
  while (!stopSignal.signal) {
    await sleep(300)
    let result = await getDataOrPopupError(`/session/${props.session}/file_download_status`)
    console.log(result)
    downloadingFiles.value = result
    if (result.length == 0) {
      return;
    }
  }
  // 最后再刷新一次，保证去除上传失败的文件
  let result = await getDataOrPopupError(`/session/${props.session}/file_download_status`)
  downloadingFiles.value = result
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
let clickMenuEntry = undefined

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
    "name": "duplicate_file",
    "text": "复制一份新的文件",
    "icon": IconFile,
    "color": "white",
    "entry_type": ["file", "link-file"]
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
    "name": "delete_file",
    "text": "删除文件",
    "icon": IconDelete,
    "color": "red",
    "entry_type": ["file", "link-file"]
  },
  {
    "name": "open_terminal_here",
    "text": "在此处打开终端",
    "icon": IconTerminal,
    "color": "white",
    "entry_type": ["empty", "file", "link-file", "dir", "link-dir"]
  },
  {
    "name": "rename_file",
    "text": "重命名",
    "icon": IconPenSquare,
    "color": "white",
    "entry_type": ["file", "link-file", "dir", "link-dir"]
  },
  {
    "name": "open_dir",
    "text": "打开文件夹",
    "icon": IconDirectory,
    "color": "white",
    "entry_type": ["dir", "link-dir"]
  },
  {
    "name": "new_dir",
    "text": "新建文件夹",
    "icon": IconDirectory,
    "color": "white",
    "entry_type": ["empty", "file", "link-file", "dir", "link-dir"]
  },
  {
    "name": "delete_dir",
    "text": "删除文件夹",
    "icon": IconDelete,
    "color": "red",
    "entry_type": ["dir", "link-dir"]
  },
]
const ClickMenuFolderEntry = ClickMenuManager([

], (item) => {
  console.log(item)
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
  } else if (item.name == "duplicate_file") {
    confirmDuplicateFile(clickMenuEntry.name)
  } else if (item.name == "delete_file") {
    confirmDeleteFile(clickMenuEntry.name)
  } else if (item.name == "delete_dir") {
    confirmDeleteDir(clickMenuEntry.name)
  } else if (item.name == "new_dir") {
    confirmNewDir()

  } else if (item.name == "open_terminal_here") {
    router.push({
      path: `/terminal/${props.session}`,
      query: {
        pwd: pwd.value
      }
    })
  } else {
    addPopup("red", "内部错误", `没有实现动作：${item.name}`)
  }
})



function confirmNewFile() {
  showInputBox.value = true
  inputBoxTitle.value = "新建文件"
  inputBoxNote.value = "输入文件的文件名"
  inputBoxRequireInput.value = true
  inputBoxCallback = async filename => {
    if (!filename) {
      showInputBox.value = false
      return
    }
    try {
      let success = await postDataOrPopupError(`/session/${props.session}/put_file_contents`, {
        text: "",
        encoding: "utf-8",
        filename: filename,
        current_dir: pwd.value
      })
      if (success) {
        addPopup("green", "新建成功", `文件${filename}已经成功创建`)
      } else {
        addPopup("red", "新建失败", `文件${filename}创建失败`)
      }
    } finally {
      showInputBox.value = false
    }

    await listDir(pwd.value)

    viewNewFile(filename)
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
    try {
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
    } finally {
      showInputBox.value = false
    }
  }
}

function confirmDuplicateFile(filename) {
  showInputBox.value = true
  inputBoxTitle.value = "复制新的文件"
  inputBoxNote.value = `输入新的文件名${filename}`
  inputBoxRequireInput.value = true
  inputBoxCallback = async new_filename => {
    try {
      if (new_filename) {
        let result = await getDataOrPopupError(`/session/${props.session}/copy_file`, {
          params: {
            filepath: (await joinPath(pwd.value, filename)),
            new_filepath: (await joinPath(pwd.value, new_filename))
          }
        })
        if (result) {
          addPopup("green", "复制成功", `文件${filename}已经复制`)
        } else {
          addPopup("red", "复制失败", `文件${filename}复制失败`)
        }
        listDir(pwd.value)
      }
    } finally {
      showInputBox.value = false
    }
  }
}


function confirmDeleteFile(filename) {
  showInputBox.value = true
  inputBoxTitle.value = "删除文件"
  inputBoxNote.value = `真的要删除文件${filename}吗`
  inputBoxRequireInput.value = false
  inputBoxCallback = async result => {
    try {
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
    } finally {
      showInputBox.value = false

    }

  }
}


function confirmDeleteDir(filename) {
  showInputBox.value = true
  inputBoxTitle.value = "删除文件夹"
  inputBoxNote.value = `真的要删除文件夹${filename}吗`
  inputBoxRequireInput.value = false
  inputBoxCallback = async result => {
    try {
      if (result) {
        let result = await getDataOrPopupError(`/session/${props.session}/delete_file`, {
          params: {
            current_dir: pwd.value,
            filename: filename
          }
        })
        if (result) {
          addPopup("green", "删除成功", `文件夹${filename}已经删除`)
        } else {
          addPopup("red", "删除失败", `文件夹${filename}删除失败`)
        }
        listDir(pwd.value)
      }
    } finally {
      showInputBox.value = false
    }
  }
}

function confirmNewDir() {
  showInputBox.value = true
  inputBoxTitle.value = "新建文件夹"
  inputBoxNote.value = "输入文件夹的名称"
  inputBoxRequireInput.value = true
  inputBoxCallback = async dirname => {
    if (!dirname) {
      showInputBox.value = false
      return
    }
    try {
      let dirpath = await getDataOrPopupError("/utils/join_path", {
        params: {
          folder: pwd.value,
          entry: dirname
        }
      })
      let success = await getDataOrPopupError(`/session/${props.session}/mkdir`, {
        params: {
          dirpath: dirpath
        }
      })
      if (success) {
        addPopup("green", "新建成功", `文件夹${dirname}已经成功创建`)
      } else {
        addPopup("red", "新建失败", `文件夹${dirname}创建失败`)
      }
    } finally {
      showInputBox.value = false
    }
    await listDir(pwd.value)
  }
}

function onRightClickEntry(event) {
  const element = event.currentTarget
  const entry = entries.value[element.dataset.entryIndex]
  ClickMenuFolderEntry.items.value = menuItemsAll.filter(item => item.entry_type.includes(entry.entryType))
  clickMenuEntry = entry
  ClickMenuFolderEntry.onshow(event)
}

function onRightClickEmpty(event) {
  ClickMenuFolderEntry.items.value = menuItemsAll.filter(item => item.entry_type.includes("empty"))
  clickMenuEntry = undefined
  ClickMenuFolderEntry.onshow(event)
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
    "font-size": "1rem",
  },
  ".cm-gutters *": {
    "background-color": "var(--background-color-3)",

  }
}, { dark: true })

const codeMirrorExtensions = shallowRef([codeMirrorTheme, (store.theme == "glass" ? noctisLilac : oneDark)])

function codeMirrorReady(payload) {
  codeMirrorView.value = payload.view
}

watch(fileExtension, (newFileExtension, _) => {
  let extensions = [codeMirrorTheme, (store.theme == "glass" ? noctisLilac : oneDark)];
  let highlightings = [
    { suffix: ["cpp"], extension: () => cpp() },
    { suffix: ["css"], extension: () => css() },
    { suffix: ["html", "htm", "xhtml"], extension: () => html() },
    { suffix: ["java"], extension: () => java() },
    { suffix: ["js", "mjs"], extension: () => javascript() },
    { suffix: ["md"], extension: () => markdown() },
    { suffix: ["sh"], extension: () => StreamLanguage.define(shell) },
    { suffix: ["php", "php7", "php5", "phar"], extension: () => php() },
    { suffix: ["py"], extension: () => python() },
    { suffix: ["xml"], extension: () => xml() },
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
  try {
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
  } finally {
    await listDir(pwd.value)

  }


}

// input box 

const showInputBox = ref(false)
const inputBoxTitle = ref("")
const inputBoxNote = ref("")
const inputBoxRequireInput = ref(false)
let inputBoxCallback = ref(undefined)


// #################
// --- Utilities ---
// #################


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
  <div class="file-panel">
    <div class="folder-control">
      <form action="" class="filepath-input" @submit="onUserInputPwd">
        <input v-model="userPwd" id="filepath-input" class="shadow-box" type="text" placeholder="/var/www/html">
        <div class="filepath-icon shadow-box" @click="onUserInputPwd">
          <IconRun />
        </div>
        <div class="filepath-icon shadow-box" @click="() => {
          listDir(pwd);
          userPwd = pwd;
        }">
          <IconLoad />
        </div>
      </form>
      <div class="folder-panel scrollbar shadow-box" @click.right.stop="onRightClickEmpty">
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
    </div>

    <div class="file-content-panel">
      <div class="file-control">

        <div class="files-title">
          <input type="text" name="filename" id="files-title-filename" placeholder="passwd" class="shadow-box"
            v-model="userFilename">
        </div>
        <div class="file-actions shadow-box">
          <input type="text" name="encoding" id="file-actions-encoding" placeholder="文件编码" v-model="fileEncoding">
          <button class="button" @click="saveFile">保存</button>
        </div>
      </div>

      <div class="files-content scrollbar shadow-box">
        <codemirror v-model="codeMirrorContent" placeholder="Content goes here..." :autofocus="true"
          :indent-with-tab="true" :tab-size="4" :extensions="codeMirrorExtensions" @ready="codeMirrorReady" />
      </div>
    </div>
  </div>
  <transition>
    <div v-if="ClickMenuFolderEntry.show.value">
      <ClickMenu :mouse_x="ClickMenuFolderEntry.x" :mouse_y="ClickMenuFolderEntry.y"
        :menuItems="ClickMenuFolderEntry.items.value" @remove="ClickMenuFolderEntry.onremove"
        @clickItem="ClickMenuFolderEntry.onclick" />
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
      <div class="hover-form-line">
        <div class="input-file">
          <input type="file" name="file" id="file">
        </div>
      </div>
    </HoverForm>
  </transition>

  <transition>
    <HoverStatus v-if="uploadingFiles.length + downloadingFiles.length != 0">
      <div class="file-transfer">
        <h1 v-if="uploadingFiles.length != 0">上传进度</h1>
        <div class="file-transfer-file" v-for="file in uploadingFiles">
          <div class="file-transfer-percentage">
            <p>
              {{ Math.floor(file.percentage * 100) }}%
            </p>
          </div>
          <div class="file-transfer-fileinfo">
            <p class="file-transfer-filename">
              {{ file.file }}
            </p>
            <p class="file-transfer-meta">
              {{ readableFileSize(file.done_bytes) }}
              / {{ readableFileSize(file.max_bytes) }}
              at {{ file.folder }}
            </p>
          </div>

        </div>
        <h1 v-if="downloadingFiles.length != 0">下载进度</h1>
        <div class="file-transfer-file" v-for="file in downloadingFiles">
          <div class="file-transfer-percentage">
            <p>
              {{ Math.floor(file.percentage * 100) }}%
            </p>
          </div>
          <div class="file-transfer-fileinfo">
            <p class="file-transfer-filename">
              {{ file.file }}
            </p>
            <p class="file-transfer-meta">
              {{ readableFileSize(file.done_bytes) }}
              / {{ readableFileSize(file.max_bytes) }}
              at {{ file.folder }}
            </p>
          </div>

        </div>
      </div>
    </HoverStatus>
  </transition>

</template>

<style scoped>
.filepath-input {
  display: flex;
  height: 2.8rem;
}

input[type="text"] {
  font-size: 1.3rem;
  text-indent: 10px;
  color: var(--font-color-primary);
  border: none;
  outline: none;
  border-radius: 1rem;
}

.filepath-input input {
  background-color: var(--background-color-2);
  flex-grow: 1;
  min-width: 50px;
}

.filepath-icon {
  flex-grow: 0;
  flex-shrink: 0;
  width: 2.8rem;
  margin-left: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color-2);
  border-radius: 1rem;
  transition: all 0.3s ease;
  opacity: 1;
}

.filepath-icon:hover {
  background-color: var(--background-color-3);
  outline: 2px solid var(--font-color-secondary);
}

.filepath-icon svg {
  width: 1.8rem;
}

.file-panel {
  display: flex;
  height: 85%;
  flex-grow: 1;
  justify-content: space-between;
  margin-top: 20px;
}

.folder-control {
  width: 25%;
  display: flex;
  flex-direction: column;
  margin-right: 30px;

}

.folder-panel {
  flex-grow: 1;
  margin-top: 20px;
  height: 60%;
  border-radius: 1rem;
  background-color: var(--background-color-2);
  padding-top: 20px;
  overflow: overlay;
  flex-shrink: 0;
  transition: background 1s ease;
}

.folder-entry {
  display: flex;
  min-height: 3.2rem;
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
  margin: 0px 15px;
}

.folder-entry-icon svg {
  width: 2rem;
}

.folder-entry-info {
  font-size: 0.8rem;
  display: flex;
  flex-direction: column;
}

.folder-entry-name {
  color: var(--font-color-primary);
  font-size: 1.2rem;
  margin: 0;
}

.folder-entry-meta {
  color: var(--font-color-secondary);

}

.file-content-panel {
  width: 60%;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.file-control {
  display: flex;
  flex-direction: row;
}

.files-title {
  height: 2.8rem;
  width: 50%;
  margin-right: 20px;
  flex-grow: 1;
  flex-shrink: 0;
}

.files-title input {
  border: none;
  outline: none;
  height: 100%;
  width: 100%;
  background-color: var(--background-color-2);
  font-size: 1.3rem;
}

.files-content {
  flex-grow: 1;
  margin-top: 20px;
  border-radius: 1rem;
  padding-top: 20px;
  padding-bottom: 20px;
  background-color: var(--background-color-2);
  overflow: auto;
}

.file-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: var(--background-color-2);
  border-radius: 1rem;
  padding-left: 20px;
  padding-right: 20px;
  height: 2.8rem;
  color: var(--font-color-primary);
  flex-shrink: 0;
  justify-content: space-between;
}

.file-actions input {
  height: 2rem;
  max-width: 100px;
  background-color: var(--background-color-3);
  font-size: 0.8rem;
  color: var(--font-color-primary);
  margin-right: 10px;
}


.file-actions button {
  height: 2rem;
  margin-right: 10px;
}

.file-transfer {
  padding: 20px;
  color: var(--font-color-primary);
}

.file-transfer p {
  margin: 0;
}

.file-transfer-file {
  background-color: #00000015;
  height: 100px;
  border-radius: 1rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 20px;
}

.file-transfer-fileinfo {
  display: flex;
  flex-direction: column;
  align-items: left;
}

.file-transfer-filename {
  font-size: 28px;
}

.file-transfer-meta {
  color: var(--font-color-secondary);
}

.file-transfer-percentage {
  margin-right: 20px;
  font-size: 36px;
  width: 130px;
  background-color: #00000015;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70px;
  border-radius: 1rem;
}

svg {
  stroke: var(--font-color-primary);
}
</style>
