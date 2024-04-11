<script setup>
import { getDataOrPopupError } from "@/assets/utils";
import IconRun from "./icons/iconRun.vue"
import Popups from "./Popups.vue"
import { ref } from "vue";
import Axios from "axios";
import { getCurrentApiUrl } from "@/assets/utils";

const props = defineProps({
  session: String,
})
const terminalInput = ref("")
const terminalOutput = ref("")
const popupsRef = ref(null)

function addOutput(command, output) {
  let leading = ""
  if (terminalOutput.value) {
    leading = `${terminalOutput.value}\n`;
  }
  terminalOutput.value = `${leading}$ ${command}\n${output}`
  // change scroll position after text rendered.
  setTimeout(() => {
    let textarea = document.getElementById("command-output");
    textarea.scrollTop = textarea.scrollHeight;
  }, 0)
}

async function onExecuteCommand(event) {
  const url = `${getCurrentApiUrl()}/session/${props.session}/execute_cmd`
  const cmd = terminalInput.value;
  event.preventDefault()
  terminalInput.value = ""
  const resp = await Axios.get(url, {
    params: {
      cmd: cmd
    }
  })
  console.log(resp)
  const result = getDataOrPopupError(resp, popupsRef)
  addOutput(cmd, result)
}

</script>

<template>
  <form action="" class="command-input" @submit="onExecuteCommand">
    <input id="command-input" type="text" placeholder="cat /etc/passwd" v-model="terminalInput">
    <div class="icon-run" @click="onExecuteCommand">
      <IconRun />
    </div>
  </form>
  <div class="terminal-output">
    <textarea name="command-output" id="command-output" readonly :value="terminalOutput"></textarea>
  </div>
  <Popups ref="popupsRef" />
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
  font-size: 30px;
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

.terminal-output {
  margin-top: 30px;
  height: 85%;
}

.terminal-output textarea {
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
