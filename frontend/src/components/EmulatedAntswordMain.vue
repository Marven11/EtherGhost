<script setup>
import { store } from '@/assets/store';
import { getCurrentApiUrl } from '@/assets/utils';


const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
}

</script>

<template>
  <div class="info-main">
    <div class="info-panel shadow">
      <h1>对接蚁剑</h1>
      <p>使用以下信息让蚁剑通过游魂连接webshell</p>
      <table>
        <tr>
          <td>地址</td>
          <td class="info-value">{{ getCurrentApiUrl() }}/session/{{ props.session }}/emulated_antsword</td>
        </tr>
        <tr>
          <td>密码</td>
          <td class="info-value">as</td>
        </tr>
      </table>
      <p>可以让蚁剑的各类插件对接游魂，运行在冰蝎webshell上，享受游魂带来的各类特性</p>
      <p>暂时仅支持PHP webshell</p>
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
  width: 50%;
  border-radius: 20px;
  color: var(--font-color-secodary);
  padding: 20px;
}

.info-panel h1 {
  color: var(--font-color-primary);

}

.info-panel table {
  width: 100%;
  font-size: 20px;
  color: var(--font-color-secodary);
}

.info-panel td {
  min-width: 100px;
}

.info-value {
  font-weight: bold;
  color: var(--font-color-primary);
}
</style>