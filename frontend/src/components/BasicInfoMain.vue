<script setup>
import { store } from '@/assets/store';
import { getCurrentApiUrl, getDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';
import axios from 'axios';

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const infos = ref([

])

async function openPhpInfo() {
  const result = await axios.get(`${getCurrentApiUrl()}/session/${props.session}/download_phpinfo`, { responseType: 'blob' });
  const url = URL.createObjectURL(result.data);
  console.log(url)
  window.open(url, "_blank")
}

async function downloadPhpInfo() {
  window.open(`${getCurrentApiUrl()}/session/${props.session}/download_phpinfo`, "_blank")
}


async function updateInfo() {
  const result = await getDataOrPopupError(`/session/${props.session}/basicinfo`)
  infos.value = result
}

setTimeout(updateInfo, 0)

</script>

<template>
  <div class="actions shadow">
    <button class="action-button" @click="openPhpInfo">
      打开PHPINFO
    </button>
    <button class="action-button" @click="downloadPhpInfo">
      下载PHPINFO
    </button>
    <button class="action-button" @click="updateInfo">
      刷新
    </button>
  </div>
  <div class="info-panel">
    <table class="infos shadow">
      <tr class="info" v-for="[i, info] in infos.entries()">
        <td class="info-data" :data-tail="i != 0">{{ info.key }}</td>
        <td class="info-data" :data-tail="i != 0">{{ info.value }}</td>
      </tr>
    </table>
  </div>
</template>

<style scoped>
.actions {
  width: 100%;
  min-height: 60px;
  border-radius: 20px;
  background-color: var(--background-color-2);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: left;
  padding-left: 20px;
  padding-right: 20px;
}

.action-button {
  min-width: 100px;
  height: 40px;
  border-radius: 20px;
  outline: none;
  border: none;
  background-color: var(--background-color-3);
  color: var(--font-color-white);
  margin-right: 10px;
}

.info-panel {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.infos {
  width: 60%;
  background-color: var(--background-color-2);
  border-radius: 20px;
}

.info {
  height: 60px;
  font-size: 20px;
  color: var(--font-color-white);
}

.info-data {
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 6px;
  padding-bottom: 6px;
}

.info-data[data-tail="true"] {
  border-top: 1px solid #ffffff15;
}
</style>