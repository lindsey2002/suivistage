checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let allRapports = []

async function loadRapports() {
  const { data } = await apiRequest('/admin/rapports')
  allRapports = data.data
  renderRapports(allRapports)
}

function renderRapports(rapports) {
  const tbody = document.getElementById('rapports-table')

  if (rapports.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#64748B;">Aucun rapport</td></tr>'
    return
  }

  tbody.innerHTML = rapports.map(r => `
    <tr>
      <td>${r.stagiaire.prenom} ${r.stagiaire.nom}</td>
      <td>${r.stage.titre}</td>
      <td>Semaine ${r.semaine}</td>
      <td>${new Date(r.date_soumission).toLocaleDateString('fr-FR')}</td>
      <td><span class="badge badge-${r.statut === 'en_attente' ? 'attente' : r.statut}">${r.statut.replace('_', ' ')}</span></td>
      <td>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="viewRapport(${r.id})">
          Voir
        </button>
      </td>
    </tr>
  `).join('')
}

function filterRapports() {
  const statut = document.getElementById('filter-statut').value
  if (!statut) {
    renderRapports(allRapports)
  } else {
    renderRapports(allRapports.filter(r => r.statut === statut))
  }
}

function viewRapport(id) {
  const rapport = allRapports.find(r => r.id === id)
  if (!rapport) return

  document.getElementById('modal-content').innerHTML = `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Stagiaire</p>
      <p style="font-weight:500;">${rapport.stagiaire.prenom} ${rapport.stagiaire.nom}</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Période</p>
      <p style="font-weight:500;">Semaine ${rapport.semaine} — du ${rapport.date_debut_sem} au ${rapport.date_fin_sem}</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Contenu</p>
      <p style="line-height:1.6; background:#F8FAFC; padding:12px; border-radius:8px; font-size:14px;">${rapport.contenu}</p>
    </div>
    ${rapport.commentaire_tuteur ? `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Commentaire tuteur</p>
      <p style="line-height:1.6; background:#FEF3C7; padding:12px; border-radius:8px; font-size:14px;">${rapport.commentaire_tuteur}</p>
    </div>` : ''}
    ${rapport.livrables && rapport.livrables.length > 0 ? `
    <div>
      <p style="font-size:13px; color:#64748B; margin-bottom:8px;">Livrables</p>
      ${rapport.livrables.map(l => `
        <div style="display:flex; align-items:center; gap:8px; padding:8px; background:#F8FAFC; border-radius:8px; margin-bottom:6px;">
          <span style="font-size:14px;">${l.nom}</span>
          ${l.type === 'lien' ? `<a href="${l.url_ou_chemin}" target="_blank" class="btn btn-secondary" style="font-size:12px; padding:3px 8px;">Ouvrir</a>` : ''}
        </div>
      `).join('')}
    </div>` : ''}
  `

  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
}

loadRapports()