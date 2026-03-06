<script setup lang="ts">
import { ref, onMounted, computed } from "vue"

const API_BASE = "http://localhost:8000"

interface Item {
  id: number
  name: string
  location?: string
  barcode?: string
}

const items = ref<Item[]>([])
const templates = ref<string[]>([])
const selectedTemplate = ref<string>("")

const selectedIds = ref<number[]>([])
const searchQuery = ref("")
const pdfUrl = ref<string | null>(null)

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const itemsResponse = await fetch("http://localhost:8005/items") // <-- grocy items endpoint
    items.value = await itemsResponse.json()

    const templateResponse = await fetch(`${API_BASE}/templates`)
    templates.value = await templateResponse.json()

    if (templates.value.length > 0) {
      selectedTemplate.value = templates.value[0] || ""
    }

  } catch (err: any) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

const filteredItems = computed(() => {
  if (!searchQuery.value) return items.value

  const q = searchQuery.value.toLowerCase()

  return items.value.filter(item =>
    item.name.toLowerCase().includes(q)
  )
})

async function handleGenerate() {

  if (!selectedIds.value.length || !selectedTemplate.value) return

  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      service: "grocy",
      action: "products",
      template: selectedTemplate.value,
      payload: {
        product_ids: selectedIds.value
      }
    })
  })

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
    <div class="max-w-6xl mx-auto bg-white shadow rounded-lg p-6">

      <h1 class="text-2xl font-bold mb-6">Grocy Labels</h1>

      <div v-if="loading">Loading...</div>
      <div v-else-if="error" class="text-red-600">Error: {{ error }}</div>

      <div v-else>

        <!-- Template + Button -->
        <div class="flex justify-between mb-4">
          <select v-model="selectedTemplate" class="border px-3 py-2 rounded">
            <option v-for="t in templates" :key="t" :value="t">
              {{ t }}
            </option>
          </select>

          <button
            @click="handleGenerate"
            class="bg-blue-600 text-white px-4 py-2 rounded"
            :disabled="!selectedIds.length"
          >
            Preview
          </button>
        </div>

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="border px-3 py-2 rounded w-full mb-4"
        />

        <!-- Table -->
        <table class="min-w-full border">
          <thead>
            <tr>
              <th></th>
              <th>Name</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <input
                  type="checkbox"
                  :value="item.id"
                  v-model="selectedIds"
                />
              </td>
              <td>{{ item.name }}</td>
            </tr>
          </tbody>
        </table>

      </div>
    </div>
  </div>

  <!-- PDF Modal -->
  <div
    v-if="pdfUrl"
    class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center"
  >
    <div class="bg-white w-4/5 h-4/5 rounded flex flex-col">

      <div class="flex justify-between p-4 border-b">
        <h2 class="font-bold">Preview</h2>
        <button @click="closePreview">Close</button>
      </div>

      <iframe :src="pdfUrl" class="flex-1 w-full"></iframe>
    </div>
  </div>
</template>