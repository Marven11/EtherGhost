<script setup>
import { ref } from 'vue';

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, required: true },
  requireInput: { type: Boolean, required: true },
  value: { type: String, required: false, default: "" },
})

const userInput = ref(props.value)
const emit = defineEmits(["result"])
const inputBox = ref(null)

function onConfirm(event) {
  event.preventDefault()
  if (props.requireInput) {
    emit("result", userInput.value)
  } else {
    emit("result", true)
  }
}

function onCancel(event) {
  event.preventDefault()
  if (props.requireInput) {
    emit("result", undefined)
  } else {
    emit("result", false)
  }
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
  if (props.requireInput) {
    emit("result", undefined)
  } else {
    emit("result", false)
  }
}

</script>

<template>
  <div class="input-box-main" @click="onClickBackground">
    <div class="input-box" ref="inputBox">
      <h1 class="input-box-title">
        {{ props.title }}
      </h1>
      <p class="input-box-note">
        {{ props.note }}
      </p>

      <input v-if="props.requireInput" type="text" class="input-box-input" placeholder="testtest" v-model="userInput"
        @keypress.enter="onConfirm">
      <div class="input-box-buttons">
        <input class="input-box-button" type="button" value="取消" @click="onCancel">
        <input class="input-box-button" type="button" value="确认" @click="onConfirm">
      </div>

    </div>
  </div>
</template>

<style scoped>
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

body[data-theme="glass"] .input-box-main {
  backdrop-filter: blur(20px);
}

.input-box-background {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
}

.input-box {
  width: 30%;
  min-width: 400px;
  background-color: var(--background-color-1);
  color: var(--font-color-secondary);
  border-radius: 20px;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.input-box-title {
  color: var(--font-color-primary);
  margin: 0;
  margin-top: 20px;
}

.input-box-note {
  color: var(--font-color-secondary);
  margin-bottom: 50px;
}

.input-box-input {
  outline: none;
  border: none;
  background-color: var(--background-color-2);
  height: 60px;
  width: 80%;
  border-radius: 20px;
  color: var(--font-color-primary);
  font-size: 20px;
  text-indent: 10px;
  margin-bottom: 30px;
}

.input-box-buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 80%;
  height: 100px;
}

.input-box-button {
  width: 20%;
  height: 50%;
  background-color: var(--background-color-2);
  color: var(--font-color-primary);
  outline: none;
  border: none;
  border-radius: 20px;
  margin-bottom: 30px;
  transition: background 0.3s ease;
}

.input-box-button:hover {
  background-color: color-mix(in lch, rgb(255, 255, 255) 5%, var(--background-color-3));
}
</style>
