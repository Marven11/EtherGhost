<script setup>
import { ref, shallowRef, reactive } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup, doAssert } from "@/assets/utils"
import GroupedForm from "@/components/GroupedForm.vue"
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
      if (option.default_value !== undefined && option.default_value !== null) {
        optionValues[option.id] = option.default_value
      }
    }
  }
}

async function fetchSupportedSessionTypes() {
  const sessionTypes = await getDataOrPopupError("/sessiontype")
  let optionIdx = basicOptionGroup.options.findIndex(option => option.id == 'session_type')
  basicOptionGroup.options[optionIdx].alternatives = sessionTypes.map(sessionType => {
    return {
      name: sessionType.name,
      value: sessionType.id
    }
  })
}

async function fetchCurrentSession() {
  const session = await getDataOrPopupError(`/session/${props.session}`)
  await updateOption(session.session_type)
  for (const group of optionsGroups.value) {
    for (const option of group.options) {
      doAssert(["text", "checkbox", "select"].includes(option.type), "内部错误：没有这类选项")
      if (["name", "session_type", "note"].includes(option.id)) {
        optionValues[option.id] = session[option.id]
      } else if (session.connection[option.id] !== undefined && session.connection[option.id] !== null) {
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
      if (optionValues[option.id] === undefined || optionValues[option.id] == null) {
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
  if (!session) return;
  let data = await postDataOrPopupError("/test_webshell", session)
  if (!data.success) {
    addPopup("red", "测试失败", data.msg)
  } else {
    addPopup("green", "测试成功", data.msg)
  }
}

async function saveSession() {
  let session = getCurrentSession()
  if (!session) return;
  let sessionId = await postDataOrPopupError("/update_webshell", session)
  if (!sessionId) {
    addPopup("red", "保存失败", "保存webshell到本地数据库失败")
  } else {
    addPopup("green", "保存成功", "保存webshell到本地数据库成功")
    let sessionInfo = await getDataOrPopupError(`/session/${sessionId}/`)
    store.sessionName = sessionInfo.name
    setTimeout(() => {
      router.push("/")
    }, 1000);
  }
}

function onUpdateOption(optionId, value) {
  optionValues[optionId] = value
  // If session_type changes, reload options
  if (optionId === "session_type") {
    updateOption(value)
  }
}

const buttons = [
  { label: "丢弃" },
  { label: "保存" },
  { label: "测试" }
]

function onButtonClick(button) {
  if (button.label === "丢弃") {
    router.go(-1)
  } else if (button.label === "保存") {
    saveSession()
  } else if (button.label === "测试") {
    testSession()
  }
}

setTimeout(async () => {
  await fetchSupportedSessionTypes();
  if (props.session) {
    await fetchCurrentSession()
  } else {
    await updateOption("ONELINE_PHP")
  }
}, 0)
</script>

<template>
  <GroupedForm
    :groups="optionsGroups"
    :modelValue="optionValues"
    @update:modelValue="onUpdateOption"
    :buttons="buttons"
    @button-click="onButtonClick"
  />
</template>
