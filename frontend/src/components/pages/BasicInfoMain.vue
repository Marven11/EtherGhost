<script setup>
import { store } from '@/assets/store';
import { addPopup, getCurrentApiUrl, getDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';
import axios from 'axios';
import sanitizeHtml from 'sanitize-html';

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const infos = ref([

])

async function openPhpInfo() {
  addPopup("yellow", "显示可能有问题", "为了阻止XSS漏洞，打开的phpinfo html会被清理，导致某些元素显示不正常")
  const result = await axios.get(`${getCurrentApiUrl()}/session/${props.session}/download_phpinfo`);
  const style = `
  <style type="text/css">
body {background-color: #fff; color: #222; font-family: sans-serif;}
pre {margin: 0; font-family: monospace;}
a:link {color: #009; text-decoration: none; background-color: #fff;}
a:hover {text-decoration: underline;}
table {border-collapse: collapse; border: 0; width: 934px; box-shadow: 1px 2px 3px #ccc;}
.center {text-align: center;}
.center table {margin: 1em auto; text-align: left;}
.center th {text-align: center !important;}
td, th {border: 1px solid #666; font-size: 75%; vertical-align: baseline; padding: 4px 5px;}
th {position: sticky; top: 0; background: inherit;}
h1 {font-size: 150%;}
h2 {font-size: 125%;}
.p {text-align: left;}
.e {background-color: #ccf; width: 300px; font-weight: bold;}
.h {background-color: #99c; font-weight: bold;}
.v {background-color: #ddd; max-width: 300px; overflow-x: auto; word-wrap: break-word;}
.v i {color: #999;}
img {float: right; border: 0;}
hr {width: 934px; background-color: #ccc; border: 0; height: 1px;}
</style>
  `
  const url = URL.createObjectURL(new Blob([style + sanitizeHtml(result.data, {
    allowedAttributes: {
      'div': ['class'],
      'td': ['class'],
      'tr': ['class'],
    },
  })], { type: 'text/html' }));
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
  <div class="actions shadow-box">
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
    <table class="infos shadow-box">
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
  color: var(--font-color-primary);
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
  color: var(--font-color-primary);
}

.info-data {
  padding-left: 20px;
  padding-right: 20px;
  padding-top: 6px;
  padding-bottom: 6px;
  min-width: 200px;
  word-wrap: break-word;
  word-break: break-all;
  white-space: normal;

}

.info-data[data-tail="true"] {
  border-top: 1px solid #ffffff15;
}
</style>