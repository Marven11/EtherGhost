<script setup>
import { ref, shallowRef, defineEmits } from "vue"
import IconCross from "./icons/iconCross.vue"
import IconCheck from "./icons/iconCheck.vue"
import IconWarning from "./icons/iconWarning.vue"
import IconPlus from "./icons/iconPlus.vue"
import { doAssert } from "@/assets/utils"

const POPUP_SHOW_TIME = 5000;

const popups = ref([

])

function getPopup(id) {
  const selectedPopups = popups.value.filter(popup => popup.id == id)
  if (selectedPopups.length == 0) {
    return undefined
  }
  doAssert(selectedPopups.length == 1, "Multiple popups with same id")
  return selectedPopups[0]
}


function addPopup(color, title, message) {
  const id = Date.now()
  const popup = {
    id,
    color,
    title,
    message,
    state: "show"
  }
  popups.value.push(popup)

  setTimeout(() => {
    let popup = getPopup(id)
    if (popup) {
      popup.state = "hide"
    }
  }, POPUP_SHOW_TIME)
  setTimeout(() => {
    const idx = popups.value.find(popup => popup.id == id)
    if(idx > -1) {
      popups.splice(idx, 1)
    } 
  }, POPUP_SHOW_TIME + 2000)
}

defineExpose({ addPopup })

</script>

<template>
  <div class="popups" v-if="popups.length != 0">
    <div class="popup" v-for="popup in popups" :color="popup.color" :state="popup.state">
      <div class="popup-title-line">
        <div class="popup-icon">
          <IconCross v-if="popup.color == 'red'" />
          <IconWarning v-else-if="popup.color == 'yellow'" />
          <IconCheck v-else-if="popup.color == 'green'" />
          <IconPlus v-else-if="popup.color == 'blue'" />
        </div>
        <h3 class="popup-title">
          {{ popup.title }}
        </h3>
      </div>

      <p class="popup-message">
        {{ popup.message }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.popups {
  position: fixed;
  bottom: 0;
  right: 5%;
  width: 20%;
  min-width: 300px;
}

.popup {
  background-color: #00000015;
  border-radius: 20px;
  margin-bottom: 20px;
  height: 12lvh;
  transition: opacity 0.5s ease;
}

.popup, .popup * {
  animation: slide-in 0.5s ease-in-out;
}

.popup[color="red"] {
  background-color: var(--red);
}

.popup[color="yellow"] {
  background-color: var(--yellow);
}

.popup[color="green"] {
  background-color: var(--green);
}

.popup[color="blue"] {
  background-color: var(--blue);
}


.popup[state=show] {
  opacity: 1;
}

.popup[state=hide],
.popup[state=hide] * {
  opacity: 0;
}

.popup-title-line {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.popup-icon {
  margin-top: 20px;
  margin-left: 20px;
  margin-right: 10px;
  margin-bottom: 0px;

}

.popup-title {
  font-size: 24px;
  margin: 0;
  margin-bottom: 10px;
  margin-top: 20px;
}

.popup-message {
  margin: 0px 20px 0px;
}

@keyframes slide-in {
  0% {
    opacity: 0;
    height: 0;
  }

  100% {
    opacity: 1;
  }
}

svg {
  height: 30px;
  stroke: var(--font-color-black);
}
</style>
