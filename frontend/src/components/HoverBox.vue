<script setup>

</script>

<template>
  <div class="hover-box-main">
    <slot></slot>
  </div>
</template>

<style scoped>
.hover-box-main {
  position: absolute;
  left: 25%;
  top: 97%;
  width: 50%;
  height: 80%;
  background-color: var(--background-color-hover);
  border-radius: 20px;
  transition: all 0.5s ease;
}

.hover-box-main:hover {
  top: 60%;
}
</style>
