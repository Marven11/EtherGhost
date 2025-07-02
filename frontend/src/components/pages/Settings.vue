<script setup>

import { ref, shallowRef } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup } from "@/assets/utils"
import IconCross from '@/components/icons/iconCross.vue'
import IconCheck from '@/components/icons/iconCheck.vue'
import GroupedForm from "@/components/GroupedForm.vue"
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
    {
      id: "fontSize",
      name: "字体大小",
      type: "text",
      placeholder: "单位是pixel",
      default_value: "16",
    }
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

function onUpdateSettings(optionId, value) {
  currentSettings[optionId] = value
}

let buttons = [
  {
    "label": "丢弃",
  },
  {
    "label": "保存",
  }
]

function onButtonClick(button) {
  console.log(button)
  if (button.label == "丢弃") {
    router.go(-1)
  } else if (button.label == "保存") {
    saveSettings()
  }
}

</script>

<template>
  <GroupedForm :groups="optionsGroups" :modelValue="currentSettings" @update:modelValue="onUpdateSettings"
    :buttons="buttons" @button-click="onButtonClick">

  </GroupedForm>

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
  font-size: 1rem;
  padding-left: 10px;
  padding-right: 10px;
  transition: outline-color 0.3s ease;
}
</style>
