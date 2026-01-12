<script setup lang="ts">
import { RouterView } from 'vue-router';
import Navbar from './components/Navbar.vue';
</script>

<template>
  <div>
    <Navbar />
    <RouterView class="bg-slate-900 min-h-screen"/>
  </div>
</template>

<style scoped>
</style>