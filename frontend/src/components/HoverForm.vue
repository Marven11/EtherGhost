<script setup>
import { ref } from 'vue';

const props = defineProps(["callback", "title"])

const emit = defineEmits(["result"])
const form = ref(null)

function onClickConfirm(event) {
  event.preventDefault()
  let formData = Object.fromEntries(new FormData(form.value))
  console.log(form.value)
  props.callback(formData)
}

function onClickCancel(event) {
  event.preventDefault()
  props.callback(undefined)
}

function onClickBackground(event) {
  event.preventDefault()
  let target = event.target
  while (target) {
    if (target.classList.contains("input-box")) {
      return;
    }
    target = target.parentElement
  }

}

</script>

<template>
  <div class="input-box-main" @click.self="onClickBackground">
    <div class="input-box">
      <h1 class="input-box-title">{{ props.title }}</h1>
      <form action="" class="input-box-form" ref="form">
        <slot></slot>
        <div class="input-box-line">
          <input class="input-box-button" type="button" value="取消" @click="onClickCancel">
          <input class="input-box-button" type="button" value="确认" @click="onClickConfirm">
        </div>
      </form>
    </div>
  </div>
</template>

<style>
.input-box-main {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background-color: #00000030;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-box-main .input-box {
  width: 50%;
  background-color: var(--background-color-1);
  color: var(--font-color-grey);
  border-radius: 20px;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.input-box-main .input-box-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-box-main .input-box-title {
  color: var(--font-color-white);
  margin: 0;
  margin-top: 20px;
}

.input-box-main .input-box-line {
  display: flex;
  flex-direction: row;
  height: 100px;
  width: 80%;
  align-items: center;
  justify-content: space-evenly;
}

.input-box-main .input-box-line p {
  font-size: 20px;
  color: var(--font-color-white);
  margin-left: 20px;
  margin-right: 20px;
}

.input-box-main .input-box input,
.input-box-main .input-box select,
.input-box-main .input-file {
  transition: background 0.3s ease;
  background-color: var(--background-color-2);
}

.input-box-main .input-file {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
  width: 50%;
  height: 50px;
  border: none;
  border-radius: 20px;
}

.input-box-main .input-box input[type="text"] {
  height: 50px;
  width: 50%;
  outline: none;
  border: none;
  border-radius: 20px;
  color: var(--font-color-white);
  font-size: 20px;
  padding-left: 10px;
  padding-right: 10px;
}

.input-box-main .input-box input[type="button"] {
  height: 50px;
  width: 100px;
  outline: 2px dashed var(--font-color-grey);
  border: none;
  border-radius: 20px;
  color: var(--font-color-white);
  font-size: 16px;
}

.input-box-main .input-box input[type="button"]:hover {
  background-color: #ffffff15;
}
</style>
