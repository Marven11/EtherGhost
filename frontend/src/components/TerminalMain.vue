<script setup>
import { getDataOrPopupError, parseDataOrPopupError } from "@/assets/utils";
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
const terminalInputReadonly = ref(false)
const terminalOutput = ref("$")

if (props.session) {
  store.session = props.session
}

function addCommand(command) {
  terminalOutput.value = `${terminalOutput.value} ${command}\n`
  // change scroll position after text rendered.
  setTimeout(() => {
    let textarea = document.getElementById("command-output");
    textarea.scrollTop = textarea.scrollHeight;
  }, 0)
}

function addOutput(output) {
  terminalOutput.value = `${terminalOutput.value}${output}\n$`
  // change scroll position after text rendered.
  setTimeout(() => {
    let textarea = document.getElementById("command-output");
    textarea.scrollTop = textarea.scrollHeight;
  }, 0)
}

async function onExecuteCommand(event) {
  const cmd = terminalInput.value;
  event.preventDefault()
  terminalInput.value = ""
  terminalInputReadonly.value = true
  try {
    addCommand(cmd)
    const result = await getDataOrPopupError(`/session/${props.session}/execute_cmd`, {
      params: {
        cmd: cmd
      }
    })
    addOutput(result)
  } catch (error) {
    throw error
  } finally {
    terminalInputReadonly.value = false

  }

}

// ###########
// --- Input Box ---
// ###########

const showInputBox = ref(false)

</script>

<template>
  <form action="" class="command-input" @submit="onExecuteCommand">
    <input id="command-input" type="text" placeholder="cat /etc/passwd" v-model="terminalInput"
      :readonly="terminalInputReadonly">
    <div class="icon-run" @click="onExecuteCommand">
      <IconRun />
    </div>
  </form>
  <div class="terminal-output">
    <textarea name="command-output" id="command-output" readonly :value="terminalOutput"></textarea>
  </div>
  <transition>
    <InputBox v-if="showInputBox" title="测试标题" note="测试测试，这是一个测试" :requireInput="true"
      @result="(_) => showInputBox = false" />
  </transition>
</template>

<style scoped>
.command-input {
  display: flex;
  height: 60px;
}

.command-input input {
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  border: none;
  border-radius: 20px;
  margin-right: 20px;
  outline: none;
  flex-grow: 1;
  font-size: 24px;
  text-indent: 10px;
  width: 100px;
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

.terminal-output {
  margin-top: 30px;
  height: 85%;
  flex-grow: 1;
}

.terminal-output textarea {
  width: 100%;
  height: 100%;
  background-color: var(--background-color-2);
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
t.me