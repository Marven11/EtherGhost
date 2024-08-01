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
    <div class="info-panel">
      <h1>对接蚁剑</h1>
      <p>使用以下信息让蚁剑通过游魂连接webshell</p>
      <table>
        <tr>
          <td>地址</td>
          <td>{{ getCurrentApiUrl() }}/session/{{ props.session }}/emulated_antsword</td>
        </tr>
        <tr>
          <td>密码</td>
          <td>as</td>
        </tr>
      </table>
      <p>就这么多了</p>
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
  background-color: var(--background-color-1);
  height: 30%;
  width: 50%;
  border-radius: 20px;
  color: var(--font-color-grey);
  padding: 20px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}

.info-panel h1 {
  color: var(--font-color-white);

}

.info-panel table {
  width: 100%;
  font-size: 20px;
  color: var(--font-color-grey);
}

.info-panel td {
  min-width: 100px;
}
</style>