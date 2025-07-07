<script setup>
import { ref, shallowRef, reactive } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup, doAssert } from "@/assets/utils"
import GroupedForm from "@/components/GroupedForm.vue"
import { store } from "@/assets/store";
import { useRouter } from "vue-router"

const router = useRouter()
const props = defineProps({
  connector: String,
})

if (props.connector) {
  store.connector = props.connector
}

const basicOptionGroup = {
  name: "基本配置",
  options: [
    {
      id: "name",
      name: "名称",
      type: "text",
      placeholder: "连接器名称",
      default_value: undefined
    },
    {
      id: "note",
      name: "备注",
      type: "text",
      placeholder: "连接器备注信息...",
      default_value: "并没有备注"
    },
    {
      id: "connector_type",
      name: "类型",
      type: "select",
      default_value: undefined,
      alternatives: []
    },
    {
      id: "autostart",
      name: "自动随着主程序启动",
      type: "checkbox",
      default_value: false
    }
  ]
}

const optionValues = reactive({
  name: "",
  connector_type: "",
  note: "并没有备注",
  autostart: false
})
const optionsGroups = shallowRef([])

async function updateOption(connectorType) {
  let options = await getDataOrPopupError(`/connectortype/${connectorType}/conn_options`)
  optionsGroups.value = [basicOptionGroup, ...options]
  for (let group of optionsGroups.value) {
    for (let option of group.options) {
      if (option.default_value !== undefined && option.default_value !== null) {
        optionValues[option.id] = option.default_value
      }
    }
  }
}

async function fetchSupportedConnectorTypes() {
  const data = await getDataOrPopupError("/connectortype")
  let optionIdx = basicOptionGroup.options.findIndex(option => option.id == 'connector_type')
  basicOptionGroup.options[optionIdx].alternatives = data.map(connectorType => {
    return {
      name: connectorType.name,
      value: connectorType.type
    }
  })
}

async function fetchCurrentConnector() {
  const connector = await getDataOrPopupError(`/connector/${props.connector}`)
  await updateOption(connector.connector_type)
  for (const group of optionsGroups.value) {
    for (const option of group.options) {
      doAssert(["text", "checkbox", "select"].includes(option.type), "内部错误：没有这类选项")
      if (["name", "connector_type", "note", "autostart"].includes(option.id)) {
        optionValues[option.id] = connector[option.id]
      } else if (connector.connection[option.id] !== undefined && connector.connection[option.id] !== null) {
        optionValues[option.id] = connector.connection[option.id]
      }
    }
  }
}

function getCurrentConnector() {
  let connector = { connection: {} }
  if (!optionValues["connector_type"]) {
    return undefined;
  }
  for (const group of optionsGroups.value) {
    for (const option of group.options) {
      doAssert(["text", "checkbox", "select"].includes(option.type), "内部错误：没有这类选项")
      if (optionValues[option.id] === undefined || optionValues[option.id] == null) {
        if (option.type !== "checkbox") {
          addPopup("red", `选项${option.name}未填写`, `选项${option.name}仍未填写，无法获取当前配置！`)
          return undefined
        }
      }
      if (["name", "connector_type", "note", "autostart"].includes(option.id)) {
        connector[option.id] = optionValues[option.id]
      } else {
        connector.connection[option.id] = optionValues[option.id]
      }
    }
  }
  if (store.connector) {
    connector.connector_id = store.connector;
  } else {
    // 生成新的 UUID
    connector.connector_id = crypto.randomUUID();
  }
  return connector
}

async function saveConnector() {
  let connector = getCurrentConnector()
  if (!connector) return;
  let result = await postDataOrPopupError("/connector", connector)
  if (!result) {
    addPopup("red", "保存失败", "保存连接器到本地数据库失败")
  } else {
    addPopup("green", "保存成功", `${result.action === 'add' ? '添加' : '更新'}连接器到本地数据库成功`)
    setTimeout(() => {
      router.push("/connector")
    }, 1000);
  }
}

function onUpdateOption(optionId, value) {
  optionValues[optionId] = value
  // If connector_type changes, reload options
  if (optionId === "connector_type") {
    updateOption(value)
  }
}

const buttons = [
  { label: "取消" },
  { label: "保存" },
]

function onButtonClick(button) {
  if (button.label === "取消") {
    router.push("/connector")
  } else if (button.label === "保存") {
    saveConnector()
  }
}

setTimeout(async () => {
  await fetchSupportedConnectorTypes();
  if (props.connector) {
    await fetchCurrentConnector()
  } else {
    // 设置默认连接器类型
    if (basicOptionGroup.options.find(opt => opt.id === 'connector_type').alternatives.length > 0) {
      const defaultType = basicOptionGroup.options.find(opt => opt.id === 'connector_type').alternatives[0].value
      optionValues.connector_type = defaultType
      await updateOption(defaultType)
    }
  }
}, 0)
</script>

<template>
  <GroupedForm :groups="optionsGroups" :modelValue="optionValues" @update:modelValue="onUpdateOption" :buttons="buttons"
    @button-click="onButtonClick" />
</template>
