import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";

import Settings from "./components/pages/Settings.vue";
import WebshellEditorMain from "./components/pages/WebshellEditorMain.vue";
import HomeMain from "./components/pages/HomeMain.vue";
import TerminalMain from "./components/pages/TerminalMain.vue";
import ShellCommandMain from "./components/pages/ShellCommandMain.vue";
import FileBrowserMain from "./components/pages/FileBrowserMain.vue";
import PhpEvalMain from "./components/pages/PhpEvalMain.vue";
import EmulatedAntswordMain from "./components/pages/EmulatedAntswordMain.vue";
import BasicInfoMain from "./components/pages/BasicInfoMain.vue";
import AwdActionsMain from "./components/pages/AwdToolsMain.vue";
import Proxies from "./components/pages/Proxies.vue";
import { createRouter, createWebHashHistory } from "vue-router";
import Terminal from 'vue-web-terminal'
//  亮色主题：vue-web-terminal/lib/theme/light.css
import './assets/vue-web-terminal.css'


const routes = [
  { path: "/", component: HomeMain, props: true },
  {
    path: "/webshell-editor/:session",
    component: WebshellEditorMain,
    props: true,
  },
  {
    path: "/webshell-editor/",
    component: WebshellEditorMain,
    props: true,
  },
  {
    path: "/settings/",
    component: Settings,
    props: true,
  },
  {
    path: "/terminal/:session",
    component: TerminalMain,
    props: route => ({
      session: route.params.session,
      pwd: route.query.pwd
    })
  },
  { path: "/shell-command/:session", component: ShellCommandMain, props: true },
  { path: "/awd-tools/:session", component: AwdActionsMain, props: true },
  { path: "/file-browser/:session", component: FileBrowserMain, props: true },
  { path: "/php-eval/:session", component: PhpEvalMain, props: true },
  { path: "/emulated-antsword/:session", component: EmulatedAntswordMain, props: true },
  { path: "/basic-info/:session", component: BasicInfoMain, props: true },
  { path: "/proxies", component: Proxies, props: true },
  { path: "/proxies/:session", component: Proxies, props: true },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

createApp(App).use(router).use(Terminal).mount("#app");
