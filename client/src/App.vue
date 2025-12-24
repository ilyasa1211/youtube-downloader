<script setup lang="ts">
</script>

<template>
  <div class="page">
    <form
      class="card"
      action="http://localhost:8080/download"
      method="POST"
    >
      <h1>YouTube Downloader</h1>

      <label for="youtube-link">YouTube URL</label>

      <input
        type="text"
        name="url"
        id="youtube-link"
        placeholder="https://www.youtube.com/watch?v=..."
        required
      />

      <button type="submit">Download</button>
    </form>
  </div>
</template>

<style scoped>
/* Page layout */
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f2933, #111827);
  font-family: system-ui, sans-serif;
}

/* Card container */
.card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

/* Title */
h1 {
  margin: 0;
  text-align: center;
  font-size: 1.5rem;
  color: #111827;
}

/* Label */
label {
  font-size: 0.9rem;
  color: #374151;
}

/* Text input */
input[type="text"] {
  padding: 0.9rem 1rem;
  border-radius: 12px;
  border: 1px solid #d1d5db;
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input[type="text"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

/* Button */
button {
  margin-top: 0.5rem;
  padding: 0.9rem;
  border-radius: 12px;
  border: none;
  background: #3b82f6;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

button:hover {
  background: #2563eb;
}

button:active {
  transform: scale(0.98);
}
</style>

