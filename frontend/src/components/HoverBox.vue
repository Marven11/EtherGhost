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
import { addPopup } from "@/assets/utils"

</script>

<template>
  <div class="hover-box-main">
    <slot></slot>
  </div>
</template>

<style scoped>
.hover-box-main {
  position: absolute;
  left: 25%;
  top: 97%;
  width: 50%;
  height: 80%;
  background-color: var(--background-color-hover);
  border-radius: 20px;
  transition: all 0.5s ease;
}
.hover-box-main:hover {
  top: 60%;
}

</style>
