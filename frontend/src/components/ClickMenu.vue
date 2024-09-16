<script setup>
import { ref, shallowRef, watch } from "vue"


const props = defineProps(["mouse_x", "mouse_y", "menuItems"])

const emit = defineEmits(["remove", "clickItem", "rightClickItem"])

// An item is sth like this:
// {
//     "name": "open_terminal",
//     "text": "打开终端",
//     "icon": IconTerminal,
//     "color": "white",
//   },

const clickMenu = ref(null)

const menuTop = ref(props.mouse_y || 0)
const menuLeft = ref(props.mouse_x || 0)

const menuItems = shallowRef([...props.menuItems])

watch(clickMenu, () => {
  if (menuLeft.value + clickMenu.value.clientWidth > screen.width) {
    menuLeft.value -= (menuLeft.value + clickMenu.value.clientWidth - screen.width)
  }
  if (menuTop.value + clickMenu.value.clientHeight > screen.height) {
    menuTop.value -= (menuTop.value + clickMenu.value.clientHeight - screen.height)
  }
  console.log(menuTop.value)
})

</script>

<template>
  <div class="background" @click="emit('remove', true)" @click.right.prevent="emit('remove', true)">
  </div>
  <div class="click-menu" :style="`top: ${menuTop}px; left: ${menuLeft}px; `" ref="clickMenu">
    <div class="click-menu-item" v-for="menuItem in menuItems"
      @click="emit('clickItem', menuItem); emit('remove', true)"
      @click.right.prevent="e => { emit('rightClickItem', e, menuItem); emit('remove', true) }">
      <div class="click-menu-icon" :color="menuItem.color">
        <component :is="menuItem.icon"></component>
      </div>
      <div class="menu-item" :color="menuItem.color">
        <p>
          {{ menuItem.text }}
        </p>
      </div>

    </div>
  </div>

</template>

<style scoped>
.click-menu {
  position: absolute;
  background-color: var(--background-color-hover);
  border-radius: 20px;
  padding-top: 20px;
  padding-bottom: 20px;
  box-shadow: 0 0 15px rgba(15, 15, 15, 0.3);
  backdrop-filter: blur(20px);
}

.click-menu-item {
  height: 3rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 1rem;
  padding-right: 1rem;
  color: var(--font-color-primary);
  user-select: none;
  transition: background 0.3s ease;
}

.click-menu-item:hover {
  background-color: #00000015;
}

.click-menu-icon {
  width: 2rem;
  height: 2rem;
  margin-right: 10px;
}

.click-menu-item p {
  font-size: 1rem;
  margin: 0;
}

*[color="white"] {
  stroke: var(--font-color-primary);
  color: var(--font-color-primary);
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
