<script setup>
import { store } from '@/assets/store';
import { getDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';
import Terminal, { TerminalApi } from 'vue-web-terminal';

const props = defineProps({
  session: String,
})

const dragConf = {
  width: "90%",
  height: "80%",
  zIndex: 100,

  pinned: false
}

if (props.session) {
  store.session = props.session
}

const pwd = ref("/unknown_pwd")

function randomString(length) {
  let result = '';
  for (let i = 0; i < length; i++) {
    result += String.fromCharCode(Math.floor(Math.random() * 26) + 97);
  }
  return result;
}


async function psudoExec(command) {
  const result_text = await getDataOrPopupError(`/session/${props.session}/execute_cmd`, {
    params: {
      cmd: `cd ${pwd.value}; (${command}) 2>&1`
    }
  })
  return result_text
}

async function onExecCmd(key, command, success, failed) {
  if (key == "cd") {
    const result = await psudoExec(command)
    // when `cd` success it produces no output
    if (result.trim() == "") {
      pwd.value = command.substring(2).trim()
    }
    success({
      type: "ansi",
      content: result
    })
  } else if (key == "clear") {
    TerminalApi.clearLog("my-terminal")
    success()
  } else {
    success({
      type: 'ansi',
      content: await psudoExec(command)
    })
  }
}

setTimeout(async () => {
  const result = await getDataOrPopupError(`/session/${props.session}/execute_cmd`, {
    params: {
      cmd: "pwd"
    }
  })
  pwd.value = result.trim()
}, 0)
</script>

<template>
  <div class="terminal-main">
    <terminal name="my-terminal" :context="pwd" :show-header="false" :log-size-limit="500"
      :enable-default-command="false" @exec-cmd="onExecCmd" :drag-conf="dragConf" />
  </div>

</template>

<style scoped>
.terminal-main {
  height: 100%;
  width: 100%;
}
</style>
