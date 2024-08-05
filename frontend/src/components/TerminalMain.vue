<script setup>
import { store } from '@/assets/store';
import { getDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';
import Terminal, { TerminalApi } from 'vue-web-terminal';

const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

const pwd = ref("")

async function psudoExec(command) {
  if (pwd.value == "") {
    pwd.value = (await getDataOrPopupError(`/session/${props.session}/execute_cmd`, {
      params: {
        cmd: "pwd"
      }
    })).trim()
  }
  const result_text = await getDataOrPopupError(`/session/${props.session}/execute_cmd`, {
    params: {
      cmd: `cd ${pwd.value}; (${command}) 2>&1`
    }
  })
  return result_text
}

async function onExecCmd(key, command, success, failed) {

  // TODO: fix this regexp, it stop user cd to special directory
  if (key == "cd" && /^cd +[-_a-zA-Z0-9\/]+$/.test(command)) {
    let result
    try {
      result = await psudoExec(command + "; pwd")
    } catch (error) {
      failed()
      return
    }
    // when `cd` success it produces no output
    if (!result.trim().includes("can't cd to")) {
      pwd.value = result.trim()
      success()
    } else {
      success({
        type: "ansi",
        content: result
      })
    }
  } else if (key == "clear") {
    TerminalApi.clearLog("my-terminal")
    success()
  } else {
    let result
    try {
      result = await psudoExec(command)
    } catch (error) {
      failed()
      return
    }
    success({
      type: 'ansi',
      content: result
    })
  }
}
</script>

<template>
  <div class="terminal-main">
    <terminal name="my-terminal" :context="pwd" :show-header="false" :log-size-limit="500"
      :enable-default-command="false" @exec-cmd="onExecCmd" />
  </div>
</template>

<style scoped>
.terminal-main {
  height: 100%;
  width: 100%;
  z-index: 0;
}
</style>
