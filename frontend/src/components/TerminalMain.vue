<script setup>
import Terminal from 'vue-web-terminal';

const dragConf = {
    width: "90%",
    height: "80%",
    zIndex: 100,

    pinned: false
}

function onExecCmd(key, command, success, failed) {
    if (key === 'fail') {
        failed('Something wrong!!!')
    } else {
        let allClass = ['success', 'error', 'system', 'info', 'warning'];

        let clazz = allClass[Math.floor(Math.random() * allClass.length)];
        success({
            type: 'normal',
            class: clazz,
            tag: clazz,
            content: `Your command is '${command}'`
        })
    }
}
</script>

<template>
    <div class="terminal-main">
        <terminal name="my-terminal" :show-header="false" :log-size-limit="500" :enable-default-command="false"
        @exec-cmd="onExecCmd" :drag-conf="dragConf" />
    </div>

</template>

<style scoped>
.terminal-main {
    height: 100%;
    width: 100%;
}

</style>
