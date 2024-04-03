<script setup>
import IconOthers from "./icons/iconOthers.vue"
</script>

<template>
  <div class="card">
    <div class="card-top">
      <div class="card-name">
        <p>
          测试webshell
        </p>
      </div>
      <div>
        <IconOthers />
      </div>
    </div>
    <div class="card-bottom">
      <div class="card-note">
        测试测试
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  height: 160px;
  width: 30%;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  padding-left: 20px;
  padding-right: 20px;
  border-radius: 20px;
  font-family: 'Courier New', Courier, monospace;
}

.card-top {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
  height: 40%;
}

.card-top p, .card-top svg {
  margin: 0px;
  margin-top: 20px;
}

.card-top p {
  font-size: 20px;
  font-weight: bold;
}

.card-bottom {
  color: var(--font-color-grey);
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
