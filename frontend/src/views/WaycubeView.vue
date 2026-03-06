<script setup lang="ts">
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const API_BASE = "http://127.0.0.1:8001/api/waycube"

const templates = ref<string[]>([])
const selectedTemplate = ref<string>("")
const pdfUrl = ref<string | null>(null)

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const response = await fetch(`${API_BASE}/templates`)
    templates.value = await response.json()

    if (templates.value.length > 0) {
      selectedTemplate.value = templates.value[0]
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

async function handleGenerate() {
  if (!selectedTemplate.value) return

  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      template: selectedTemplate.value
    })
  })

  const blob = await response.blob()
  pdfUrl.value = URL.createObjectURL(blob)
}

async function handlePrint() {
  if (!selectedTemplate.value) return

  await fetch(`${API_BASE}/print`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      template: selectedTemplate.value
    })
  })

  alert("Sent to printer")
}

function closePreview() {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
  pdfUrl.value = null
}

function goHome() {
  router.push("/")
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto bg-white shadow rounded-lg p-6">

      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">
          Waycube Labels
        </h1>

        <button
          @click="goHome"
          class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
        >
          Home
        </button>
      </div>

      <div v-if="loading" class="text-gray-500">
        Loading...
      </div>

      <div v-else-if="error" class="text-red-600">
        Error: {{ error }}
      </div>

      <div v-else>

        <div class="flex justify-between items-center mb-4 gap-4">

          <select
            v-model="selectedTemplate"
            class="border px-3 py-2 rounded bg-white w-full"
          >
            <option
              v-for="template in templates"
              :key="template"
              :value="template"
            >
              {{ template }}
            </option>
          </select>

          <div class="flex gap-2">
            <button
              @click="handleGenerate"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Preview
            </button>

            <button
              @click="handlePrint"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Print
            </button>
          </div>

        </div>

      </div>
    </div>
  </div>

  <!-- PDF Preview Modal -->
  <div
    v-if="pdfUrl"
    class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
  >
    <div class="bg-white w-4/5 h-4/5 rounded shadow-lg flex flex-col">

      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="font-bold">Label Preview</h2>

        <div class="flex gap-2">
          <button
            @click="handlePrint"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Print
          </button>

          <button
            @click="closePreview"
            class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Close
          </button>
        </div>
      </div>

      <iframe
        :src="pdfUrl"
        class="flex-1 w-full"
      />
    </div>
  </div>
</template>