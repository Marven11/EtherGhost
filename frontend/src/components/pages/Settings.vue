<script setup>

import { ref, shallowRef } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup } from "@/assets/utils"
import IconCross from '../icons/iconCross.vue'
import IconCheck from '../icons/iconCheck.vue'
import { store, currentSettings } from "@/assets/store";
import { useRouter } from "vue-router"

const router = useRouter()
const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const userInterfaceOptionGroup = {
  name: "界面配置",
  options: [
    // {
    //   id: "name",
    //   name: "名称",
    //   type: "text",
    //   placeholder: "xxx",
    //   default_value: undefined
    // },
    {
      id: "theme",
      name: "主题色",
      type: "select",
      default_value: store.theme,
      alternatives: [
        {
          name: "灰白色",
          value: "white"
        },
        {
          name: "红色",
          value: "red"
        },
        {
          name: "黄色",
          value: "yellow"
        },
        {
          name: "绿色",
          value: "green"
        },
        {
          name: "蓝色",
          value: "blue"
        },
        {
          name: "玻璃",
          value: "glass"
        },
      ]
    },
  ]
}

const connectionOptionGroup = {
  name: "连接配置",
  options: [
    {
      id: "proxy",
      name: "代理",
      type: "text",
      placeholder: "http://127.0.0.1:7890",
      default_value: "",
    }
  ]
}

const othersOptionGroup = {
  name: "其他配置",
  options: [
    {
      id: "filesizeUnit",
      name: "文件大小单位",
      type: "select",
      default_value: 1024,
      alternatives: [
        {
          name: "KiB, MiB...",
          value: 1024
        },
        {
          name: "KB, MB...",
          value: 1000
        },
      ]
    },
  ]
}

const optionsGroups = shallowRef([userInterfaceOptionGroup, connectionOptionGroup, othersOptionGroup])

function changeClickboxOption(optionId) {
  currentSettings[optionId] = !currentSettings[optionId]
}

async function saveSettings() {
  let settings = { ...currentSettings }
  console.log(settings)
  await postDataOrPopupError("/settings", settings)
  addPopup("green", "保存成功", "新的设置已经保存到本地数据库")
}

// actions

const testProxySite = ref("apple")

async function onTestProxy() {
  const data = await getDataOrPopupError("/utils/test_proxy", {
    params: {
      proxy: currentSettings.proxy,
      site: testProxySite.value
    }
  })
  if (data) {
    addPopup("green", "代理测试成功", `可以连接到${testProxySite.value}服务器`)
  } else {
    addPopup("yellow", "代理测试失败", `不可以连接到${testProxySite.value}服务器`)
  }
}

</script>

<template>
  <div class="option-group" v-for="group in optionsGroups">
    <p class="group-title shadow-box">
      {{ group.name }}
    </p>
    <div class="options">
      <div class="option" v-for="option in group.options">
        <div class="option-name">
          {{ option.name }}
        </div>
        <input v-if="option.type == 'text'" :type="option.type" :name="option.id" v-model="currentSettings[option.id]"
          :placeholder="option.placeholder" :id="'option-' + option.id">
        <select v-else-if="option.type == 'select'" :name="option.id" :id="'option-' + option.id"
          v-model="currentSettings[option.id]">
          <option disabled value="">选择一个</option>
          <option v-for="alternative in option.alternatives" :value="alternative.value">
            {{ alternative.name }}
          </option>
        </select>
        <div v-else-if="option.type == 'checkbox'" class="input-checkbox" :id="'option-' + option.id"
          :checked="currentSettings[option.id]" @click="changeClickboxOption(option.id)">
          <input type="hidden" :name="option.id" :id="'option-' + option.id" v-model="currentSettings[option.id]">
          <IconCheck v-if="currentSettings[option.id]" />
          <IconCross v-else />
        </div>
        <p v-else>内部错误：未知选项类型 {{ option.type }}</p>
      </div>
    </div>
  </div>
  <div class="submit-buttons shadow-box">
    <div class="submit-button" @click="() => router.go(-1)">
      丢弃
    </div>
    <div class="submit-button" @click="saveSettings">
      保存
    </div>
  </div>
  <div class="actions shadow-box">
    <button class="button" @click="onTestProxy">测试代理</button>
    <select name="testProxySites" id="testProxySites" v-model="testProxySite">
      <option value="apple">苹果服务器</option>
      <option value="google">谷歌服务器</option>
      <option value="cloudflare">CloudFlare服务器</option>
      <option value="microsoft">微软服务器</option>
      <option value="huawei">华为服务器</option>
      <option value="xiaomi">小米服务器</option>
    </select>
  </div>
</template>

<style scoped>
.option-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
  width: 60%;
  margin-left: 20%;
  margin-right: 20%;
}

.group-title {
  background-color: var(--background-color-2);
  color: var(--font-color-primary);
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0;
  padding-top: 20px;
  padding-bottom: 20px;
  border-radius: 20px;
  margin-bottom: 10px;
}

.options {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

body[data-theme="glass"] .options {
  border-radius: 20px;
  background-color: #00000015;
  backdrop-filter: blur(20px);
  padding: 10px 20px;
  margin-top: 5px;
}


.option {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: start;
  color: var(--font-color-primary);
  height: 50px;
  font-size: 20px;
}

.option-name {
  margin-right: 20px;
}

.option input[type="text"] {
  height: 40px;
  min-width: 200px;
  border-radius: 8px;
  flex-grow: 1;
  font-size: 20px;
  text-indent: 10px;
}

.option select {
  background-color: #00000015;
  outline: none;
  border: none;
  border-radius: 8px;
  color: var(--font-color-primary);
  height: 40px;
  min-width: 100px;
  font-size: 16px;
  padding-left: 10px;
}


input {
  background-color: #00000015;
  border: none;
  outline: none;
  color: var(--font-color-primary);
}

.input-checkbox {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background-color: #00000015;
  outline: 2px dashed var(--font-color-secondary);
  stroke: var(--font-color-secondary);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: background 0.3s ease;
}

.input-checkbox:hover {
  background-color: #ffffff15;
}

.input-checkbox[checked=true] {
  background-color: var(--font-color-primary);
  stroke: var(--font-color-secondary);
}

.input-checkbox svg {
  width: 20px;
  height: 20px;
}

.submit-buttons {
  height: 100px;
  width: 60%;
  border-radius: 20px;
  margin-left: 20%;
  margin-right: 20%;
  background-color: var(--background-color-2);
  display: flex;
  align-items: center;
  justify-content: space-around;
  user-select: none;
}

.submit-button {
  height: 60%;
  width: 30%;
  margin-left: 20px;
  margin-right: 20px;
  border-radius: 12px;

  background-color: var(--background-color-3);
  color: var(--font-color-primary);
  outline: 2px dashed var(--font-color-secondary);
  font-size: 20px;

  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease;
}

.submit-button:hover {
  background-color: color-mix(in lch, rgb(255, 255, 255) 10%, var(--background-color-3));
}


.actions {
  width: 60%;
  margin-top: 20px;
  margin-left: 20%;
  margin-right: 20%;
  height: 70px;
  background-color: var(--background-color-2);
  border-radius: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: left;
  padding-left: 5%;
  padding-right: 5%;
}

.actions button,
.actions input {
  height: 50%;
}

.actions select {
  height: 50%;
  min-width: 50px;
  border-radius: 20px;
  border: none;
  outline: 2px solid #ffffff00;
  background-color: var(--background-color-3);
  color: var(--font-color-primary);
  font-size: 18px;
  padding-left: 10px;
  padding-right: 10px;
  transition: outline-color 0.3s ease;
}
</style>
