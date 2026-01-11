<script setup>
import { computed, ref, shallowRef, watch } from "vue"
import IconHome from "@/components/icons/iconHome.vue"
import IconTerminal from "@/components/icons/iconTerminal.vue"
import IconFileBrowser from "@/components/icons/iconFileBrowser.vue"
import IconInfo from "@/components/icons/iconInfo.vue"
import IconProxy from "@/components/icons/iconProxy.vue"
import IconOthers from "@/components/icons/iconOthers.vue"
import IconSetting from "@/components/icons/iconSetting.vue"
import { useRouter } from "vue-router"
import { store } from "@/assets/store.js"
import IconCode from "@/components/icons/iconCode.vue"
import { addPopup, ClickMenuManager, ClickMenuManagerDualLayer } from "@/assets/utils"
import IconHash from "@/components/icons/iconHash.vue"
import IconEdit from "@/components/icons/iconEdit.vue"
import ClickMenu from "./ClickMenu.vue"
import ClickMenuDualLayer from "./ClickMenuDualLayer.vue"
import IconSpider from "./icons/iconSpider.vue"
import IconLeft from "./icons/iconLeft.vue"
import IconRight from "./icons/iconRight.vue"
import IconKnife from "./icons/iconKnife.vue"
import IconWarning from "./icons/iconWarning.vue"
import IconPlug from "./icons/iconPlug.vue"
import IconUsb from "./icons/iconUsb.vue"

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
    type: "file-browser",
    component: IconFileBrowser,
    uri: "/file-browser/SESSION",
    tooltip: "文件管理"
  },
  {
    type: "info",
    component: IconInfo,
    uri: "/basic-info/SESSION",
    tooltip: "机器信息"
  },
  {
    type: "proxy",
    component: IconProxy,
    uri: "/proxies",
    tooltip: "打开代理"
  },
  {
    type: "connector",
    component: IconUsb,
    uri: "/connector/",
    tooltip: "连接器"
  },
  {
    type: "settings",
    component: IconSetting,
    uri: "/settings/",
    tooltip: "设置"
  },
  {
    type: "others",
    component: IconOthers,
    uri: "",
    tooltip: "其他"
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

// click menus
// 这里一共有三个click menu
// clickMenuRightClick: 右键普通按钮时出现的click menu
// clickMenuOthers: 点击Others按钮时出现的click menu
// clickMenuOthersRightClick: 右键点击clickMenuOthers的项目时产生的click menu(二级菜单)

// 左键点击clickMenuOthers时会直接执行对应的动作并关闭click menu
// 右键点击clickMenuOthers时会打开clickMenuOthersRightClick
// 然后在clickMenuOthersRightClick关闭时一并关闭clickMenuOthers



let rightClickedIcon = undefined

const clickMenuRightClick = ClickMenuManager(
  [
    {
      name: "open",
      text: "打开",
      icon: IconHash,
      color: "white",
    },
    {
      name: "open_in_new_page",
      text: "在新标签页打开",
      icon: IconCode,
      color: "white",
    },
  ],
  (item) => {
    if (rightClickedIcon.uri == "/popup/no_session") {
      addPopup("red", "没有选中WebShell", "请先在主页选中Webshell")
    }
    else if (item.name == "open") {
      router.push(rightClickedIcon.uri)
    } else {
      let link = router.resolve({ path: rightClickedIcon.uri })
      window.open(link.href, '_blank');
    }
  }
)

const clickMenuOthers = ClickMenuManagerDualLayer(
  [
    {
      name: "shell_command",
      text: "命令执行",
      icon: IconHash,
      color: "white",
      link: "/shell-command/SESSION"
    },
    {
      name: "php_eval",
      text: "PHP代码执行",
      icon: IconCode,
      color: "white",
      link: "/php-eval/SESSION",
    },
    {
      name: "reverse_shell",
      text: "反弹Shell",
      icon: IconPlug,
      color: "white",
      link: "/reverse-shell/SESSION"
    },
    {
      name: "emulated_antsword",
      text: "对接蚁剑",
      icon: IconSpider,
      color: "white",
      children: [
        {
          name: "open_antsword",
          text: "打开",
          icon: IconHash,
          color: "white",
          link: "/emulated-antsword/SESSION"
        },
        {
          name: "open_antsword_new_page",
          text: "在新标签页打开",
          icon: IconCode,
          color: "white",
          link: "/emulated-antsword/SESSION"
        }
      ]
    },
    {
      name: "awd_tools",
      text: "AWD实用工具",
      icon: IconKnife,
      color: "white",
      children: [
        {
          name: "open_awd_tools",
          text: "打开",
          icon: IconHash,
          color: "white",
          link: "/awd-tools/SESSION"
        },
        {
          name: "open_awd_tools_new_page",
          text: "在新标签页打开",
          icon: IconCode,
          color: "white",
          link: "/awd-tools/SESSION"
        }
      ]
    },
    {
      name: "about",
      text: "关于本软件",
      icon: IconWarning,
      color: "white",
      link: "/about"
    },
    {
      name: "edit_session",
      text: "修改webshell",
      icon: IconEdit,
      color: "white",
      link: "/webshell-editor/SESSION"
    },
  ],
  (item) => {
    if (!store.session && item.link && item.link.indexOf("SESSION") != -1) {
      addPopup("red", "没有选中WebShell", "请先在主页选中Webshell")
    } else if (item.link) {
      const uri = item.link.replace("SESSION", store.session)
      router.push(uri)
    }
  }
)


function clickIcon(event, icon) {
  if (icon.type == "others") {
    clickMenuOthers.onshow(event)
  }
  else if (icon.uri == "/popup/no_session") {
    addPopup("red", "没有选中WebShell", "请先在主页选中Webshell")
  } else {
    router.push(icon.uri)
  }
}


function rightClickIcon(event, icon) {
  rightClickedIcon = icon
  console.log(icon)
  if (icon.type == "others") {
    clickMenuOthers.onshow(event)
  } else {
    clickMenuRightClick.onshow(event)
  }
}


function historyBack() {
  window.history.back()
}

function historyForward() {
  window.history.forward()
}

</script>

<template>
  <header :data-bg-transition="store.theme_background_transition">
    <div class="header-title">
      <h1>
        游魂
      </h1>
      <p>{{ store.sessionName }}</p>
    </div>
    <div class="nav-space">

      <nav>
        <div class="icon" @click="historyBack()" title="返回">
          <IconLeft></IconLeft>
        </div>
        <div class="icon" @click="historyForward()" title="前进">
          <IconRight></IconRight>
        </div>
        <div class="icon-delimiter-background">
          <div class="icon-delimiter"></div>

        </div>
        <div v-for="icon in icons" class="icon" @click="(event) => clickIcon(event, icon)"
          @click.right.prevent="event => rightClickIcon(event, icon)" :title="icon.tooltip">
          <component :is="icon.component"></component>
        </div>
      </nav>
    </div>

  </header>

  <transition>
    <div v-if="clickMenuOthers.show.value" class="header-click-menu">
      <ClickMenuDualLayer :mouse_y="clickMenuOthers.y" :mouse_x="clickMenuOthers.x" :menuItems="clickMenuOthers.items.value" :show="clickMenuOthers.show.value"
        @close="clickMenuOthers.onremove"
        @select="clickMenuOthers.onclick" />
    </div>
  </transition>
  <transition>
    <div v-if="clickMenuRightClick.show.value" class="header-click-menu">
      <ClickMenu :mouse_y="clickMenuRightClick.y" :mouse_x="clickMenuRightClick.x"
        :menuItems="clickMenuRightClick.items.value" @remove="clickMenuRightClick.onremove"
        @clickItem="clickMenuRightClick.onclick" />
    </div>
  </transition>

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
  min-height: 6rem;
  padding-left: 2%;
  padding-right: 2%;
  box-shadow: 0 0 10px rgba(15, 15, 15, 0.7);
}

header[data-bg-transition="true"] {
  transition: background 0.8s ease;
}

body[data-theme="glass"] header {
  backdrop-filter: blur(20px);
}

.header-title {
  display: flex;
  align-items: left;
  justify-content: center;
  flex-direction: column;
}

.header-title h1 {
  font-size: 2.2rem;
  margin: 0;
}

.header-title p {
  font-size: 1rem;
  color: var(--font-color-secondary);
  margin: 0;
}

.nav-space {
  flex-grow: 1;
  max-width: 50rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

nav {
  display: grid;
  width: 100%;
  justify-items: end;
  grid-template-columns: repeat(auto-fill, minmax(3.125rem, 1fr));
}

@media (min-width: 600px) {
  nav {
    grid-template-columns: 1fr 1fr 0.4fr repeat(v-bind(iconsCount), 1fr);
  }
}

.icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 3.125rem;
  border-radius: 200px;
  transition: background 0.3s ease;
}

.icon:hover {
  background-color: #00000015;
}

.icon-delimiter-background {
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.icon-delimiter {
  background-color: #00000015;
  height: 100%;
  width: 0.3125rem;
  border-radius: 20px;
}

svg {
  width: 1.875rem;
  color: var(--font-color-black);
  stroke: var(--font-color-black);
}

.header-click-menu {
  z-index: 10;
}
</style>
