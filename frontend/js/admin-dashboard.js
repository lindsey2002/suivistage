// Vérifier l'authentification
checkAuth()

// Afficher le nom de l'utilisateur
const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

// Charger les stats
async function loadStats() {
  try {
    const [usersRes, stagesRes, rapportsRes, affectationsRes] = await Promise.all([
      apiRequest('/admin/users'),
      apiRequest('/admin/stages'),
      apiRequest('/admin/rapports'),
      apiRequest('/admin/affectations'),
    ])

    document.getElementById('stat-users').textContent = usersRes.data.data.length
    document.getElementById('stat-stages').textContent = stagesRes.data.data.length
    document.getElementById('stat-rapports').textContent = rapportsRes.data.data.length
    document.getElementById('stat-affectations').textContent = affectationsRes.data.data.length

    // Derniers utilisateurs
    const users = usersRes.data.data.slice(0, 5)
    const tbody = document.getElementById('recent-users')
    if (users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748B;">Aucun utilisateur</td></tr>'
      return
    }
    tbody.innerHTML = users.map(u => `
      <tr>
        <td>${u.prenom} ${u.nom}</td>
        <td>${u.email}</td>
        <td><span class="badge badge-${u.role === 'administrateur' ? 'valide' : u.role === 'tuteur' ? 'attente' : 'archive'}">${u.role}</span></td>
        <td><span class="badge ${u.est_actif ? 'badge-valide' : 'badge-rejete'}">${u.est_actif ? 'Actif' : 'Inactif'}</span></td>
      </tr>
    `).join('')

  } catch (error) {
    console.error('Erreur chargement stats:', error)
  }
}

loadStats()