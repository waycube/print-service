<script setup lang="ts">
import { onMounted, ref, computed } from "vue"
import { useRouter } from "vue-router"

interface GenericItem {
  id: number
  name: string
  location?: string
  barcode?: string
}

const router = useRouter()

// ✅ Alleen backend aanspreken
const API_BASE = import.meta.env.VITE_API_BASE

const items = ref<GenericItem[]>([])
const templates = ref<string[]>([])
const selectedTemplate = ref<string>("")

const selectedIds = ref<number[]>([])
const searchQuery = ref("")
const pdfUrl = ref<string | null>(null)

const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    // Backend haalt zelf data uit grocy-service
    const itemsResponse = await fetch(`${API_BASE}/grocy/items`)
    items.value = await itemsResponse.json()

    const templateResponse = await fetch(`${API_BASE}/templates`)
    const allTemplates = await templateResponse.json()

    // Alleen grocy templates
    templates.value = allTemplates.filter((t: string) =>
      t.startsWith("grocy/")
    )

    if (templates.value.length > 0) {
      selectedTemplate.value = templates.value[0] ?? ""
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
    item.location?.toLowerCase().includes(q) ||
    item.barcode?.toLowerCase().includes(q)
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
  if (!selectedIds.value.length || !selectedTemplate.value) return

  try {
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

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const blob = await response.blob()
    pdfUrl.value = URL.createObjectURL(blob)

  } catch (err: any) {
    alert("Error generating labels: " + err.message)
  }
}

async function handlePrint() {
  if (!selectedIds.value.length || !selectedTemplate.value) return

  try {
    const response = await fetch(`${API_BASE}/print`, {
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

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    alert("Sent to printer")

  } catch (err: any) {
    alert("Print error: " + err.message)
  }
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
    <div class="max-w-6xl mx-auto bg-white shadow rounded-lg p-6">

      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">
          Grocy Labels
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

        <!-- Top controls -->
        <div class="flex justify-between items-center mb-4 gap-4">

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

          <div class="flex gap-2">
            <button
              @click="handleGenerate"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              :disabled="!selectedIds.length"
            >
              Preview
            </button>

            <button
              @click="handlePrint"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              :disabled="!selectedIds.length"
            >
              Print
            </button>
          </div>

        </div>

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Zoek op naam, locatie of barcode..."
          class="border px-3 py-2 rounded w-full mb-4"
        />

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
                <td class="p-3 border">{{ item.name }}</td>
                <td class="p-3 border">{{ item.location }}</td>
                <td class="p-3 border">{{ item.barcode }}</td>
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