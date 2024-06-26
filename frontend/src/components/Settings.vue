<script setup>

import { reactive, ref, shallowRef, watch } from "vue";
import { getDataOrPopupError, postDataOrPopupError, addPopup, doAssert } from "@/assets/utils"
import IconCross from './icons/iconCross.vue'
import IconCheck from './icons/iconCheck.vue'
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
      ]
    },
  ]
}


const optionsGroups = shallowRef([userInterfaceOptionGroup])

function changeClickboxOption(optionId) {
  currentSettings[optionId] = !currentSettings[optionId]
}

async function saveSettings() {
  let settings = { ...currentSettings }
  console.log(settings)
  await postDataOrPopupError("/settings", settings)
  addPopup("green", "保存成功", "新的设置已经保存到本地数据库")
}

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
  <div class="submit-buttons">
    <div class="submit-button" @click="() => router.go(-1)">
      丢弃
    </div>
    <div class="submit-button" @click="saveSettings">
      保存
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
  transition: background 0.3s ease;
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
  transition: opacity 0.3s ease;
}

.submit-button:hover {
  background-color: color-mix(in lch, rgb(255, 255, 255) 10%, var(--background-color-3));
}
</style>
