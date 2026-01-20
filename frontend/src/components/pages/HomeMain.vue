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


import ClickMenuDualLayer from "@/components/ClickMenuDualLayer.vue"
import { addPopup, ClickMenuManagerDualLayer, getDataOrPopupError, parseDataOrPopupError } from "@/assets/utils";
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

// 多选状态
const isMultiSelectMode = ref(false)
const selectedSessionIds = ref(new Set())
const batchOperationStatus = ref({}) // sessionId -> 'pending' | 'success' | 'error'
const isBatchOperating = ref(false)

// ################
// --- Elements ---
// ################


const router = useRouter();
let clickedSession = ""

const ClickMenuSession = ClickMenuManagerDualLayer(
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
      "text": "PHP代码执行",
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
      "name": "multiselect",
      "text": "多选webshell",
      "icon": IconTerminal, // 临时图标，稍后可以更换
      "color": "white",
      "link": undefined,
      "func": (session) => enterMultiSelectMode(),
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

// 批量操作菜单
const ClickMenuBatchOperation = ClickMenuManagerDualLayer(
  [
    {
      "name": "batch_test_webshell",
      "text": "批量测试webshell",
      "icon": IconInfo,
      "color": "white",
      "func": () => batchTestWebshell(),
    },
    {
      "name": "batch_print_to_console",
      "text": "打印到console",
      "icon": IconTerminal,
      "color": "white",
      "func": () => batchPrintToConsole(),
    },
    // 后续可以添加更多批量操作
  ],
  (item) => {
    if (item.func) {
      item.func()
    }
  }
)

function onClickIconOthers(event, sessionId) {
  event.stopPropagation();
  event.preventDefault();
  clickedSession = sessionId;
  ClickMenuSession.onshow(event)
}

// 进入多选模式
function enterMultiSelectMode() {
  isMultiSelectMode.value = true
  selectedSessionIds.value.clear()
  batchOperationStatus.value = {}
}

// 退出多选模式
function exitMultiSelectMode() {
  if (isBatchOperating.value) {
    // 中断批量操作
    batchOperationStatus.value = {}
    isBatchOperating.value = false
  }
  isMultiSelectMode.value = false
  selectedSessionIds.value.clear()
  batchOperationStatus.value = {}
}

// 切换session选中状态
function toggleSessionSelection(sessionId, event) {
  if (!isMultiSelectMode.value) return
  
  event.stopPropagation()
  event.preventDefault()
  
  const newSet = new Set(selectedSessionIds.value)
  if (newSet.has(sessionId)) {
    newSet.delete(sessionId)
  } else {
    newSet.add(sessionId)
  }
  selectedSessionIds.value = newSet
}

// 右键处理（多选模式下）
function handleRightClickInMultiSelectMode(event, sessionId) {
  if (!isMultiSelectMode.value) return
  if (!selectedSessionIds.value.has(sessionId)) return
  
  event.stopPropagation()
  event.preventDefault()
  clickedSession = sessionId
  // 显示批量操作菜单
  ClickMenuBatchOperation.onshow(event)
}

// 处理session点击事件
function handleSessionClick(event, sessionId) {
  if (isMultiSelectMode.value) {
    toggleSessionSelection(sessionId, event)
  }
  // 非多选模式下不做特殊处理
}

// 处理session右键事件
function handleSessionRightClick(event, sessionId) {
  if (isMultiSelectMode.value && selectedSessionIds.value.has(sessionId)) {
    handleRightClickInMultiSelectMode(event, sessionId)
  } else {
    onClickIconOthers(event, sessionId)
  }
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

// 批量打印到console（dummy功能）
async function batchPrintToConsole() {
  if (selectedSessionIds.value.size === 0) {
    addPopup("red", "错误", "没有选中任何webshell")
    return
  }

  isBatchOperating.value = true
  
  // 初始化状态
  const sessionIds = Array.from(selectedSessionIds.value)
  for (const sessionId of sessionIds) {
    batchOperationStatus.value[sessionId] = 'pending'
  }

  // 模拟批量操作
  for (const sessionId of sessionIds) {
    // 等待0.5秒，模拟操作延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 随机成功或失败
    const isSuccess = Math.random() > 0.3
    batchOperationStatus.value[sessionId] = isSuccess ? 'success' : 'error'
    
    // 打印到console
    const session = sessions.value.find(s => s.id === sessionId)
    console.log(`批量操作: ${session?.name || sessionId}`)
  }

  // 所有操作完成，等待三秒
  setTimeout(() => {
    // 清除状态
    batchOperationStatus.value = {}
    isBatchOperating.value = false
    
    // 如果没有选中的session，自动退出多选模式
    if (selectedSessionIds.value.size === 0) {
      exitMultiSelectMode()
    }
  }, 3000)
}

// 批量测试webshell
async function batchTestWebshell() {
  if (selectedSessionIds.value.size === 0) {
    addPopup("red", "错误", "没有选中任何webshell")
    return
  }

  isBatchOperating.value = true
  
  // 初始化状态
  const sessionIds = Array.from(selectedSessionIds.value)
  for (const sessionId of sessionIds) {
    batchOperationStatus.value[sessionId] = 'pending'
  }

  try {
    // 对每个选中的webshell进行测试
    for (const sessionId of sessionIds) {
      const session = sessions.value.find(s => s.id === sessionId)
      if (!session) {
        batchOperationStatus.value[sessionId] = 'error'
        continue
      }
      
      try {
        // 调用后端测试API - 需要发送完整的session_info结构
        // 从session对象中提取后端需要的信息
        const sessionInfo = {
          session_id: session.id,
          name: session.name,
          type: session.type,
          url: session.url,
          password: session.password,
          comment: session.comment,
          extra_data: session.extra_data || {},
        }
        
        const response = await axios.post(`${getCurrentApiUrl()}/test_webshell`, sessionInfo)
        const result = parseDataOrPopupError(response)
        
        if (result && result.success) {
          batchOperationStatus.value[sessionId] = 'success'
        } else {
          batchOperationStatus.value[sessionId] = 'error'
        }
      } catch (error) {
        console.error(`测试webshell ${sessionId} 失败:`, error)
        batchOperationStatus.value[sessionId] = 'error'
      }
      
      // 每个测试间隔0.2秒，避免服务器压力过大
      await new Promise(resolve => setTimeout(resolve, 200))
    }
  } finally {
    // 所有操作完成，等待三秒
    setTimeout(() => {
      // 清除状态
      batchOperationStatus.value = {}
      isBatchOperating.value = false
      
      // 如果没有选中的session，自动退出多选模式
      if (selectedSessionIds.value.size === 0) {
        exitMultiSelectMode()
      }
    }, 3000)
  }
}

</script>

<template>
  <div class="main-panel">
    <div class="sessions" v-if="sessions.length != 0">
      <div class="session shadow-box session-container" v-for="session in sessions"
        @click="event => handleSessionClick(event, session.id)"
        @click.right="event => handleSessionRightClick(event, session.id)">
        <!-- 小圆点状态指示器 -->
        <div class="session-dot"
          :class="{
            'selected': selectedSessionIds.has(session.id) && !batchOperationStatus[session.id],
            'pending': batchOperationStatus[session.id] === 'pending',
            'success': batchOperationStatus[session.id] === 'success',
            'error': batchOperationStatus[session.id] === 'error'
          }">
        </div>
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
          <div class="session-type-dot">
            <div :data-type="session.type"></div>
          </div>
          <p>
            {{ session.readable_type }}
          </p>
          <div class="session-bottom-seperator"></div>
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
      <ClickMenuDualLayer :mouse_y="ClickMenuSession.y.value" :mouse_x="ClickMenuSession.x.value" :menuItems="ClickMenuSession.items.value" :show="ClickMenuSession.show"
        @close="ClickMenuSession.onremove" @select="ClickMenuSession.onclick" />
    </div>
  </transition>

  <transition>
    <div v-if="ClickMenuBatchOperation.show.value">
      <ClickMenuDualLayer :mouse_y="ClickMenuBatchOperation.y.value" :mouse_x="ClickMenuBatchOperation.x.value" :menuItems="ClickMenuBatchOperation.items.value" :show="ClickMenuBatchOperation.show"
        @close="ClickMenuBatchOperation.onremove" @select="ClickMenuBatchOperation.onclick" />
    </div>
  </transition>

  <div class="add-webshell-button shadow-box" @click="store.session = ''; router.push('/webshell-editor/')">
    <IconPlus />
  </div>
  <div v-if="isMultiSelectMode" class="exit-multiselect-button shadow-box" @click="exitMultiSelectMode" title="退出多选模式">
    ×
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

.session-type-dot {
  width: 1rem;
  height: 1rem;

}

.session-type-dot div {

  width: 0.5rem;
  height: 0.5rem;
  border-radius: 20px;

  margin: 0.25rem;
  margin-left: 0rem;

  background-color: var(--white);
}

.session-type-dot div[data-type="ONELINE_PHP"] {
  background-color: var(--color-php);
}

.session-type-dot div[data-type="BEHINDER_PHP_AES"] {
  background-color: var(--color-php);
}

.session-type-dot div[data-type="BEHINDER_PHP_XOR"] {
  background-color: var(--color-php);
}

.session-type-dot div[data-type="BEHINDER_JSP_AES"] {
  background-color: var(--color-java);
}

.session-type-dot div[data-type="LINUX_CMD_ONELINER"] {
  background-color: var(--color-shell);
}

.session-bottom-seperator {
  flex-grow: 1;
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
.session-icon-others {
  cursor: pointer;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 多选相关样式 */
.session-container {
  position: relative;
}

.session-dot {
  position: absolute;
  top: 0rem;
  left: 0rem;
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
  box-shadow: 0 0 5px rgba(15, 15, 15, 0.5);
}

.session-dot.selected {
  opacity: 1;
  background-color: var(--green);
}

.session-dot.pending {
  opacity: 1;
  background-color: var(--yellow);
  animation: pulse 0.5s infinite alternate;
}

.session-dot.success {
  opacity: 1;
  background-color: var(--green);
}

.session-dot.error {
  opacity: 1;
  background-color: var(--red);
}

@keyframes pulse {
  from {
    opacity: 0.6;
  }
  to {
    opacity: 1;
  }
}

.exit-multiselect-button {
  width: 3.5rem;
  height: 3.5rem;
  background-color: #00000030;
  border-radius: 1000px;
  position: fixed;
  top: 90vh;
  left: calc(50% + 3.5rem); /* 在添加按钮右侧，间隔一些距离 */
  transform: translateX(-50%);
  transition: background 0.3s ease, transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--font-color-primary);
  font-size: 1.5rem;
  cursor: pointer;
  border: 2px solid transparent;
}

.exit-multiselect-button:hover {
  background-color: #00000015;
  border-color: rgba(255, 255, 255, 0.3);
}

.exit-multiselect-button:active {
  transform: translateX(-50%) scale(0.95);
}

</style>
