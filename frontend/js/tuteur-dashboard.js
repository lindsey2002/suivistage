checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

async function loadDashboard() {
  try {
    const [stagiairesRes, rapportsRes, evaluationsRes] = await Promise.all([
      apiRequest('/tuteur/stagiaires'),
      apiRequest('/tuteur/rapports'),
      apiRequest('/tuteur/evaluations'),
    ])

    const stagiaires = stagiairesRes.data.data
    const rapports = rapportsRes.data.data
    const evaluations = evaluationsRes.data.data
    const enAttente = rapports.filter(r => r.statut === 'en_attente')

    document.getElementById('stat-stagiaires').textContent = stagiaires.length
    document.getElementById('stat-rapports').textContent = rapports.length
    document.getElementById('stat-evalues').textContent = evaluations.length
    document.getElementById('stat-attente').textContent = enAttente.length

    const tbody = document.getElementById('rapports-attente')
    if (enAttente.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#64748B;">Aucun rapport en attente</td></tr>'
      return
    }

    tbody.innerHTML = enAttente.slice(0, 5).map(r => `
      <tr>
        <td>${r.stagiaire.prenom} ${r.stagiaire.nom}</td>
        <td>Semaine ${r.semaine}</td>
        <td>${new Date(r.date_soumission).toLocaleDateString('fr-FR')}</td>
        <td>
          <a href="rapports.html" class="btn btn-primary" style="font-size:12px; padding:5px 10px;">
            Valider
          </a>
        </td>
      </tr>
    `).join('')

  } catch (error) {
    console.error('Erreur:', error)
  }
}

loadDashboard()