<template>
  <main class="min-h-screen p-6 md:p-10">
    <div class="mx-auto max-w-6xl space-y-6">
      <header class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight text-slate-900">Label System</h1>
        <p class="text-slate-600">Frontend talks only to the backend service.</p>
      </header>

      <PMessage v-if="errorMessage" severity="error">{{ errorMessage }}</PMessage>

      <PCard>
        <template #title>
          <div class="flex items-center gap-2">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-white">1</span>
            <span>Select products</span>
          </div>
        </template>
        <template #content>
          <div class="space-y-4">
            <div class="flex flex-wrap items-center gap-3">
              <PButton
                label="Load Grocy Products"
                icon="pi pi-download"
                :loading="loadingProducts"
                @click="loadProducts"
              />

              <span v-if="products.length" class="text-sm text-slate-600">
                Loaded {{ products.length }} products
              </span>
            </div>

            <div class="grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
              <span class="p-input-icon-left block">
                <i class="pi pi-search" />
                <PInputText
                  v-model="searchTerm"
                  class="w-full"
                  placeholder="Search products by name"
                />
              </span>

              <div class="text-sm text-slate-700">
                Selected: <strong>{{ selectedIds.length }}</strong>
              </div>
            </div>

            <div class="max-h-[420px] overflow-auto rounded-lg border border-slate-200 bg-white">
              <table class="min-w-full border-collapse text-sm">
                <thead class="sticky top-0 bg-slate-100">
                  <tr>
                    <th class="w-14 p-3 text-left">Pick</th>
                    <th class="p-3 text-left">Name</th>
                    <th class="p-3 text-left">Id</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in filteredProducts"
                    :key="item.id"
                    class="border-t border-slate-100 hover:bg-slate-50"
                  >
                    <td class="p-3">
                      <PCheckbox
                        :binary="true"
                        :modelValue="selectedIdSet.has(item.id)"
                        @update:modelValue="toggleSelection(item.id, $event)"
                      />
                    </td>
                    <td class="p-3">{{ item.name }}</td>
                    <td class="p-3 text-slate-500">{{ item.id }}</td>
                  </tr>

                  <tr v-if="!filteredProducts.length">
                    <td class="p-4 text-center text-slate-500" colspan="3">No products found</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex justify-end">
              <PButton
                label="Next"
                icon="pi pi-arrow-right"
                iconPos="right"
                :disabled="!selectedIds.length"
                :loading="loadingNext"
                @click="goToTemplateStep"
              />
            </div>
          </div>
        </template>
      </PCard>

      <PCard>
        <template #title>
          <div class="flex items-center gap-2">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-white">2</span>
            <span>Choose template and generate</span>
          </div>
        </template>
        <template #content>
          <div class="space-y-4">
            <div class="grid gap-3 md:grid-cols-[1fr_auto_auto] md:items-end">
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">Template</label>
                <PSelect
                  v-model="selectedTemplate"
                  :options="templateOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                  placeholder="Select a template"
                  :disabled="!readyForTemplates"
                />
              </div>

              <PButton
                label="Generate"
                icon="pi pi-file-pdf"
                :disabled="!canGenerate"
                :loading="loadingGenerate"
                @click="generate"
              />

              <PButton
                label="Print"
                icon="pi pi-print"
                severity="secondary"
                :disabled="!pdfUrl"
                @click="printPdf"
              />
            </div>

            <div v-if="loadingGenerate" class="flex items-center gap-2 text-slate-600">
              <PProgressSpinner style="width: 24px; height: 24px" strokeWidth="6" />
              <span>Generating PDF...</span>
            </div>

            <div v-if="pdfUrl" class="overflow-hidden rounded-lg border border-slate-200 bg-white">
              <iframe :src="pdfUrl" class="h-[700px] w-full" title="Generated PDF"></iframe>
            </div>
          </div>
        </template>
      </PCard>
    </div>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { createCsv, fetchGrocyProducts, fetchTemplates, generatePdf } from './api'

const products = ref([])
const selectedIds = ref([])
const searchTerm = ref('')
const templates = ref([])
const selectedTemplate = ref(null)
const pdfUrl = ref('')
const readyForTemplates = ref(false)
const errorMessage = ref('')

const loadingProducts = ref(false)
const loadingNext = ref(false)
const loadingGenerate = ref(false)

const selectedIdSet = computed(() => new Set(selectedIds.value))

const filteredProducts = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()

  if (!term) {
    return products.value
  }

  return products.value.filter((item) => (item.name || '').toLowerCase().includes(term))
})

const selectedProducts = computed(() => {
  return products.value.filter((item) => selectedIdSet.value.has(item.id))
})

const templateOptions = computed(() => {
  return templates.value.map((templatePath) => ({
    label: templatePath,
    value: templatePath,
  }))
})

const canGenerate = computed(() => {
  return readyForTemplates.value && selectedProducts.value.length > 0 && !!selectedTemplate.value
})

function clearError() {
  errorMessage.value = ''
}

function setError(err) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    errorMessage.value = detail
    return
  }

  if (typeof err?.message === 'string' && err.message.trim()) {
    errorMessage.value = err.message
    return
  }

  errorMessage.value = 'Unexpected error'
}

function normalizeProduct(item) {
  return {
    id: item.id,
    name: item.name || `Product ${item.id}`,
    location: item.location || item.location_name || '',
    barcode: item.barcode || null,
  }
}

async function loadProducts() {
  clearError()
  loadingProducts.value = true

  try {
    const data = await fetchGrocyProducts()
    products.value = Array.isArray(data) ? data.map(normalizeProduct) : []
    selectedIds.value = []
    templates.value = []
    selectedTemplate.value = null
    readyForTemplates.value = false

    if (pdfUrl.value) {
      URL.revokeObjectURL(pdfUrl.value)
      pdfUrl.value = ''
    }
  } catch (err) {
    setError(err)
  } finally {
    loadingProducts.value = false
  }
}

function toggleSelection(id, checked) {
  if (checked) {
    if (!selectedIdSet.value.has(id)) {
      selectedIds.value = [...selectedIds.value, id]
    }
    return
  }

  selectedIds.value = selectedIds.value.filter((v) => v !== id)
}

async function goToTemplateStep() {
  if (!selectedProducts.value.length) {
    return
  }

  clearError()
  loadingNext.value = true

  try {
    await createCsv(selectedProducts.value)

    const templatesData = await fetchTemplates()
    templates.value = Array.isArray(templatesData) ? templatesData : []
    selectedTemplate.value = templates.value[0] || null
    readyForTemplates.value = true
  } catch (err) {
    setError(err)
  } finally {
    loadingNext.value = false
  }
}

async function generate() {
  if (!canGenerate.value) {
    return
  }

  clearError()
  loadingGenerate.value = true

  try {
    const blob = await generatePdf(selectedProducts.value, selectedTemplate.value)

    if (pdfUrl.value) {
      URL.revokeObjectURL(pdfUrl.value)
    }

    pdfUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    setError(err)
  } finally {
    loadingGenerate.value = false
  }
}

function printPdf() {
  if (!pdfUrl.value) {
    return
  }

  const printWindow = window.open(pdfUrl.value, '_blank')
  if (!printWindow) {
    errorMessage.value = 'Could not open print window. Please allow popups.'
    return
  }

  printWindow.onload = () => {
    printWindow.focus()
    printWindow.print()
  }
}

onBeforeUnmount(() => {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
})
</script>
