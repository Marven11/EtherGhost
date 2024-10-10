<script setup>
import { getCurrentApiUrl, getDataOrPopupError } from '@/assets/utils';
import { ref } from 'vue';

const version = ref("Unknown Version")

setTimeout(async () => {
  let serverVersion = await getDataOrPopupError("/utils/version")
  version.value = `v${serverVersion}`
}, 0)

</script>

<template>
  <div class="info-main">
    <div class="info-panel shadow-box">
      <!-- TODO: 把这个界面做得更美观一点 -->
      <h1>游魂</h1>
      <p>{{ version }}</p>
      <p>
        <a href="https://github.com/Marven11/EtherGhost">Github</a>
        | <a href="https://github.com/Marven11/EtherGhost/issues">漏洞报告与功能建议</a>
      </p>
    </div>

  </div>
</template>

<style scoped>
.info-main {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-panel {
  background-color: var(--background-color-2);
  height: max-content;
  width: 30%;
  border-radius: 20px;
  color: var(--font-color-secondary);
  padding: 20px;
}

.info-panel h1 {
  color: var(--font-color-primary);

}

.info-value {
  font-weight: bold;
  color: var(--font-color-primary);
}
</style>