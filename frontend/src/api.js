import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export async function fetchGrocyProducts() {
  const response = await api.get('/products/grocy')
  return response.data
}

export async function fetchTemplates() {
  const response = await api.get('/templates')
  return response.data
}

export async function createCsv(products) {
  const response = await api.post(
    '/csv/products',
    { products },
    { responseType: 'text' }
  )

  return response.data
}

export async function generatePdf(products, templatePath) {
  const response = await api.post(
    '/labels/generate',
    {
      products,
      template_path: templatePath,
    },
    { responseType: 'blob' }
  )

  return response.data
}
