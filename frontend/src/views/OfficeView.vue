<script setup lang="ts">
import { ref, onMounted } from "vue"

const BACKEND_API = "http://backend:8000"

const templates = ref<string[]>([])
const selectedTemplate = ref<string>("")

const selectedAction = ref<"paid" | "fridge">("paid")

const pdfUrl = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const templateResponse = await fetch(`${BACKEND_API}/templates`)
    const allTemplates = await templateResponse.json()

    // Filter only office templates
    templates.value = allTemplates.filter((t: string) =>
      t.startsWith("office/")
    )

    if (templates.value.length > 0) {
      selectedTemplate.value = templates.value[0] || ""
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

async function handleGenerate() {

  if (!selectedTemplate.value) return

  const response = await fetch(`${BACKEND_API}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      service: "office",
      action: selectedAction.value,
      template: selectedTemplate.value,
      payload: {}
    })
  })

  if (!response.ok) {
    alert("Generation failed")
    return
  }

  const blob = await response.blob()
  pdfUrl.value = URL.createObjectURL(blob)
}

function closePreview() {
  if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value)
  pdfUrl.value = null
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto bg-white shadow rounded-lg p-6">

      <h1 class="text-2xl font-bold mb-6">Office Labels</h1>

      <div v-if="loading">Loading...</div>
      <div v-else-if="error" class="text-red-600">Error: {{ error }}</div>

      <div v-else>

        <!-- Action Selector -->
        <div class="mb-4">
          <label class="font-semibold mr-4">Label Type:</label>

          <select
            v-model="selectedAction"
            class="border px-3 py-2 rounded"
          >
            <option value="paid">Paid</option>
            <option value="fridge">Waycube Fridge</option>
          </select>
        </div>

        <!-- Template Selector -->
        <div class="mb-4">
          <label class="font-semibold mr-4">Template:</label>

          <select
            v-model="selectedTemplate"
            class="border px-3 py-2 rounded w-full"
          >
            <option
              v-for="template in templates"
              :key="template"
              :value="template"
            >
              {{ template }}
            </option>
          </select>
        </div>

        <!-- Generate Button -->
        <button
          @click="handleGenerate"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Preview Label
        </button>

      </div>
    </div>
  </div>

  <!-- PDF Modal -->
  <div
    v-if="pdfUrl"
    class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
  >
    <div class="bg-white w-4/5 h-4/5 rounded shadow-lg flex flex-col">

      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="font-bold">Preview</h2>

        <button
          @click="closePreview"
          class="bg-red-600 text-white px-4 py-2 rounded"
        >
          Close
        </button>
      </div>

      <iframe
        :src="pdfUrl"
        class="flex-1 w-full"
      />
    </div>
  </div>
</template>