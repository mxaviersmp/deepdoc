import axios from 'axios'

const baseUrl = 'http://localhost:5000'

const searchTerms = async search => {
  const response = await axios.get(`${baseUrl}/search/term?query=${search}`)
  return response.data
}

const searchCategory = async search => {
  const response = await axios.get(`${baseUrl}/search/category?query=${search}`)
  return response.data
}

export default {
  searchTerms,
  searchCategory,
}
