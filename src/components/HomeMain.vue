<script setup>
import IconOthers from "./icons/iconOthers.vue"
import IconPlus from "./icons/iconPlus.vue"
import ClickMenu from "./ClickMenu.vue"
import { ref, defineProps } from "vue";

const cards = ref([
  {
    title: "测试webshell",
    note: "测试测试"
  },
  {
    title: "测试webshell",
    note: "测试测试"
  },
  {
    title: "测试webshell",
    note: "测试测试"
  },
  {
    title: "测试webshell",
    note: "测试测试"
  },
  {
    title: "测试webshell",
    note: "测试测试"
  },
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
  <div class="cards">
    <div class="card" v-for="card in cards">
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
    <ClickMenu :top="ClickMenuTop" :left="ClickMenuLeft" @remove="(_) => showClickMenu = false" />
  </div>
  <div class="add-webshell-button">
    <IconPlus />
  </div>
</template>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  column-gap: 2%;
  justify-content: space-between;
}

.card {
  height: 160px;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  margin-bottom: 40px;
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
