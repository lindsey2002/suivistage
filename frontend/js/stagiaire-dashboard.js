checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

async function loadDashboard() {
  try {
    const { data } = await apiRequest('/stagiaire/rapports')
    const rapports = data.data

    const valides = rapports.filter(r => r.statut === 'valide')
    const attente = rapports.filter(r => r.statut === 'en_attente')
    const rejetes = rapports.filter(r => r.statut === 'rejete')

    document.getElementById('stat-total').textContent = rapports.length
    document.getElementById('stat-valides').textContent = valides.length
    document.getElementById('stat-attente').textContent = attente.length
    document.getElementById('stat-rejetes').textContent = rejetes.length

    const tbody = document.getElementById('recent-rapports')
    if (rapports.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748B;">Aucun rapport soumis</td></tr>'
      return
    }

    tbody.innerHTML = rapports.slice(0, 5).map(r => `
      <tr>
        <td>Semaine ${r.semaine}</td>
        <td style="font-size:13px; color:#64748B;">${r.date_debut_sem} → ${r.date_fin_sem}</td>
        <td>${new Date(r.date_soumission).toLocaleDateString('fr-FR')}</td>
        <td><span class="badge badge-${r.statut === 'en_attente' ? 'attente' : r.statut}">${r.statut.replace('_', ' ')}</span></td>
      </tr>
    `).join('')

  } catch (error) {
    console.error('Erreur:', error)
  }
}

loadDashboard()