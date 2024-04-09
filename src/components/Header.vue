<script setup>
import { ref } from "vue"
import IconHome from "./icons/iconHome.vue"
import IconTerminal from "./icons/iconTerminal.vue"
import IconFileBrowser from "./icons/iconFileBrowser.vue"
import IconInfo from "./icons/iconInfo.vue"
import IconProxy from "./icons/iconProxy.vue"
import IconOthers from "./icons/iconOthers.vue"
import IconSetting from "./icons/iconSetting.vue"

const icons = [
  {
    type: "home",
    component: IconHome,
    uri: "/"
  },
  {
    type: "terminal",
    component: IconTerminal,
    uri: "/"
  },
  {
    type: "file-browser",
    component: IconFileBrowser,
    uri: "/"
  },
  {
    type: "info",
    component: IconInfo,
    uri: "/"
  },
  {
    type: "proxy",
    component: IconProxy,
    uri: "/"
  },
  {
    type: "others",
    component: IconOthers,
    uri: "/"
  },
]

function clickIcon(icon) {
  window.location = icon.uri
}

</script>

<template>
  <header>
    <div class="header-title">
      <p>
        鬼刃
      </p>
    </div>
    <nav>
      <div v-for="icon in icons" @click="clickIcon(icon)" class="icon">
        <component :is="icon.component"></component>
      </div>
    </nav>
    <div class="header-setting">
      <div class="icon">
        <IconSetting />
      </div>

    </div>
  </header>

</template>

<style scoped>
header {
  display: flex;
  justify-content: center;
  flex-direction: row;
  margin-top: 30px;
  border-radius: 20px;
  background-color: var(--primary-color);
  width: 90%;
  height: 12vh;
  min-height: 130px;
}

.header-title {
  width: 30%;
  display: flex;
  align-items: center;
  padding-left: 50px;
}

.header-title p {
  font-size: 40px;
  font-weight: bolder;
}

nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 40%;
}


.icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  border-radius: 200px;
}

.icon:hover {
  background-color: #00000015;
}

svg {
  width: 35px;
  color: var(--font-color-black);
  stroke: var(--font-color-black);
}


.header-setting {
  width: 30%;
  display: flex;
  flex-direction: row-reverse;
  padding-right: 50px;
  align-items: center;
}
</style>
