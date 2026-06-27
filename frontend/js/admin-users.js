checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let allUsers = []

async function loadUsers() {
  const { data } = await apiRequest('/admin/users')
  allUsers = data.data
  renderUsers(allUsers)
}

function renderUsers(users) {
  const tbody = document.getElementById('users-table')
  if (users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B;">Aucun utilisateur</td></tr>'
    return
  }
  tbody.innerHTML = users.map(u => `
    <tr>
      <td>${u.prenom} ${u.nom}</td>
      <td>${u.email}</td>
      <td><span class="badge badge-${u.role === 'administrateur' ? 'valide' : u.role === 'tuteur' ? 'attente' : 'archive'}">${u.role}</span></td>
      <td><span class="badge ${u.est_actif ? 'badge-valide' : 'badge-rejete'}">${u.est_actif ? 'Actif' : 'Inactif'}</span></td>
      <td>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="toggleUser(${u.id})">
          ${u.est_actif ? 'Désactiver' : 'Activer'}
        </button>
        <button class="btn btn-danger" style="font-size:12px; padding:5px 10px; margin-left:6px;" onclick="deleteUser(${u.id})">
          Supprimer
        </button>
      </td>
    </tr>
  `).join('')
}

function filterUsers() {
  const role = document.getElementById('filter-role').value
  if (!role) {
    renderUsers(allUsers)
  } else {
    renderUsers(allUsers.filter(u => u.role === role))
  }
}

async function toggleUser(id) {
  await apiRequest(`/admin/users/${id}/toggle`, 'POST')
  loadUsers()
}

async function deleteUser(id) {
  if (!confirm('Confirmer la suppression ?')) return
  await apiRequest(`/admin/users/${id}`, 'DELETE')
  loadUsers()
}

function openModal() {
  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
  document.getElementById('modal-error').style.display = 'none'
}

async function createUser() {
  const nom = document.getElementById('input-nom').value
  const prenom = document.getElementById('input-prenom').value
  const email = document.getElementById('input-email').value
  const mot_de_passe = document.getElementById('input-mdp').value
  const mot_de_passe_confirmation = document.getElementById('input-mdp-confirm').value
  const role = document.getElementById('input-role').value
  const errorDiv = document.getElementById('modal-error')

  const { response, data } = await apiRequest('/register', 'POST', {
    nom, prenom, email, mot_de_passe, mot_de_passe_confirmation, role
  })

  if (response.ok) {
    closeModal()
    loadUsers()
  } else {
    errorDiv.style.display = 'block'
    errorDiv.textContent = data.message || 'Erreur lors de la création.'
  }
}

// Ajouter style filter-select dans main.css
loadUsers()