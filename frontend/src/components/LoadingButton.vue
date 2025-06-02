<script setup>
import { ref, computed } from 'vue'
import IconRun from './icons/iconRun.vue';
import IconPause from './icons/iconPause.vue';
import IconLoad from './icons/iconLoad.vue';

const props = defineProps({
  status: {
    type: String,
    default: 'off', // 'on', 'off', 'loading'
    validator: v => ['on', 'off', 'loading'].includes(v)
  }
})

</script>

<template>
  <button class="loading-button" :class="props.status" :disabled="props.status === 'loading'">
    <IconRun v-if="props.status == 'off'"></IconRun>
    <IconPause v-if="props.status == 'on'"></IconPause>
    <IconLoad v-if="props.status == 'loading'"></IconLoad>
  </button>
</template>

<style scoped>
.loading-button {
  all: unset;
  width: 100%;
  height: 100%;

  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;

  transition: all 0.2s ease;
}

.loading-button.on {
  background-color: var(--green);
}

.loading-button.off {
  background-color: var(--red);
}

.loading-button.loading {
  background-color: var(--white);
}

svg {
  width: 70%;
  stroke: #000000;
}
</style>
