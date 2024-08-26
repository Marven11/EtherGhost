<script setup>

import { addPopup, getCurrentApiUrl, getDataOrPopupError, parseDataOrPopupError, postDataOrPopupError } from "@/assets/utils";
import { reactive, ref, watch } from "vue";
import iconCross from "./icons/iconCross.vue";
import { store } from "@/assets/store";
import axios from "axios";

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}


const sessions = ref([])
const supportedSendMethods = reactive({})

const readableProxyType = {
  vessel_forward_tcp: "Vessel正向TCP代理",
  psudo_forward_proxy: "伪正向代理（仅支持HTTP）",
}

// `openedProxies` is a list of objects like:
// {
//     "type": "psudo_forward_proxy",
//     "session_id": session_id,
//     "session_name": get_session_name(session_id),
//     "listen_host": listen_host,
//     "listen_port": listen_port,
//     "host": host,
//     "port": port,
//     "send_method": send_method,
// }

const openedProxies = ref([])

// TODO: support not just remote IP but remote address

const addProxyInput = reactive({
  type: "",
  session_id: "",
  listen_host: "",
  listen_port: "",
  host: "",
  port: "",
  send_method: "",
})

// null: no input, false: input invalid, true: input valid
const addProxyInputValid = reactive({
  session_id: null,
  listen_host: null,
  listen_port: null,
  host: null,
  port: null,
  send_method: null,
})


async function createProxy() {
  const invalidInputs = Object.entries(addProxyInputValid).filter(pair => (!pair[1]) && pair[0] != "send_method").map(pair => pair[0])
  if (invalidInputs.length != 0) {
    addPopup("red", "请填写所有选项", `${invalidInputs[0]}选项未填写正确`)
    return;
  } else if (addProxyInput.type == "") {
    addPopup("red", "请填写代理类型", "代理类型未填写")
  } else if (addProxyInput.type == "psudo_forward_proxy" || addProxyInput.type == "vessel_forward_tcp") {
    const data = {
      "type": addProxyInput.type,
      "session_id": addProxyInput.session_id,
      "listen_host": addProxyInput.listen_host,
      "listen_port": parseInt(addProxyInput.listen_port),
      "host": addProxyInput.host,
      "port": parseInt(addProxyInput.port),
      "send_method": addProxyInput.send_method ? addProxyInput.send_method : null,
    }
    await postDataOrPopupError("/forward_proxy/create_psudo_proxy", data)
    addPopup("green", "代理添加成功", `到${addProxyInput.host}:${addProxyInput.port}的代理添加成功`)
    Object.keys(addProxyInput).forEach(key => {
      addProxyInput[key] = ""
    });
    setTimeout(() => {
      addPopup("yellow", "此功能仍不稳定", `代理仍在测试中，且仅支持HTTP！`)
    }, 500)
  } else {
    addPopup("red", "不支持的代理类型", `当前还不支持以下代理类型${JSON.stringify(addProxyInput.type)}`)
  }
  openedProxies.value = await getDataOrPopupError("/forward_proxy/list")

}
async function closeProxy(listen_port) {
  const response = await axios.delete(`${getCurrentApiUrl()}/forward_proxy/${listen_port}/`)
  try {
    const result = parseDataOrPopupError(response)
    if (!result) {
      addPopup("yellow", "关闭失败", "代理无法被关闭")
    }
  } finally {
    openedProxies.value = await getDataOrPopupError("/forward_proxy/list")
  }
}

watch(addProxyInput, (newValue, oldValue) => {
  addProxyInputValid.session_id = newValue.session_id == "" ? null : true
  addProxyInputValid.listen_host = newValue.listen_host == "" ? null : /^\d+\.\d+\.\d+\.\d+$/.test(newValue.listen_host)
  addProxyInputValid.listen_port = newValue.listen_port == "" ? null : /^\d{1,5}$/.test(newValue.listen_port)
  addProxyInputValid.host = newValue.host == "" ? null : /^\d+\.\d+\.\d+\.\d+$/.test(newValue.host)
  addProxyInputValid.port = newValue.port == "" ? null : /^\d{1,5}$/.test(newValue.port)
  if (newValue.send_method == "") {
    addProxyInputValid.send_method = null
  } else if (!supportedSendMethods[newValue.session_id]) {
    addProxyInputValid.send_method = false
  } else {
    addProxyInputValid.send_method = supportedSendMethods[newValue.session_id].includes(addProxyInput.send_method)
  }
})

watch(() => addProxyInput.session_id, async (newValue, oldValue) => {
  if (newValue == "") {
    return
  }
  if (!supportedSendMethods[newValue]) {
    supportedSendMethods[newValue] = await getDataOrPopupError(`/session/${newValue}/supported_send_tcp_methods`)
  }
})

setTimeout(async () => {
  const newSessions = await getDataOrPopupError("/session")
  sessions.value = newSessions.map(session => ({
    name: session.name,
    readable_type: session.readable_type,
    id: session.id,
  }))
}, 0)

setTimeout(async () => {
  openedProxies.value = await getDataOrPopupError("/forward_proxy/list")
}, 0)

setTimeout(() => {
  if (store.session) {
    addProxyInput.session_id = store.session
  }
}, 0)

</script>

<template>
  <div class="add-proxy shadow-box">
    <form action="" class="add-proxy-form" @submit.prevent="createProxy">
      <select name="proxy_type" id="" v-model="addProxyInput.type">
        <option value="">选择代理类型</option>
        <option v-for="proxyType in Object.keys(readableProxyType)" :value="proxyType">{{
          readableProxyType[proxyType] }}</option>
        <!-- <option value="backward">反向代理</option> -->
        <!-- TODO: add reverse proxy function -->
      </select>
      <select name="session" id="" v-model="addProxyInput.session_id">
        <option :value="''">选择一个session
        </option>
        <option v-for="session in sessions" :value="session.id">{{ session.readable_type }} - {{ session.name }}
        </option>
      </select>
      <input type="text" name="listen_host" id="" placeholder="本地监听IP" v-model="addProxyInput.listen_host"
        :data-valid="addProxyInputValid.listen_host">
      <input type="text" name="listen_port" id="" placeholder="本地监听端口" v-model="addProxyInput.listen_port"
        :data-valid="addProxyInputValid.listen_port">
      <input type="text" name="host" id="" placeholder="远程连接IP" v-model="addProxyInput.host"
        :data-valid="addProxyInputValid.host">
      <input type="text" name="port" id="" placeholder="远程连接端口" v-model="addProxyInput.port"
        :data-valid="addProxyInputValid.port">
      <select v-if="supportedSendMethods.length != 0 && addProxyInput.session_id != '' && addProxyInput.type=='psudo_forward_proxy'" name="send_method" id=""
        v-model="addProxyInput.send_method">
        <option :value="''">自动选择发送方法
        </option>
        <option v-for="method in supportedSendMethods[addProxyInput.session_id]" :value="method">{{ method }}
        </option>
      </select>
      <input type="button" value="添加代理" @click="createProxy">
    </form>
  </div>
  <table class="opened-proxies shadow-box">
    <tr class="opened-proxies-row">
      <th class="open-proxies-head">Session</th>
      <th class="open-proxies-head">代理类型</th>
      <th class="open-proxies-head">监听IP</th>
      <th class="open-proxies-head">监听端口</th>
      <th class="open-proxies-head">远程连接IP</th>
      <th class="open-proxies-head">远程连接端口</th>
      <th class="open-proxies-head">发送方式</th>
      <th class="open-proxies-head">操作</th>
    </tr>
    <tr class="opened-proxies-row" v-for="proxy in openedProxies">
      <td class="open-proxies-data">{{ proxy.session_name }}</td>
      <td class="open-proxies-data">{{ readableProxyType[proxy.type] }}</td>
      <td class="open-proxies-data">{{ proxy.listen_host }}</td>
      <td class="open-proxies-data">{{ proxy.listen_port }}</td>
      <td class="open-proxies-data">{{ proxy.host }}</td>
      <td class="open-proxies-data">{{ proxy.port }}</td>
      <td class="open-proxies-data">{{ proxy.send_method }}</td>
      <td class="open-proxies-data">
        <div class="close-proxy-button" @click="closeProxy(proxy.listen_port)">
          <iconCross></iconCross>
        </div>
      </td>
    </tr>
  </table>
</template>

<style scoped>
.add-proxy {
  background-color: var(--background-color-2);
  border-radius: 20px;
  width: 100%;
  height: 100px;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
}

.add-proxy-form {
  width: 80%;
  height: 100%;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
}

.add-proxy input,
.add-proxy select {
  height: 50px;
  min-width: 100px;
  border-radius: 20px;
  border: none;
  outline: 2px solid #ffffff00;
  background-color: var(--background-color-1);
  color: var(--font-color-primary);
  font-size: 18px;
  padding-left: 10px;
  padding-right: 10px;
  transition: outline-color 0.3s ease;
}

.add-proxy input:focus,
.add-proxy select:focus {
  outline: 2px solid var(--font-color-secondary);
}

.add-proxy input:not(:focus)[data-valid="false"] {
  outline: 2px solid var(--red);
}

.add-proxy input:not(:focus)[data-valid="true"] {
  outline: 2px solid var(--green);
}

.add-proxy input[type="text"] {
  max-width: 150px;
}

.opened-proxies {
  margin-top: 20px;
  background-color: var(--background-color-2);
  width: 100%;
  height: max-content;
  color: var(--font-color-primary);
  font-size: 20px;
  border-radius: 20px;
  padding-left: 20px;
}

.opened-proxies-row {
  height: 60px;
}

.open-proxies-head,
.open-proxies-data {
  padding-left: 10px;
  text-align: left;
}

.close-proxy-button {
  stroke: var(--font-color-black);
  width: 30px;
  height: 30px;
  background-color: var(--red);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-proxy-button svg {
  width: 25px;
  height: 25px;
}
</style>
