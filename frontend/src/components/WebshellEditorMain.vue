<script setup>

import { reactive, ref, shallowRef, watch } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup, doAssert } from "@/assets/utils"
import IconCross from './icons/iconCross.vue'
import IconCheck from './icons/iconCheck.vue'
import { store } from "@/assets/store";
import { useRouter } from "vue-router"

const router = useRouter()
const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const basicOptionGroup = {
  name: "基本配置",
  options: [
    {
      id: "name",
      name: "名称",
      type: "text",
      placeholder: "xxx",
      default_value: undefined
    },
    {
      id: "note",
      name: "备注",
      type: "text",
      placeholder: "xxx...",
      default_value: "并没有备注"
    },
    {
      id: "session_type",
      name: "类型",
      type: "select",
      default_value: undefined,
      alternatives: [
        {
          name: "一句话PHP",
          value: "ONELINE_PHP"
        },
        {
          name: "冰蝎AES",
          value: "BEHINDER_PHP_AES"
        },
        {
          name: "冰蝎XOR",
          value: "BEHINDER_PHP_XOR"
        },
      ]
    },
  ]
}

const optionValues = reactive({
  name: "",
  session_type: "ONELINE_PHP"
})
const optionsGroups = shallowRef([])


async function updateOption(sessionType) {
  let options = await getDataOrPopupError(`/sessiontype/${sessionType}/conn_options`)
  optionsGroups.value = [basicOptionGroup, ...options]
  for (let group of optionsGroups.value) {
    for (let option of group.options) {
      if(option.default_value !== undefined) {
        optionValues[option.id] = option.default_value
      }
    }
  }
}

function changeClickboxOption(optionId) {
  optionValues[optionId] = !optionValues[optionId]
}

async function fetchCurrentSession() {
  const session = await getDataOrPopupError(`/session/${props.session}`)

  await updateOption(session.session_type)
  for (const group of optionsGroups.value) {
    for (const option of group.options) {
      doAssert(["text", "checkbox", "select"].includes(option.type), "内部错误：没有这类选项")
      if (["name", "session_type", "note"].includes(option.id)) {
        optionValues[option.id] = session[option.id]
      } else {
        optionValues[option.id] = session.connection[option.id]
      }
    }
  }


}

function getCurrentSession() {
  let session = { connection: {} }
  if (!optionValues["session_type"]) {
    return undefined;
  }

  for (const group of optionsGroups.value) {
    for (const option of group.options) {
      doAssert(["text", "checkbox", "select"].includes(option.type), "内部错误：没有这类选项")
      if (optionValues[option.id] == undefined) {
        addPopup("red", `选项${option.name}未填写`, `选项${option.name}仍未填写，无法获取当前配置！`)
        return undefined
      }
      if (["name", "session_type", "note"].includes(option.id)) {
        session[option.id] = optionValues[option.id]
      } else {
        session.connection[option.id] = optionValues[option.id]
      }
    }
  }
  if (store.session) {
    session.session_id = store.session;
  }
  return session
}


async function testSession() {
  let session = getCurrentSession()
  if (!session) {
    return;
  }
  let data = await postDataOrPopupError("/test_webshell", session)
  if (!data.success) {
    addPopup("red", "测试失败", data.msg)
  } else {
    addPopup("green", "测试成功", data.msg)
  }
}

async function saveSession() {
  let session = getCurrentSession()
  if (!session) {
    return;
  }
  let data = await postDataOrPopupError("/update_webshell", session)
  if (!data) {
    addPopup("red", "保存失败", "保存webshell到本地数据库失败")
  } else {
    addPopup("green", "保存成功", "保存webshell到本地数据库成功")
    setTimeout(() => {
      router.push("/")
    }, 1000);
  }

}

setTimeout(async () => {
  if (props.session) {
    await fetchCurrentSession(props.session)
  } else {
    updateOption("ONELINE_PHP")
  }
}, 0)

watch(
  () => optionValues.session_type,
  (newValue, oldValue) => {
    if(newValue == oldValue) {
      return
    }
    console.log(newValue)
    updateOption(newValue)
  }
)

</script>

<template>
  <div class="option-group" v-for="group in optionsGroups">
    <p class="group-title">
      {{ group.name }}
    </p>
    <div class="option" v-for="option in group.options">
      <div class="option-name">
        {{ option.name }}
      </div>
      <input v-if="option.type == 'text'" :type="option.type" :name="option.id" v-model="optionValues[option.id]"
        :placeholder="option.placeholder" :id="'option-' + option.id">
      <select v-else-if="option.type == 'select'" :name="option.id" :id="'option-' + option.id"
        v-model="optionValues[option.id]">
        <option disabled value="">选择一个</option>
        <option v-for="alternative in option.alternatives" :value="alternative.value">
          {{ alternative.name }}
        </option>
      </select>
      <div v-else-if="option.type == 'checkbox'" class="input-checkbox" :id="'option-' + option.id"
        :checked="optionValues[option.id]" @click="changeClickboxOption(option.id)">
        <input type="hidden" :name="option.id" :id="'option-' + option.id" v-model="optionValues[option.id]">
        <IconCheck v-if="optionValues[option.id]" />
        <IconCross v-else />
      </div>
      <p v-else>内部错误：未知选项类型 {{ option.type }}</p>
    </div>
  </div>
  <div class="submit-buttons">
    <div class="submit-button" @click="() => router.go(-1)">
      丢弃
    </div>
    <div class="submit-button" @click="saveSession">
      保存
    </div>
    <div class="submit-button" @click="testSession">
      测试
    </div>
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
