<script setup>
import { shallowRef, watch } from "vue"
import IconHome from "./icons/iconHome.vue"
import IconTerminal from "./icons/iconTerminal.vue"
import IconFileBrowser from "./icons/iconFileBrowser.vue"
import IconInfo from "./icons/iconInfo.vue"
import IconProxy from "./icons/iconProxy.vue"
import IconOthers from "./icons/iconOthers.vue"
import IconSetting from "./icons/iconSetting.vue"
import { useRouter } from "vue-router"
import { store } from "@/assets/store.js"
import IconCode from "./icons/iconCode.vue"

const router = useRouter()
const iconSpecs = [
  {
    type: "home",
    component: IconHome,
    uri: "/",
    tooltip: "回到主页，打开其他webshell"
  },
  {
    type: "terminal",
    component: IconTerminal,
    uri: "/terminal/SESSION",
    tooltip: "模拟终端"
  },
  {
    type: "open-php-eval",
    component: IconCode,
    uri: "/php-eval/SESSION",
    tooltip: "PHP Eval"
  },
  {
    type: "file-browser",
    component: IconFileBrowser,
    uri: "/file-browser/SESSION",
    tooltip: "文件管理"
  },
  {
    type: "info",
    component: IconInfo,
    uri: "/",
    tooltip: "机器信息"
  },
  {
    type: "proxy",
    component: IconProxy,
    uri: "/",
    tooltip: "代理"
  },
  {
    type: "others",
    component: IconOthers,
    uri: "/",
    tooltip: "其他"
  },
]

const icons = shallowRef({})

function fillSession(icons, session) {
  return icons.map(icon => {
    let clone = { ...icon };
    if (icon.uri.indexOf("SESSION") == -1) {
      return clone
    }
    if (session) {
      clone.uri = icon.uri.replace("SESSION", session)
    } else {
      clone.uri = "/page_404/no_session"
    }
    return clone
  })
}

icons.value = fillSession(iconSpecs, "")

watch(() => store.session, (newSession, _) => {
  icons.value = fillSession(iconSpecs, newSession)
})

function clickIcon(icon) {
  router.push(icon.uri)
}

</script>

<template>
  <header>
    <div class="header-title">
      <h1>
        鬼刃
      </h1>
      <p>{{ store.sessionName }}</p>
    </div>
    <nav>
      <div v-for="icon in icons" @click="clickIcon(icon)" class="icon" :title="icon.tooltip">
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
  align-items: left;
  justify-content: center;
  flex-direction: column;
  padding-left: 50px;
}

.header-title h1 {
  font-size: 40px;
  font-weight: bolder;
  margin: 0;
}

.header-title p {
  font-size: 16px;
  color: var(--font-color-grey);
  margin: 0;
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
