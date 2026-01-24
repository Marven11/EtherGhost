<template>
  <div class="session-type-dot">
    <div :data-type="type"></div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  type: {
    type: String,
    required: true
  }
});
</script>

<style scoped>
.session-type-dot {
  width: 1rem;
  height: 1rem;
  margin-right: 0;
}

.session-type-dot div {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 20px;
  margin: 0.25rem;
  margin-left: 0rem;
  background-color: var(--white);
}

.session-type-dot div[data-type="ONELINE_PHP"],
.session-type-dot div[data-type="BEHINDER_PHP_AES"],
.session-type-dot div[data-type="BEHINDER_PHP_XOR"] {
  background-color: var(--color-php);
}

.session-type-dot div[data-type="ONELINE_JSP"],
.session-type-dot div[data-type="BEHINDER_JSP_AES"] {
  background-color: var(--color-java);
}

.session-type-dot div[data-type="LINUX_CMD_ONELINER"] {
  background-color: var(--color-shell);
}
</style>