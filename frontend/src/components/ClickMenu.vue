<script setup>
import { ref, shallowRef } from "vue"


const props = defineProps(["top", "left", "menuItems"])

const emit = defineEmits(["remove", "clickItem"])

// An item is sth like this:
// {
//     "name": "open_terminal",
//     "text": "打开终端",
//     "icon": IconTerminal,
//     "color": "white",
//   },
const menuItems = shallowRef([...props.menuItems])

function hideAndEmit() {
  emit("remove", true)
}

function onClickItem(itemName) {
  emit("clickItem", itemName)
  hideAndEmit()
}

</script>

<template>
  <div class="background" @click="hideAndEmit" @click.right="e => { e.preventDefault(); hideAndEmit() }">
  </div>
  <div class="click-menu" :style="`top: ${props.top || 0}px; left: ${props.left || 0}px; `">
    <div class="click-menu-item" v-for="menu_item in menuItems" @click="onClickItem(menu_item)"
      @click.right="e => { e.preventDefault(); hideAndEmit() }">
      <div class="click-menu-icon" :color="menu_item.color">
        <component :is="menu_item.icon"></component>
      </div>
      <div class="menu-item" :color="menu_item.color">
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
  background-color: var(--background-color-grey);
  border-radius: 20px;
  padding-top: 20px;
  padding-bottom: 20px;
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

*[color="white"] {
  stroke: var(--white);
  color: var(--white);
}

*[color="red"] {
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
