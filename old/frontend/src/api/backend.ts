const API_BASE = "http://127.0.0.1:8000"

export async function fetchItems() {
  const response = await fetch(`${API_BASE}/api/items`)
  return response.json()
}

export async function fetchTemplates() {
  const response = await fetch(`${API_BASE}/api/templates`)
  return response.json()
}

export async function generateLabels(itemIds: string[], template: string) {
  const response = await fetch(`${API_BASE}/api/labels/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      item_ids: itemIds,
      template: template,
    }),
  })

  return response.blob()
}