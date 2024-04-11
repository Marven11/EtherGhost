<script setup>
import IconOthers from "./icons/iconOthers.vue"
import IconPlus from "./icons/iconPlus.vue"
import ClickMenu from "./ClickMenu.vue"
import { ref } from "vue";
import { getCurrentApiUrl, getDataOrPopupError } from "@/assets/utils";
import Popups from "./Popups.vue";
import axios from "axios";

const sessions = ref([
  {
    type: "ONELINE_PHP",
    readable_type: "PHP一句话",
    id: "b9ffbeaa-2906-4865-ad7f-1818896dfe8c",
    name: "123",
    note: "测试备注",
    location: "未知位置"
  }
])

const popupsRef = ref(null)
const showClickMenu = ref(false)
const ClickMenuLeft = ref(0)
const ClickMenuTop = ref(0)
function onClickIconOthers(event) {
  console.log(event)
  showClickMenu.value = true
  ClickMenuLeft.value = event.clientX;
  ClickMenuTop.value = event.clientY;
}

async function fetchWebshell() {
  const url = getCurrentApiUrl()
  const resp = await axios.get(`${url}/session`)
  const sessions = getDataOrPopupError(resp.data, popupsRef)
  sessions.value = sessions
}

setTimeout(fetchWebshell, 0)

</script>

<template>
  <div class="sessions">
    <div class="session" v-for="session in sessions">
      <div class="session-top">
        <div class="session-name">
          <p>
            {{ session.name }}
          </p>
        </div>
        <div>
          <div class="session-icon-others" @click="onClickIconOthers">
            <IconOthers />
          </div>
        </div>
      </div>
      <div class="session-bottom">
        <div class="session-note">
          {{ session.note }}
        </div>
      </div>
    </div>
  </div>
  <div v-if="showClickMenu">
    <ClickMenu :top="ClickMenuTop" :left="ClickMenuLeft" @remove="(_) => showClickMenu = false" />
  </div>
  <div class="add-webshell-button">
    <IconPlus />
  </div>
  <Popups ref="popupsRef" />
</template>

<style scoped>
.sessions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  column-gap: 2%;
  justify-content: space-between;
}

.session {
  height: 160px;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  margin-bottom: 40px;
  padding-left: 20px;
  padding-right: 20px;
  border-radius: 20px;
}

.session-top {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
  height: 40%;
}

.session-top p,
.session-top svg {
  margin: 0px;
  margin-top: 20px;
}

.session-top p {
  font-size: 20px;
  font-weight: bold;
}

.session-bottom {
  color: var(--font-color-grey);
}

.add-webshell-button {
  width: 70px;
  height: 70px;
  background-color: #00000030;
  border-radius: 1000px;
  position: fixed;
  top: 90vh;
}

.add-webshell-button svg {
  width: 50px;
  stroke: var(--font-color-white);
  margin: 10px;
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
