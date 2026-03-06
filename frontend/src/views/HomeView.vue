<script setup lang="ts">
import { useRouter } from "vue-router"

const router = useRouter()

function goToGrocy() {
  router.push("/grocy")
}

function goToWaycube() {
  router.push("/waycube")
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100 gap-6">

    <h1 class="text-3xl font-bold mb-8">
      Waycube Label System
    </h1>

    <button
      @click="goToGrocy"
      class="bg-blue-600 text-white px-8 py-4 rounded text-xl hover:bg-blue-700"
    >
      Grocy Labels
    </button>

    <button
      @click="goToWaycube"
      class="bg-green-600 text-white px-8 py-4 rounded text-xl hover:bg-green-700"
    >
      Waycube Office Labels
    </button>

  </div>
</template>