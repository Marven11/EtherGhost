<script setup>
import { ref } from "vue";
import IconCode from "@/components/icons/iconCode.vue"
import IconDelete from "@/components/icons/iconDelete.vue"
import IconEdit from "@/components/icons/iconEdit.vue"
import IconFileBrowser from "@/components/icons/iconFileBrowser.vue"
import IconHash from "@/components/icons/iconHash.vue"
import IconInfo from "@/components/icons/iconInfo.vue"
import IconOthers from "@/components/icons/iconOthers.vue"
import IconPlus from "@/components/icons/iconPlus.vue"
import IconProxy from "@/components/icons/iconProxy.vue"
import IconTerminal from "@/components/icons/iconTerminal.vue"


import ClickMenu from "@/components/ClickMenu.vue"
import { addPopup, ClickMenuManager, getDataOrPopupError, parseDataOrPopupError } from "@/assets/utils";
import { useRouter } from "vue-router"
import InputBox from "@/components/InputBox.vue"
import axios from "axios"

import { getCurrentApiUrl } from "@/assets/utils";
import { store } from "@/assets/store";
import IconSpider from "@/components/icons/iconSpider.vue";
import IconKnife from "@/components/icons/iconKnife.vue";
import IconPlug from "../icons/iconPlug.vue";


const sessions = ref([
])

// ################
// --- Elements ---
// ################


const router = useRouter();
let clickedSession = ""

const ClickMenuSession = ClickMenuManager(
  [
    {
      "name": "terminal",
      "text": "模拟终端",
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
      "name": "open_php_eval",
      "text": "PHP Eval",
      "icon": IconCode,
      "color": "white",
      "link": "/php-eval/SESSION"
    },
    {
      "name": "open_proxy",
      "text": "打开代理",
      "icon": IconProxy,
      "color": "white",
      "link": "/proxies/SESSION"
    },
    {
      "name": "get_info",
      "text": "基本信息",
      "icon": IconInfo,
      "color": "white",
      "link": "/basic-info/SESSION"
    },
    {
      "name": "open_shell_command",
      "text": "命令执行",
      "icon": IconHash,
      "color": "white",
      "link": "/shell-command/SESSION"
    },
    {
      "name": "reverse_shell",
      "text": "反弹Shell",
      "icon": IconPlug,
      "color": "white",
      "link": "/reverse-shell/SESSION"
    },
    {
      "name": "emulated_antsword",
      "text": "对接蚁剑",
      "icon": IconSpider,
      "color": "white",
      "link": "/emulated-antsword/SESSION"
    },
    {
      "name": "awd_tools",
      "text": "AWD实用工具",
      "icon": IconKnife,
      "color": "white",
      "link": "/awd-tools/SESSION"
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
  ],
  (item) => {
    if (item.link) {
      const uri = item.link.replace("SESSION", clickedSession)
      router.push(uri)
    } else if (item.func) {
      item.func(clickedSession)
    }
  }
)

function onClickIconOthers(event, sessionId) {
  clickedSession = sessionId;
  ClickMenuSession.onshow(event)
}

async function fetchWebshell() {
  const newSessions = await getDataOrPopupError("/session")
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
  if (!sessionToDelete) {
    addPopup("red", "内部错误", `找不到要删除的webshell`)
    return
  }
  try {
    if (userConfirm) {
      let response = await axios.delete(`${getCurrentApiUrl()}/session/${sessionToDelete}`)
      let result = parseDataOrPopupError(response)
      if (result) {
        addPopup("green", "删除成功", `已经删除指定session`)
      } else {
        addPopup("red", "删除失败", `无法删除指定session`)
      }
    }
  } finally {
    showInputBox.value = false
    sessionToDelete = undefined
    setTimeout(fetchWebshell, 0)
  }
}

</script>

<template>
  <div class="main-panel">
    <div class="sessions" v-if="sessions.length != 0">
      <div class="session shadow-box" v-for="session in sessions"
        @click.right="event => onClickIconOthers(event, session.id)">
        <div class="session-top">
          <div class="session-name">
            <p>
              {{ session.name }}
            </p>
          </div>
          <div>
            <div class="session-icon-others" @click="event => onClickIconOthers(event, session.id)">
              <IconOthers />
            </div>
          </div>
        </div>
        <div class="session-middle">
          <div class="session-note">
            {{ session.note }}
          </div>
        </div>
        <div class="session-bottom">
          <p>
            {{ session.readable_type }}
          </p>
          <p>
            {{ session.location }}

          </p>
        </div>
      </div>
    </div>
    <div class="no-session-panel" v-else>
      <IconTerminal></IconTerminal>
      <p>现在就添加一个webshell吧</p>
    </div>
  </div>

  <transition>
    <div v-if="ClickMenuSession.show.value">
      <ClickMenu :mouse_y="ClickMenuSession.y" :mouse_x="ClickMenuSession.x" :menuItems="ClickMenuSession.items.value"
        @remove="ClickMenuSession.onremove" @clickItem="ClickMenuSession.onclick" />
    </div>
  </transition>

  <div class="add-webshell-button shadow-box" @click="store.session = ''; router.push('/webshell-editor/')">
    <IconPlus />
  </div>
  <transition>
    <InputBox v-if="showInputBox" :title="inputBoxTitle" :note="inputBoxNote" :requireInput="false"
      @result="inputBoxCallback" />
  </transition>
</template>

<style scoped>
.main-panel {
  display: flex;
  height: 100%;
  width: 100%;
  flex-direction: column;
}

.sessions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
  column-gap: 2%;
  justify-content: space-between;
}

.no-session-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.no-session-panel svg {
  width: 24%;
  height: 24%;
  stroke: var(--font-color-secondary);
}

.no-session-panel p {
  font-size: 1.5rem;
  color: var(--font-color-secondary);
}

.session {
  display: flex;
  flex-direction: column;
  height: 9rem;
  background-color: var(--background-color-2);
  color: var(--font-color-primary);
  margin-bottom: 40px;
  padding-left: 25px;
  padding-right: 25px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.session:hover {
  filter: brightness(105%);
  box-shadow: 0 0 5px rgba(15, 15, 15, 0.5);
}

.session-top {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 35%;
  margin-top: 0.6rem;
}

.session-top svg {
  margin-top: 5px;
}

.session-name {
  margin: 0px;
  font-size: 1.2rem;
  font-weight: bold;
}

.session-name p {
  margin: 0px;
}

.session-middle {
  color: var(--font-color-secondary);
  font-size: 0.75rem;
  flex-grow: 1;
}

.session-bottom {
  bottom: 0;
  margin-bottom: 20px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.session-bottom p {
  margin: 0;
  color: var(--font-color-secondary);
  font-size: 0.75rem;
}


.add-webshell-button {
  width: 3.5rem;
  height: 3.5rem;
  background-color: #00000030;
  border-radius: 1000px;
  position: fixed;
  top: 90vh;
  transition: background 0.3s ease;
}

.add-webshell-button svg {
  width: 80%;
  stroke: var(--font-color-primary);
  margin: 10%;
}

.add-webshell-button:hover {
  background-color: #00000015;
}

svg {
  width: 1.8rem;
  stroke: var(--font-color-primary);
}
</style>
