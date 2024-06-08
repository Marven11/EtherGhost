<script setup>
import { ref } from "vue";

import IconOthers from "./icons/iconOthers.vue"
import IconPlus from "./icons/iconPlus.vue"
import IconTerminal from "./icons/iconTerminal.vue"
import IconFileBrowser from "./icons/iconFileBrowser.vue"
import IconProxy from "./icons/iconProxy.vue"
import IconInfo from "./icons/iconInfo.vue"
import IconEdit from "./icons/iconEdit.vue"
import IconDelete from "./icons/iconDelete.vue"

import ClickMenu from "./ClickMenu.vue"
import { addPopup, getDataOrPopupError } from "@/assets/utils";
import { useRouter } from "vue-router"
import InputBox from "./InputBox.vue"
import axios from "axios"

import { getCurrentApiUrl } from "@/assets/utils";


const sessions = ref([
])

// ################
// --- Elements ---
// ################


const showClickMenu = ref(false)
const clickMenuLeft = ref(0)
const clickMenuTop = ref(0)
const router = useRouter();
let clickMenuSession = ""

const menuItems = [
  {
    "name": "open_terminal",
    "text": "打开终端",
    "icon": IconTerminal,
    "color": "white",
    "link": "/terminal/SESSION"
  },
  {
    "name": "browse_files",
    "text": "浏览文件",
    "icon": IconFileBrowser,
    "color": "white",
    "link": "/file-browser/SESSION"
  },
  {
    "name": "open_proxy",
    "text": "打开代理",
    "icon": IconProxy,
    "color": "white",
    "link": "/page_404/SESSION"
  },
  {
    "name": "get_info",
    "text": "基本信息",
    "icon": IconInfo,
    "color": "white",
    "link": "/page_404/SESSION"
  },
  {
    "name": "edit_session",
    "text": "修改webshell",
    "icon": IconEdit,
    "color": "white",
    "link": "/webshell-editor/SESSION"
  },
  {
    "name": "delete_session",
    "text": "删除Webshell",
    "icon": IconDelete,
    "color": "red",
    "link": undefined,
    "func": (session) => onMarkDeleteSession(session),
  }
]

function onClickIconOthers(event) {
  showClickMenu.value = true
  clickMenuLeft.value = event.clientX;
  clickMenuTop.value = event.clientY;
  clickMenuSession = event.currentTarget.dataset["session"];
}

function onClickMenuItem(item) {
  if (item.link) {
    const uri = item.link.replace("SESSION", clickMenuSession)
    console.log(uri)
    router.push(uri)
  } else if (item.func) {
    item.func(clickMenuSession)
  }

}

async function fetchWebshell() {
  const newSessions = await getDataOrPopupError("/session")
  console.log(newSessions)
  sessions.value = newSessions
}

setTimeout(fetchWebshell, 0)

// ################
// --- InputBox ---
// ################


const showInputBox = ref(false)
const inputBoxTitle = ref("")
const inputBoxNote = ref("")
let inputBoxCallback = ref(undefined)

// ######################
// --- Delete Session ---
// ######################

let sessionToDelete = undefined

function onMarkDeleteSession(sessionId) {
  sessionToDelete = sessionId
  showInputBox.value = true
  inputBoxTitle.value = "删除Session"
  inputBoxNote.value = "你真的要删除这个session吗？"
  inputBoxCallback = onDeleteSessionConfirm
}

async function onDeleteSessionConfirm(userConfirm) {
  console.log(userConfirm)
  if (!sessionToDelete) {
    addPopup("red", "内部错误", `找不到要删除的webshell`)
    return
  }
  if (userConfirm) {
    let result = await axios.delete(`${getCurrentApiUrl()}/session/${sessionToDelete}`)
    if (result) {
      addPopup("green", "删除成功", `已经删除指定session`)
    } else {
      addPopup("red", "删除失败", `无法删除指定session`)
    }
  }
  showInputBox.value = false
  sessionToDelete = undefined
  setTimeout(fetchWebshell, 0)
}

</script>

<template>
  <div class="sessions">
    <div class="session" v-for="session in sessions">
      <div class="session-top">
        <div class="session-name">
          <p>
            {{ session.name }}
          </p>
        </div>
        <div>
          <div class="session-icon-others" :data-session="session.id" @click="onClickIconOthers">
            <IconOthers />
          </div>
        </div>
      </div>
      <div class="session-bottom">
        <div class="session-note">
          {{ session.note }}
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

  <div class="add-webshell-button" @click="router.push('/webshell-editor/')">
    <IconPlus />
  </div>
  <transition>
    <InputBox v-if="showInputBox" :title="inputBoxTitle" :note="inputBoxNote" :requireInput="false"
      @result="inputBoxCallback" />
  </transition>
</template>

<style scoped>
.sessions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  column-gap: 2%;
  justify-content: space-between;
}

.session {
  height: 160px;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  margin-bottom: 40px;
  padding-left: 20px;
  padding-right: 20px;
  border-radius: 20px;
}

.session-top {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 40%;
}

.session-top p,
.session-top svg {
  margin: 0px;
  margin-top: 20px;
}

.session-top p {
  font-size: 26px;
  font-weight: bold;
}

.session-bottom {
  color: var(--font-color-grey);
}

.add-webshell-button {
  width: 70px;
  height: 70px;
  background-color: #00000030;
  border-radius: 1000px;
  position: fixed;
  top: 90vh;
}

.add-webshell-button svg {
  width: 50px;
  stroke: var(--font-color-white);
  margin: 10px;
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
