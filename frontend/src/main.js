import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";

import Settings from "./components/Settings.vue";
import WebshellEditorMain from "./components/WebshellEditorMain.vue";
import HomeMain from "./components/HomeMain.vue";
import TerminalMain from "./components/TerminalMain.vue";
import ShellCommandMain from "./components/ShellCommandMain.vue";
import FileBrowserMain from "./components/FileBrowserMain.vue";
import PhpEvalMain from "./components/PhpEvalMain.vue";
import EmulatedAntswordMain from "./components/EmulatedAntswordMain.vue";
import Proxies from "./components/Proxies.vue";
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
  { path: "/terminal/:session", component: TerminalMain, props: true },
  { path: "/shell-command/:session", component: ShellCommandMain, props: true },
  { path: "/file-browser/:session", component: FileBrowserMain, props: true },
  { path: "/php-eval/:session", component: PhpEvalMain, props: true },
  { path: "/emulated-antsword/:session", component: EmulatedAntswordMain, props: true },
  { path: "/proxies", component: Proxies, props: true },
  { path: "/proxies/:session", component: Proxies, props: true },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

createApp(App).use(router).use(Terminal).mount("#app");
