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
    if (target.classList.contains("hover-form")) {
      return;
    }
    target = target.parentElement
  }

}

</script>

<template>
  <div class="hover-form-main" @click.self="onClickBackground">
    <div class="hover-form">
      <h1 class="hover-form-title">{{ props.title }}</h1>
      <form action="" class="hover-form-form" ref="form">
        <slot></slot>
        <div class="hover-form-line">
          <input class="hover-form-button" type="button" value="取消" @click="onClickCancel">
          <input class="hover-form-button" type="button" value="确认" @click="onClickConfirm">
        </div>
      </form>
    </div>
  </div>
</template>

<style>
.hover-form-main {
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

.hover-form-main .hover-form {
  width: 30%;
  min-width: 500px;
  background-color: var(--background-color-1);
  color: var(--font-color-secodary);
  border-radius: 20px;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.hover-form-main .hover-form-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hover-form-main .hover-form-title {
  color: var(--font-color-primary);
  margin: 0;
  margin-top: 20px;
}

.hover-form-main .hover-form-line {
  display: flex;
  flex-direction: row;
  height: 100px;
  width: 80%;
  align-items: center;
  justify-content: space-evenly;
}

.hover-form-main .hover-form-line p {
  font-size: 20px;
  color: var(--font-color-primary);
  margin-left: 20px;
  margin-right: 20px;
}

.hover-form-main .hover-form input,
.hover-form-main .hover-form select,
.hover-form-main .input-file {
  transition: background 0.3s ease;
  background-color: var(--background-color-2);
}

.hover-form-main .input-file {
  background-color: var(--background-color-2);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80%;
  height: 60px;
  border: none;
  border-radius: 20px;
}

.hover-form-main .input-file input {
  height: 60%;
}

.hover-form-main .input-file input::file-selector-button {
  background-color: var(--font-color-primary);
  border-radius: 20px;
  padding-left: 10px;
  padding-right: 10px;
  height: 100%;
  outline: none;
  border: none
}

.hover-form-main .hover-form input[type="text"] {
  height: 50px;
  width: 50%;
  outline: none;
  border: none;
  border-radius: 20px;
  color: var(--font-color-primary);
  font-size: 20px;
  padding-left: 10px;
  padding-right: 10px;
}

.hover-form-main .hover-form input[type="button"] {
  height: 50px;
  width: 100px;
  outline: 2px dashed var(--font-color-secodary);
  border: none;
  border-radius: 20px;
  color: var(--font-color-primary);
  font-size: 16px;
  transition: background 0.3s ease;
}

.hover-form-main .hover-form input[type="button"]:hover {
  background-color: #ffffff15;
}
</style>
