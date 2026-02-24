<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import {
  fetchItems,
  fetchTemplates,
  generateLabels,
} from "./api/backend"

interface GenericItem {
  id: string
  name: string
  location?: string
  barcode?: string
  extra?: Record<string, any>
}

const items = ref<GenericItem[]>([])
const templates = ref<string[]>([])
const selectedTemplate = ref<string>("")

const selectedIds = ref<string[]>([])
const searchQuery = ref("")
const pdfUrl = ref<string | null>(null)

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    items.value = await fetchItems()
    templates.value = await fetchTemplates()

    if (templates.value.length > 0) {
      selectedTemplate.value = templates.value[0]
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
    item.name.toLowerCase().includes(q) ||
    (item.location?.toLowerCase().includes(q)) ||
    (item.barcode?.toLowerCase().includes(q))
  )
})

const allSelected = computed({
  get() {
    return (
      filteredItems.value.length > 0 &&
      selectedIds.value.length === filteredItems.value.length
    )
  },
  set(value: boolean) {
    if (value) {
      selectedIds.value = filteredItems.value.map(i => i.id)
    } else {
      selectedIds.value = []
    }
  },
})

async function handleGenerate() {
  if (
    selectedIds.value.length === 0 ||
    !selectedTemplate.value
  ) return

  try {
    const blob = await generateLabels(
      selectedIds.value,
      selectedTemplate.value
    )

    pdfUrl.value = URL.createObjectURL(blob)

  } catch (err: any) {
    alert("Error generating labels: " + err)
  }
}

function closePreview() {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
  pdfUrl.value = null
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-5xl mx-auto bg-white shadow rounded-lg p-6">

      <h1 class="text-2xl font-bold mb-6">
        Label App
      </h1>

      <div v-if="loading" class="text-gray-500">
        Loading...
      </div>

      <div v-else-if="error" class="text-red-600">
        Error: {{ error }}
      </div>

      <div v-else>

        <!-- Top controls -->
        <div class="flex justify-between items-center mb-4 gap-4">

          <!-- Template selector -->
          <select
            v-model="selectedTemplate"
            class="border px-3 py-2 rounded bg-white"
          >
            <option
              v-for="template in templates"
              :key="template"
              :value="template"
            >
              {{ template }}
            </option>
          </select>

          <!-- Generate button -->
          <button
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            :disabled="
              selectedIds.length === 0 ||
              !selectedTemplate
            "
            @click="handleGenerate"
          >
            Generate Labels
          </button>
        </div>

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Zoek op naam, locatie of barcode..."
          class="border px-3 py-2 rounded w-full mb-4"
        />

        <!-- Selected counter -->
        <div class="text-sm text-gray-600 mb-4">
          {{ selectedIds.length }} geselecteerd
        </div>

        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full border border-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="p-3 border text-center">
                  <input
                    type="checkbox"
                    v-model="allSelected"
                  />
                </th>
                <th class="p-3 text-left border">Name</th>
                <th class="p-3 text-left border">Location</th>
                <th class="p-3 text-left border">Barcode</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="item in filteredItems"
                :key="item.id"
                class="hover:bg-gray-50"
              >
                <td class="p-3 border text-center">
                  <input
                    type="checkbox"
                    :value="item.id"
                    v-model="selectedIds"
                  />
                </td>
                <td class="p-3 border">
                  {{ item.name }}
                </td>
                <td class="p-3 border">
                  {{ item.location }}
                </td>
                <td class="p-3 border">
                  {{ item.barcode }}
                </td>
              </tr>
            </tbody>

          </table>
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
          <a
            :href="pdfUrl"
            download="labels.pdf"
            class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Download
          </a>

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