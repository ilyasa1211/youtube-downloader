<script setup lang="ts">
</script>

<template>
  <form action="http://localhost:8080/download" method="POST">
    <label for="youtube-link">Link: </label>
    <input type="text" name="url" id="youtube-link">
    <input type="submit" value="Submit">
  </form>
</template>

<style scoped></style>
