<template>
  <div 
    class="status-indicator" 
    :class="status"
    :title="status === 'pending' ? '未开始' : status === 'executing' ? '执行中' : status === 'success' ? '成功' : '失败'"
  ></div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  status: {
    type: String,
    default: 'pending',
    validator: (value) => ['pending', 'executing', 'success', 'error'].includes(value)
  }
});
</script>

<style scoped>
.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-bottom: 6px;
  position: relative;
}

.status-indicator.pending {
  background-color: transparent;
  border: 2px solid var(--font-color-secondary);
  opacity: 0.4;
}

.status-indicator.executing {
  background-color: var(--yellow);
  animation: subtle-pulse 1.5s infinite;
  box-shadow: 0 0 6px rgba(255, 193, 7, 0.5);
}

.status-indicator.success {
  background-color: var(--green);
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.4);
}

.status-indicator.error {
  background-color: var(--red);
  box-shadow: 0 0 8px rgba(244, 67, 54, 0.4);
}

@keyframes subtle-pulse {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}
</style>