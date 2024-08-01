<script setup>
import { computed, shallowRef, watch } from "vue"
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
import { addPopup } from "@/assets/utils"
import IconHash from "./icons/iconHash.vue"

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
    uri: "/proxies",
    tooltip: "代理"
  },
  {
    type: "shell-command",
    component: IconHash,
    uri: "/shell-command/SESSION",
    tooltip: "命令执行"
  },
  {
    type: "others",
    component: IconOthers,
    uri: "/",
    tooltip: "其他"
  },
  {
    type: "settings",
    component: IconSetting,
    uri: "/settings/",
    tooltip: "设置"
  },
]

const icons = shallowRef([])

function fillSession(icons, session) {
  return icons.map(icon => {
    let clone = { ...icon };
    if (icon.uri.indexOf("SESSION") == -1) {
      return clone
    }
    if (session) {
      clone.uri = icon.uri.replace("SESSION", session)
    } else {
      clone.uri = "/popup/no_session"
    }
    return clone
  })
}

icons.value = fillSession(iconSpecs, store.session || "")

watch(() => store.session, (newSession, _) => {
  icons.value = fillSession(iconSpecs, newSession)
})

const iconsCount = computed(() => icons.value.length)

function clickIcon(icon) {
  if (icon.uri == "/popup/no_session") {
    addPopup("red", "没有选中WebShell", "请先在主页选中Webshell")
  } else {
    router.push(icon.uri)
  }
}

</script>

<template>
  <header :data-bg-transition="store.header_background_transition">
    <div class="header-title">
      <h1>
        游魂
      </h1>
      <p>{{ store.sessionName }}</p>
    </div>
    <div class="nav-space">
      <nav>
        <div v-for="icon in icons" @click="clickIcon(icon)" class="icon" :title="icon.tooltip">
          <component :is="icon.component"></component>
        </div>
      </nav>
    </div>


  </header>

</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  margin-top: 30px;
  border-radius: 20px;
  background-color: var(--primary-color);
  width: 90%;
  min-height: 120px;
  padding-left: 2%;
  padding-right: 2%;
}

header[data-bg-transition="true"] {
  transition: background 0.8s ease;
}

.header-title {
  display: flex;
  align-items: left;
  justify-content: center;
  flex-direction: column;
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

.nav-space {
  flex-grow: 1;
  max-width: 800px;
  display: flex;
  align-items: center;
  justify-content: center;
}

nav {
  display: grid;
  width: 100%;
  justify-items: end;
  grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
}

@media (min-width: 600px) {
  nav {
    grid-template-columns: repeat(v-bind(iconsCount), 1fr);
  }
}



.icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  border-radius: 200px;
  transition: background 0.3s ease;
}

.icon:hover {
  background-color: #00000015;
}

svg {
  width: 35px;
  color: var(--font-color-black);
  stroke: var(--font-color-black);
}
</style>
