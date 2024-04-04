<script setup>
import IconRun from "./icons/iconRun.vue"
import { ref } from "vue";

const terminalOutput = ref("");

function addOutput(command, output) {
  let leading = ""
  if (terminalOutput.value) {
    leading = `${terminalOutput.value}\n`;
  }
  terminalOutput.value = `${leading}$ ${command}\n${output}`
}
addOutput("whoami", "root")

function onExecuteCommand(event) {
  event.preventDefault()
  let element = document.getElementById("command-input")
  let cmd = element.value;
  element.value = ""
  addOutput(cmd, "nothing here")
}

</script>

<template>
  <form action="" class="command-input" @submit="onExecuteCommand">
    <input id="command-input" type="text" placeholder="cat /etc/passwd">
    <div class="icon-run" @click="onExecuteCommand">
      <IconRun />
    </div>
  </form>
  <div class="terminal-output">
    <textarea name="output-area" id="output-area" readonly :value="terminalOutput"></textarea>
  </div>
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
