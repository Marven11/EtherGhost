<script setup>
import { store } from '@/assets/store';
import { addPopup, postDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';


const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
} else {
  alert("未知错误：没有选中session")
}

const host = ref("");
const port = ref("");

async function doConnect() {
  if (!/\d+/.test(port.value)) {
    addPopup("red", "端口填写错误", "端口号不是一个数字")
    return
  }
  addPopup("blue", "执行成功时连接会超时", "反弹Shell会阻塞当前进程，导致提示连接超时，忽略即可")


  const result = postDataOrPopupError(`/session/${store.session}/open_reverse_shell`, {
    host: host.value,
    port: port.value,
  })
  console.log("请求发送完毕")
}

</script>

<template>
  <div class="main">
    <div class="panel shadow-box">
      <div class="panel-line">
        <h2>打开反弹Shell</h2>
      </div>
      <div class="panel-line">
        <p>IP或域名</p>
        <input type="text" placeholder="x.x.x.x" v-model="host">
      </div>
      <div class="panel-line">
        <p>端口号</p>
        <input type="text" placeholder="8080" v-model="port">
      </div>
      <div class="panel-line">
        <input type="button" class="button" value="连接" @click="doConnect">
      </div>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.panel {
  width: 40%;
  border-radius: 20px;
  background-color: var(--background-color-2);
  padding: 20px;
  color: var(--font-color-primary);
}

.panel-line {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
}

.panel-line h2,
.panel-line p {
  margin: 0;
}

.panel-line input[type="text"] {
  margin-left: 10px;
  padding: 1rem;
  flex-grow: 1;
  height: 2rem;
  background-color: var(--background-color-3);
  border-radius: 20px;
  outline: none;
  border: none;
  color: var(--font-color-primary);
  font-size: 1rem;
}
</style>