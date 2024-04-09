<script setup>

import { ref, shallowRef } from "vue";

const props = defineProps({
  session: String,
})

const optionsGroups = shallowRef([
  {
    id: "basic_options",
    name: "基本设置",
    options: [
      "name",
      "url",
      "type"
    ]
  },
  {
    id: "php_webshell_options",
    name: "PHP Webshell 配置",
    options: [
      "method",
      "password"
    ]
  }
])

const options = shallowRef([
  {
    id: "name",
    name: "Webshell名称",
    type: "text",
    placeholder: "xxx",
    value: ""
  },
  {
    id: "url",
    name: "Webshell地址",
    type: "text",
    placeholder: "http://xxx.com",
    value: ""
  },
  {
    id: "type",
    name: "Webshell类型",
    type: "select",
    value: "",
    alternatives: [
      {
        name: "PHP一句话",
        value: "PHP_ONELINE"
      }
    ]
  },
  {
    id: "method",
    name: "Webshell请求方式",
    type: "select",
    value: "POST",
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
    value: ""
  },
])

function getOption(id) {
  let optionFound = options.value.filter(option => option.id == id)
  if (optionFound.length == 0) {
    throw Error(`Option ${id} not found`)
  }
  if (optionFound.length > 1) {
    throw Error(`There's multiple options for ${id}`)
  }
  return optionFound[0]
}

console.log(props.session)

</script>

<template>
  <div class="option-group" v-for="group in optionsGroups">
    <p class="group-title">
      {{ group.name }}
    </p>
    <div class="option" v-for="optionId in group.options">
      <div class="option-name">
        {{ getOption(optionId).name }}
      </div>
      <input :type="getOption(optionId).type" :placeholder="getOption(optionId).placeholder"
        v-if="getOption(optionId).type == 'text'">
      <select v-else-if="getOption(optionId).type == 'select'" name="optionId" id="'option-'+optionId">
        <option v-for="alternative in getOption(optionId).alternatives" :value="alternative.value">
          {{ alternative.name }}
        </option>
      </select>
      <p v-else>Not Supported</p>
    </div>
  </div>
</template>

<style scoped>
.option-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
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

.option input {
  height: 40px;
  min-width: 200px;
  border-radius: 8px;
  flex-grow: 1;
  font-size: 20px;
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

}


input {
  background-color: #00000015;
  border: none;
  outline: none;
  color: var(--font-color-white);

}
</style>
