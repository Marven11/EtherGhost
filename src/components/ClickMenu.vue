<script setup>
import { ref, shallowRef, defineEmits } from "vue"


const props = defineProps(["top", "left", "menu_items"])

const emit = defineEmits(["remove", "clickItem"])

// An item is sth loke this:
// {
//     "name": "open_terminal",
//     "text": "打开终端",
//     "icon": IconTerminal,
//     "color": "white",
//   },
const menu_items = shallowRef([...props.menu_items])

const opacity = ref(0)
const useBackground = ref(true)

setTimeout(() => {
  opacity.value = 1
}, 0)


function hideAndEmit() {
  opacity.value = 0
  useBackground.value = false
  setTimeout(() => {
    emit("remove", true)
  }, 300) // same as css opacity transition
}

function onClickItem(itemName) {
  emit("clickItem", itemName)
  hideAndEmit()
}

</script>

<template>
  <div v-if="useBackground">
    <div class="background" @click="hideAndEmit">
    </div>

  </div>
  <div class="click-menu" :style="`top: ${props.top || 0}px; left: ${props.left || 0}px; opacity: ${opacity};`">
    <div class="click-menu-item" v-for="menu_item in menu_items" @click="onClickItem(menu_item)">
      <div :class="'click-menu-icon item-color-' + menu_item.color">
        <component :is="menu_item.icon"></component>
      </div>
      <div :class="'item-color-' + menu_item.color">
        <p>
          {{ menu_item.text }}
        </p>
      </div>

    </div>
  </div>

</template>

<style scoped>
.click-menu {
  position: absolute;
  background-color: var(--background-color-2);
  border-radius: 20px;
  padding-top: 20px;
  padding-bottom: 20px;
  transition: opacity 0.3s ease;
}

.click-menu-item {
  height: 60px;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 20px;
  padding-right: 20px;
  color: var(--font-color-white);
  user-select: none;
}

.click-menu-item:hover {
  background-color: #ffffff15;
}

.click-menu-icon {
  width: 35px;
  height: 35px;
  margin-right: 5px;
}

.click-menu-item p {
  font-size: 20px;
  margin: 0;
}

svg {
  width: 35px;
}

.item-color-white {
  stroke: var(--white);
  color: var(--white);
}

.item-color-red {
  stroke: var(--red);
  color: var(--red);
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #00000000;
}
</style>
