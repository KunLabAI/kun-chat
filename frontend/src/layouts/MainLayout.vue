<template>
  <div class="layout-container">
    <Notification />
    <Sidebar />
    <main class="main-content">
      <div class="responsive-container">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<style>
@import '@/styles/MainLayout.css';
</style>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Notification from '@/components/common/Notification.vue'
</script>
