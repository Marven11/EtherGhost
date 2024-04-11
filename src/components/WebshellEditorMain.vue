<script setup>

import { reactive, ref, shallowRef } from "vue";
import axios from "axios"
import { getCurrentApiUrl, requestDataOrPopupError } from "@/assets/utils"
import IconCross from './icons/iconCross.vue'
import IconCheck from './icons/iconCheck.vue'
import Popups from './Popups.vue'

const props = defineProps({
  session: String,
})


const webshellTypes = [
  "ONELINE_PHP"
]

const webshellOptionGroups = {
  ONELINE_PHP: [
    {
      id: "basic_options",
      name: "基本设置",
      options: [
        "name",
        "session_type",
        "note"
      ]
    },
    {
      id: "php_webshell_basic_options",
      name: "PHP Webshell 基本配置",
      options: [
        "url",
        "method",
        "password",
      ]
    },
    {
      id: "php_webshell_advanced_options",
      name: "PHP Webshell 高级配置",
      options: [
        "encoder",
        "http_params_obfs",
        "sessionize_payload"
      ]
    },
  ]
}

const currentWebshellType = ref(null)


const optionsGroups = shallowRef([])

const options = reactive([
  {
    id: "name",
    name: "名称",
    type: "text",
    placeholder: "xxx",
    value: undefined
  },
  {
    id: "url",
    name: "地址",
    type: "text",
    placeholder: "http://xxx.com",
    value: undefined
  },
  {
    id: "note",
    name: "备注",
    type: "text",
    placeholder: "xxx...",
    value: undefined
  },
  {
    id: "session_type",
    name: "类型",
    type: "select",
    value: undefined,
    alternatives: [
      {
        name: "PHP一句话",
        value: "ONELINE_PHP"
      }
    ]
  },
  {
    id: "method",
    name: "Webshell请求方式",
    type: "select",
    value: undefined,
    alternatives: [
      {
        name: "POST",
        value: "POST"
      },
      {
        name: "GET",
        value: "GET"
      },
    ]
  },
  {
    id: "password",
    name: "Webshell密码",
    type: "text",
    placeholder: "data",
    value: undefined
  },
  {
    id: "encoder",
    name: "类型",
    type: "select",
    value: undefined,
    alternatives: [
      {
        name: "base64",
        value: "base64"
      }
    ]
  },
  {
    id: "http_params_obfs",
    name: "HTTP参数混淆",
    type: "checkbox",
    value: true,
  },
  {
    id: "sessionize_payload",
    name: "Session暂存payload",
    type: "checkbox",
    value: false,
  },

])

const popupsRef = ref(null)

function updateOption(webshellType) {
  currentWebshellType.value = webshellType
  optionsGroups.value = webshellOptionGroups[webshellType]
}

function getOption(id) {
  let optionFound = options.filter(option => option.id == id)
  if (optionFound.length == 0) {
    throw Error(`Option ${id} not found`)
  }
  if (optionFound.length > 1) {
    throw Error(`There's multiple options for ${id}`)
  }
  return optionFound[0]
}

function changeClickboxOption(optionId) {
  getOption(optionId).value = !getOption(optionId).value
}

async function fetchCurrentSession() {
  const session = await requestDataOrPopupError(`/session/${props.session}`, popupsRef)

  updateOption(session.session_type)
  for (const key of ["name", "session_type", "note"]) {
    const option = getOption(key)
    if (["text", "checkbox"].includes(option.type)) {
      option.value = session[key]
    } else if (option.type == "select") {
      option.value = session[key]
      console.log(option)
    }
  }
  for (const key of Object.keys(session.connection)) {
    const option = getOption(key)
    if (["text", "checkbox"].includes(option.type)) {
      option.value = session.connection[key]
    } else if (option.type == "select") {
      option.value = session.connection[key]
      console.log(option)
    }
  }
}

setTimeout(() => {
  if (props.session) {
    fetchCurrentSession(props.session)
  } else {
    updateOption("ONELINE_PHP")
  }
}, 0)

</script>

<template>
  <div class="option-group" v-for="group in optionsGroups">
    <p class="group-title">
      {{ group.name }}
    </p>
    <div class="option" v-for="option in group.options.map(getOption)">
      <div class="option-name">
        {{ option.name }}
      </div>
      <input v-if="option.type == 'text'" :type="option.type" :name="option.id" v-model="option.value"
        :placeholder="option.placeholder" :id="'option-' + option.id">
      <select v-else-if="option.type == 'select'" :name="option.id" :id="'option-' + option.id" v-model="option.value">
        <option disabled value="">选择一个</option>
        <option v-for="alternative in option.alternatives" :value="alternative.value">
          {{ alternative.name }}
        </option>
      </select>
      <div v-else-if="option.type == 'checkbox'" class="input-checkbox" :id="'option-' + option.id"
        :checked="option.value" @click="changeClickboxOption(option.id)">
        <input type="hidden" :name="option.id" :id="'option-' + option.id" v-model="option.value">
        <IconCheck v-if="option.value" />
        <IconCross v-else />
      </div>
      <p v-else>内部错误：未知选项类型 {{ option.type }}</p>
    </div>
  </div>
  <div class="submit-buttons">
    <div class="submit-button">
      丢弃
    </div>
    <div class="submit-button">
      保存
    </div>
    <div class="submit-button">
      测试
    </div>
  </div>
  <Popups ref="popupsRef" />
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
  color: var(--font-color-white);
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

.option {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: start;
  color: var(--font-color-white);
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
  color: var(--font-color-white);
  height: 40px;
  min-width: 100px;
  font-size: 16px;
  padding-left: 10px;
}


input {
  background-color: #00000015;
  border: none;
  outline: none;
  color: var(--font-color-white);
}

.input-checkbox {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background-color: #00000015;
  outline: 2px dashed var(--font-color-grey);
  stroke: var(--font-color-grey);
  display: flex;
  justify-content: center;
  align-items: center;
}

.input-checkbox:hover {
  background-color: #ffffff15;
}

.input-checkbox[checked=true] {
  background-color: var(--font-color-white);
  stroke: var(--font-color-grey);
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
  color: var(--font-color-white);
  outline: 2px dashed var(--font-color-grey);
  font-size: 20px;

  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-button:hover {
  background-color: color-mix(in lch, rgb(255, 255, 255) 10%, var(--background-color-3));
}
</style>
