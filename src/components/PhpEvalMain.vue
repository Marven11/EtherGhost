<script setup>
import { getDataOrPopupError, parseDataOrPopupError, postDataOrPopupError } from "@/assets/utils";
import IconRun from "./icons/iconRun.vue"
import { ref } from "vue";
import Axios from "axios";
import { getCurrentApiUrl } from "@/assets/utils";
import { store } from "@/assets/store";
import InputBox from "./InputBox.vue"


const props = defineProps({
  session: String,
})
const terminalInput = ref("")
const terminalOutput = ref("")

if (props.session) {
  store.session = props.session
}

function addOutput(command, output) {
  let leading = ""
  if (terminalOutput.value) {
    leading = `${terminalOutput.value}\n`;
  }
  terminalOutput.value = `${leading}$ ${command}\n${output}`
  // change scroll position after text rendered.
  setTimeout(() => {
    let textarea = document.getElementById("phpcode-output");
    textarea.scrollTop = textarea.scrollHeight;
  }, 0)
}

async function onEvalPhpCode(event) {
  const url = `/session/${props.session}/php_eval`
  const code = terminalInput.value;
  console.log(code);
  event.preventDefault()
  terminalInput.value = ""
  const result = await postDataOrPopupError(url, {
    code: code
  });
  addOutput(code, result)
}

// ###########
// --- Input Box ---
// ###########

const showInputBox = ref(false)

</script>

<template>
  <form action="" class="phpcode-input" @submit="onEvalPhpCode">
    <input id="phpcode-input" type="text" placeholder="var_dump('exploit!');" v-model="terminalInput">
    <div class="icon-run" @click="onEvalPhpCode">
      <IconRun />
    </div>
  </form>
  <div class="phpcode-output">
    <textarea name="phpcode-output" id="phpcode-output" readonly :value="terminalOutput"></textarea>
  </div>
  <transition>
    <InputBox v-if="showInputBox" title="测试标题" note="测试测试，这是一个测试" :requireInput="true"
      @result="(_) => showInputBox = false" />
  </transition>
</template>

<style scoped>
.phpcode-input {
  display: flex;
  height: 60px;
}

.phpcode-input input {
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  border: none;
  border-radius: 20px;
  margin-right: 20px;
  outline: none;
  flex-grow: 1;
  font-size: 24px;
  text-indent: 10px;
}

.icon-run {
  height: 60px;
  width: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color-2);
  border-radius: 20px;
  transition: all 0.3s ease;
  opacity: 1;
}

.icon-run:hover {
  background-color: var(--background-color-3);
  outline: 2px solid var(--font-color-grey);
}

.phpcode-output {
  margin-top: 30px;
  height: 85%;
}

.phpcode-output textarea {
  width: 100%;
  height: 100%;
  background-color: #00000015;
  color: var(--font-color-white);
  border-radius: 20px;
  font-size: 24px;
  padding: 20px;
  outline: none;
  border: none;
  resize: none;
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
