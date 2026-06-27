const API_URL = 'http://localhost:8002/api/v1'

// Récupérer le token stocké
function getToken() {
  return localStorage.getItem('token')
}

// Récupérer l'utilisateur connecté
function getUser() {
  return JSON.parse(localStorage.getItem('user'))
}

// Vérifier si connecté, sinon rediriger
function checkAuth() {
  const token = getToken()
  if (!token) {
    window.location.href = '/index.html'
    return false
  }
  return true
}

// Requête API générique avec token
async function apiRequest(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
  }
  if (body) {
    options.body = JSON.stringify(body)
  }
  const response = await fetch(`${API_URL}${endpoint}`, options)
  const data = await response.json()
  if (response.status === 401) {
    localStorage.clear()
    window.location.href = '/index.html'
  }
  return { response, data }
}

// Déconnexion
async function logout() {
  await apiRequest('/logout', 'POST')
  localStorage.clear()
  window.location.href = '/index.html'
}