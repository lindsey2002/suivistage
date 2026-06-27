checkAuth()
loadSidebarBadge()

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

    // Notification rapport rejeté
    if (rejetes.length > 0) {
      showToast(`${rejetes.length} rapport(s) rejeté(s) — veuillez les corriger.`, 'error')
    }

    // Afficher le stage
    const evalRes = await apiRequest('/stagiaire/evaluation')
    if (evalRes.response.ok) {
      const stage = evalRes.data.data.affectation.stage
      const header = document.querySelector('.page-header')
      header.innerHTML += `
        <div style="margin-top:12px; background:white; border:1px solid #E2E8F0; border-radius:10px; padding:12px 16px; display:inline-flex; gap:16px; align-items:center;">
          <div>
            <p style="font-size:12px; color:#64748B;">Stage en cours</p>
            <p style="font-size:14px; font-weight:600; color:#1E293B;">${stage.titre}</p>
            <p style="font-size:13px; color:#64748B;">${stage.entreprise}</p>
          </div>
        </div>
      `
    }

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