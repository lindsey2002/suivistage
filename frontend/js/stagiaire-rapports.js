checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let allRapports = []
let editingId = null
let currentRapportId = null

async function loadRapports() {
  const { data } = await apiRequest('/stagiaire/rapports')
  allRapports = data.data
  renderRapports(allRapports)
}

function renderRapports(rapports) {
  const tbody = document.getElementById('rapports-table')

  if (rapports.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B;">Aucun rapport soumis</td></tr>'
    return
  }

  tbody.innerHTML = rapports.map(r => `
    <tr>
      <td>Semaine ${r.semaine}</td>
      <td style="font-size:13px; color:#64748B;">${r.date_debut_sem} → ${r.date_fin_sem}</td>
      <td>${new Date(r.date_soumission).toLocaleDateString('fr-FR')}</td>
      <td><span class="badge badge-${r.statut === 'en_attente' ? 'attente' : r.statut}">${r.statut.replace('_', ' ')}</span></td>
      <td style="display:flex; gap:6px;">
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="viewRapport(${r.id})">
          Voir
        </button>
        ${r.statut === 'en_attente' || r.statut === 'rejete' ? `
        <button class="btn btn-primary" style="font-size:12px; padding:5px 10px;" onclick="editRapport(${r.id})">
          Modifier
        </button>` : ''}
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

function openCreateModal() {
  editingId = null
  document.getElementById('modal-create-title').textContent = 'Nouveau rapport'
  document.getElementById('btn-save').textContent = 'Soumettre'
  document.getElementById('input-semaine').value = ''
  document.getElementById('input-debut').value = ''
  document.getElementById('input-fin').value = ''
  document.getElementById('input-contenu').value = ''
  document.getElementById('create-error').style.display = 'none'
  document.getElementById('modal-create').classList.add('active')
}

function editRapport(id) {
  const rapport = allRapports.find(r => r.id === id)
  if (!rapport) return
  editingId = id
  document.getElementById('modal-create-title').textContent = 'Modifier le rapport'
  document.getElementById('btn-save').textContent = 'Mettre à jour'
  document.getElementById('input-semaine').value = rapport.semaine
  document.getElementById('input-debut').value = rapport.date_debut_sem
  document.getElementById('input-fin').value = rapport.date_fin_sem
  document.getElementById('input-contenu').value = rapport.contenu
  document.getElementById('create-error').style.display = 'none'
  document.getElementById('modal-create').classList.add('active')
}

function closeCreateModal() {
  document.getElementById('modal-create').classList.remove('active')
}

async function saveRapport() {
  const body = {
    semaine: parseInt(document.getElementById('input-semaine').value),
    date_debut_sem: document.getElementById('input-debut').value,
    date_fin_sem: document.getElementById('input-fin').value,
    contenu: document.getElementById('input-contenu').value,
  }
  const errorDiv = document.getElementById('create-error')

  const { response, data } = editingId
    ? await apiRequest(`/stagiaire/rapports/${editingId}`, 'PUT', body)
    : await apiRequest('/stagiaire/rapports', 'POST', body)

  if (response.ok) {
    closeCreateModal()
    showToast(editingId ? 'Rapport mis à jour !' : 'Rapport soumis avec succès !')
    loadRapports()
  } else {
    errorDiv.style.display = 'block'
    errorDiv.textContent = data.message || 'Erreur lors de la soumission.'
  }
}

function viewRapport(id) {
  const rapport = allRapports.find(r => r.id === id)
  if (!rapport) return
  currentRapportId = id

  document.getElementById('detail-content').innerHTML = `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Semaine</p>
      <p style="font-weight:500;">Semaine ${rapport.semaine} — du ${rapport.date_debut_sem} au ${rapport.date_fin_sem}</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Statut</p>
      <span class="badge badge-${rapport.statut === 'en_attente' ? 'attente' : rapport.statut}">${rapport.statut.replace('_', ' ')}</span>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Contenu</p>
      <p style="line-height:1.6; background:#F8FAFC; padding:12px; border-radius:8px; font-size:14px;">${rapport.contenu}</p>
    </div>
    ${rapport.commentaire_tuteur ? `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Commentaire du tuteur</p>
      <p style="line-height:1.6; background:#FEF3C7; padding:12px; border-radius:8px; font-size:14px;">${rapport.commentaire_tuteur}</p>
    </div>` : ''}
    ${rapport.livrables && rapport.livrables.length > 0 ? `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:8px;">Livrables</p>
      ${rapport.livrables.map(l => `
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:#F8FAFC; border-radius:8px; margin-bottom:6px;">
          <span style="font-size:14px;">${l.nom}</span>
          ${l.type === 'lien' ? `<a href="${l.url_ou_chemin}" target="_blank" class="btn btn-secondary" style="font-size:12px; padding:3px 8px;">Ouvrir</a>` : ''}
        </div>
      `).join('')}
    </div>` : ''}
  `

  // Afficher section livrable seulement si rapport modifiable
  if (rapport.statut === 'en_attente' || rapport.statut === 'rejete') {
    document.getElementById('livrable-section').style.display = 'block'
  } else {
    document.getElementById('livrable-section').style.display = 'none'
  }

  document.getElementById('modal-detail').classList.add('active')
}

function closeDetailModal() {
  document.getElementById('modal-detail').classList.remove('active')
}

async function addLivrable() {
  const nom = document.getElementById('input-livrable-nom').value
  const type = document.getElementById('input-livrable-type').value
  const url_ou_chemin = document.getElementById('input-livrable-url').value

  if (!nom || !url_ou_chemin) {
    showToast('Veuillez remplir tous les champs.', 'error')
    return
  }

  const { response, data } = await apiRequest(
    `/stagiaire/rapports/${currentRapportId}/livrables`,
    'POST',
    { nom, type, url_ou_chemin }
  )

  if (response.ok) {
    document.getElementById('input-livrable-nom').value = ''
    document.getElementById('input-livrable-url').value = ''
    closeDetailModal()
    showToast('Livrable ajouté !')
    loadRapports()
  } else {
    showToast(data.message || 'Erreur lors de l\'ajout.', 'error')
  }
}

loadRapports()