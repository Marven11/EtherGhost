<script setup>
import IconOthers from "./icons/iconOthers.vue"
import ClickMenu from "./ClickMenu.vue"
import { ref } from "vue";

const cards = ref([
  {
    title: "测试webshell",
    note: "测试测试"
  }
])

const showClickMenu = ref(false)
const ClickMenuLeft = ref(0)
const ClickMenuTop = ref(0)
function onClickIconOthers(event) {
  console.log(event)
  showClickMenu.value = true
  ClickMenuLeft.value = event.clientX;
  ClickMenuTop.value = event.clientY;
}


</script>

<template>
  <div class="cards" v-for="card in cards">
    <div class="card">
      <div class="card-top">
        <div class="card-name">
          <p>
            {{ card.title }}
          </p>
        </div>
        <div>
          <div class="card-icon-others" @click="onClickIconOthers">
            <IconOthers />
          </div>
        </div>
      </div>
      <div class="card-bottom">
        <div class="card-note">
          {{ card.note }}
        </div>
      </div>
    </div>
  </div>
  <div v-if="showClickMenu">
    <ClickMenu :top="ClickMenuTop" :left="ClickMenuLeft" @remove="(_) => showClickMenu = false"/>
  </div>
</template>

<style scoped>

.cards {
  display: flex;
}

.card {
  height: 160px;
  width: 30%;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  padding-left: 20px;
  padding-right: 20px;
  border-radius: 20px;
}

.card-top {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
  height: 40%;
}

.card-top p,
.card-top svg {
  margin: 0px;
  margin-top: 20px;
}

.card-top p {
  font-size: 20px;
  font-weight: bold;
}

.card-bottom {
  color: var(--font-color-grey);
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
