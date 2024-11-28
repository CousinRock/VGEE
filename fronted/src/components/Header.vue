<template>
    <header class="header">
        <nav class="nav-menu">
            <Tools ref="toolsRef" :map-view="mapView" />
        </nav>
    </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Tools from './Tools.vue'

const props = defineProps({
    mapView: {
        type: Object,
        required: true
    }
})

const toolsRef = ref(null)

// 点击外部关闭菜单
const handleClickOutside = (event) => {
    const header = document.querySelector('.header')
    if (header && !header.contains(event.target)) {
        toolsRef.value?.closeAllMenus()
    }
}

onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style src="../styles/header.css"></style>
