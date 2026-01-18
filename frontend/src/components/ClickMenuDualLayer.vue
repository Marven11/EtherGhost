<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"

const props = defineProps({
  mouse_x: { type: Number, default: 0 },
  mouse_y: { type: Number, default: 0 },
  menuItems: { type: Array, required: true },
  show: { type: Boolean, default: false }
})

const emit = defineEmits(["close", "select"])

// 菜单项数据结构：
// {
//   name: string,           // 唯一标识
//   text: string,           // 显示文本
//   icon: Component,        // Vue组件图标
//   color: 'white' | 'red' | string, // 颜色
//   children?: MenuItem[],  // 子菜单项（可选）
//   action?: () => void,    // 点击执行的动作（如果没有children）
// }

const clickMenu = ref(null)
const menuTop = ref(props.mouse_y || 0)
const menuLeft = ref(props.mouse_x || 0)

// 跟踪哪些菜单项是展开的
const expandedItems = ref(new Set())

// 调整菜单位置，避免超出屏幕
function adjustPosition() {
  if (!clickMenu.value) return
  
  const menuRect = clickMenu.value.getBoundingClientRect()
  const screenWidth = window.innerWidth
  const screenHeight = window.innerHeight
  
  if (menuLeft.value + menuRect.width > screenWidth) {
    menuLeft.value -= (menuLeft.value + menuRect.width - screenWidth)
  }
  
  if (menuTop.value + menuRect.height > screenHeight) {
    menuTop.value -= (menuTop.value + menuRect.height - screenHeight)
  }
}

// 点击菜单项
function handleItemClick(item, event) {
  event.stopPropagation()
  console.log('点击菜单项:', item.text, '有children:', !!(item.children && item.children.length > 0))
  
  if (item.children && item.children.length > 0) {
    // 有子菜单：切换展开状态
    console.log('切换展开状态，当前expandedItems:', Array.from(expandedItems.value))
    console.log('item.name:', item.name, '是否在expandedItems中:', expandedItems.value.has(item.name))
    
    const newSet = new Set(expandedItems.value)
    if (newSet.has(item.name)) {
      newSet.delete(item.name)
      console.log('移除展开状态:', item.name)
    } else {
      newSet.add(item.name)
      console.log('添加展开状态:', item.name)
    }
    
    // 使用新的Set来确保响应式更新
    expandedItems.value = newSet
    
    console.log('更新后expandedItems:', Array.from(expandedItems.value))
    
    // 需要重新调整位置，因为展开后高度变化
    setTimeout(() => {
      console.log('调整位置，当前菜单元素:', clickMenu.value)
      adjustPosition()
      // 检查二级菜单是否应该显示
      const shouldShowSubmenu = expandedItems.value.has(item.name)
      console.log('二级菜单应显示:', shouldShowSubmenu)
      if (shouldShowSubmenu) {
        const submenu = document.querySelector('.submenu')
        console.log('找到二级菜单元素:', !!submenu)
      }
    }, 0)
  } else if (item.action) {
    // 没有子菜单但有action：执行并关闭
    item.action()
    emit("select", item)
    emit("close")
  } else {
    // 默认行为：发送select事件
    emit("select", item)
    emit("close")
  }
}

// 点击子菜单项
function handleChildItemClick(childItem, parentItem, event) {
  event.stopPropagation()
  
  if (childItem.action) {
    childItem.action()
  }
  emit("select", childItem)
  emit("close")
}

// 点击背景关闭菜单
function handleBackgroundClick() {
  emit("close")
}

// 点击右键也关闭菜单
function handleBackgroundRightClick(event) {
  event.preventDefault()
  emit("close")
}

// 监听点击外部关闭
function handleClickOutside(event) {
  if (clickMenu.value && !clickMenu.value.contains(event.target)) {
    emit("close")
  }
}

// 初始调整位置
onMounted(() => {
  setTimeout(adjustPosition, 0)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

</script>

<template>
  <div v-if="show">
    <!-- 背景层，点击关闭 -->
    <div class="background" 
         @click="handleBackgroundClick" 
         @click.right.prevent="handleBackgroundRightClick">
    </div>
    
    <!-- 菜单主体 -->
    <div class="click-menu" 
         :style="`top: ${menuTop}px; left: ${menuLeft}px;`" 
         ref="clickMenu">
      
      <div v-for="item in menuItems" :key="item.name" class="menu-item-container">
        <!-- 一级菜单项 -->
        <div class="click-menu-item" 
             :class="{ 'has-children': item.children && item.children.length > 0, 'expanded': expandedItems.has(item.name) }"
             @click="handleItemClick(item, $event)"
             @click.right.prevent="handleItemClick(item, $event)">
          <div class="click-menu-icon" :color="item.color">
            <component :is="item.icon"></component>
          </div>
          <div class="menu-item-text" :color="item.color">
            <p>{{ item.text }}</p>
          </div>
          <!-- 如果有子菜单，显示展开指示器 -->
          <div v-if="item.children && item.children.length > 0" class="expand-indicator">
            ▶
          </div>
        </div>
        
        <!-- 二级子菜单 -->
        <transition name="submenu">
          <div v-if="item.children && item.children.length > 0 && expandedItems.has(item.name)" 
               class="submenu">
            <div v-for="child in item.children" 
                 :key="child.name" 
                 class="submenu-item"
                 @click="handleChildItemClick(child, item, $event)"
                 @click.right.prevent="handleChildItemClick(child, item, $event)">
              <div class="click-menu-icon" :color="child.color">
                <component :is="child.icon"></component>
              </div>
              <div class="menu-item-text" :color="child.color">
                <p>{{ child.text }}</p>
              </div>
            </div>
          </div>
        </transition>
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
  z-index: 1000;
  min-width: 200px;
}

.menu-item-container {
  position: relative;
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
  cursor: pointer;
  position: relative;
}

.click-menu-item:hover {
  background-color: #00000015;
}

.click-menu-item.expanded {
  background-color: #00000010;
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

.expand-indicator {
  margin-left: auto;
  font-size: 0.8rem;
  opacity: 0.6;
  transition: transform 0.2s ease;
}

.click-menu-item.expanded .expand-indicator {
  transform: rotate(90deg);
}

.submenu {
  background-color: #00000040;
  border-radius: 10px;
  margin: 5px 10px;
  overflow: hidden;
}

.submenu-item {
  height: 2.8rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 1rem;
  padding-right: 1rem;
  color: var(--font-color-primary);
  user-select: none;
  transition: background 0.3s ease;
  cursor: pointer;
}

.submenu-item:hover {
  background-color: #00000030;
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
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #00000000;
  z-index: 999;
}

.menu-item-text {
  flex-grow: 1;
}

.submenu-enter-active, .submenu-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.submenu-enter-from, .submenu-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.submenu-enter-to, .submenu-leave-from {
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}
</style>