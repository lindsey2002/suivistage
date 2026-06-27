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
    window.location.href = '/frontend/index.html'
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
   try {
    await apiRequest('/logout', 'POST')
  } catch (e) {}
  localStorage.clear()
  window.location.href = '/frontend/index.html'
}

// ── Toasts ───────────────────────────────────────────────────
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container')
  if (!container) {
    container = document.createElement('div')
    container.id = 'toast-container'
    container.className = 'toast-container'
    document.body.appendChild(container)
  }
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message
  container.appendChild(toast)
  setTimeout(() => toast.remove(), 3500)
}

// ── Modal confirmation suppression ───────────────────────────
function confirmDelete(message, callback) {
  let overlay = document.getElementById('confirm-overlay')
  if (!overlay) {
    overlay = document.createElement('div')
    overlay.id = 'confirm-overlay'
    overlay.className = 'modal-overlay'
    overlay.innerHTML = `
      <div class="modal" style="max-width:400px; text-align:center;">
        <p style="font-size:18px; font-weight:700; color:#1E293B; margin-bottom:8px;">Confirmation</p>
        <p id="confirm-message" style="color:#64748B; font-size:14px; margin-bottom:24px;"></p>
        <div style="display:flex; gap:10px; justify-content:center;">
          <button class="btn btn-secondary" id="confirm-cancel">Annuler</button>
          <button class="btn btn-danger" id="confirm-ok">Supprimer</button>
        </div>
      </div>
    `
    document.body.appendChild(overlay)
  }
  document.getElementById('confirm-message').textContent = message
  overlay.classList.add('active')
  document.getElementById('confirm-cancel').onclick = () => overlay.classList.remove('active')
  document.getElementById('confirm-ok').onclick = () => {
    overlay.classList.remove('active')
    callback()
  }
}

// ── Badge sidebar rapports en attente ────────────────────────
async function loadSidebarBadge() {
  try {
    const endpoint = window.location.pathname.includes('tuteur')
      ? '/tuteur/rapports'
      : null
    if (!endpoint) return
    const { data } = await apiRequest(endpoint)
    const enAttente = data.data.filter(r => r.statut === 'en_attente').length
    if (enAttente > 0) {
      const links = document.querySelectorAll('.nav-item')
      links.forEach(link => {
        if (link.href && link.href.includes('rapports')) {
          link.innerHTML += ` <span style="background:#EF4444; color:white; border-radius:999px; font-size:11px; padding:1px 7px; margin-left:4px;">${enAttente}</span>`
        }
      })
    }
  } catch (e) {}
}