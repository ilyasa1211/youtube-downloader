<script setup lang="ts">
import { Icon } from "@iconify/vue";
import { ref } from "vue";

type DownloadResponse = {
  redirect: string;
};
type DownloadPayload = {
  url: string;
  format: string;
};

const urlInput = ref<string>("");
const processing = ref<boolean>(false);

const baseUrl = new URL("http://localhost:8080");

async function handleClick() {
  if (urlInput.value.trim() === "") {
    alert("Please enter a valid YouTube URL.");
    return;
  }

  processing.value = true;

  const url = baseUrl.origin + "/download";

  const payload: DownloadPayload = {
    url: urlInput.value,
    format: "mp4",
  };

  const result = await fetch(url, {
    body: JSON.stringify(payload),
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      return response.json() as Promise<DownloadResponse>;
    })
    .catch((error) => {
      return error as Promise<Error>;
    });

  processing.value = false;

  if (result instanceof Error) {
    alert("An error occurred while processing your request. Please try again.");
  } else {
    location.href = baseUrl.origin + result.redirect;
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-slate-900 text-gray-400 px-4">
    <div class="max-w-xl flex flex-col gap-3 justify-center mb-20">
      <h1 class="text-6xl text-center font-extrabold text-white">Download YouTube Videos Instantly</h1>
      <p class="text-gray-400 text-xl text-center">Convert and download YouTube videos in MP4, MP3, and other formats
        without any software installation.</p>
      <div
        class="flex items-center justify-between my-6 border border-gray-600 shadow-lg shadow-blue-600/30 rounded-xl">
        <label for="url-input" class="px-6">
          <Icon icon="material-symbols:link" width="24" height="24" class="" />
        </label>
        <input type="text" v-model="urlInput" id="url-input" placeholder="Paste YouTube link here..."
          class="grow py-4 rounded-l-xl outline-none" />
        <button type="button" @click="handleClick" :disabled="processing"
          :class="[processing ? 'bg-gray-700 cursor-wait' : 'bg-blue-500 hover:bg-blue-800']"
          class="flex items-center gap-2 px-6 py-4 rounded-r-xl font-bold text-white">
          <p>Proceed</p>
          <Icon icon="material-symbols:arrow-circle-right-outline-rounded" width="24" height="24" />
        </button>
      </div>
      <div class="flex gap-8 justify-center text-sm text-white">
        <div class="flex items-center gap-2">
          <Icon icon="material-symbols:check-circle" width="24" height="24" />
          <p>NO REGISTRATION</p>
        </div>
        <div class="flex items-center gap-2">
          <Icon icon="material-symbols:check-circle" width="24" height="24" />
          <p>100% FREE</p>
        </div>
        <div class="flex items-center gap-2">
          <Icon icon="material-symbols:check-circle" width="24" height="24" />
          <p>OPEN SOURCE</p>
        </div>
        <div class="flex items-center gap-2">
          <Icon icon="material-symbols:check-circle" width="24" height="24" />
          <p>TRUSTED</p>
        </div>
      </div>
    </div>
  </div>
</template>