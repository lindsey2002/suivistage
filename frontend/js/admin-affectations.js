checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

async function loadAffectations() {
  const { data } = await apiRequest('/admin/affectations')
  const affectations = data.data
  const tbody = document.getElementById('affectations-table')

  if (affectations.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B;">Aucune affectation</td></tr>'
    return
  }

  tbody.innerHTML = affectations.map(a => `
    <tr>
      <td>${a.stagiaire.prenom} ${a.stagiaire.nom}</td>
      <td>${a.tuteur.prenom} ${a.tuteur.nom}</td>
      <td>${a.stage.titre}<br/><span style="font-size:12px; color:#64748B;">${a.stage.entreprise}</span></td>
      <td>${new Date(a.date_affectation).toLocaleDateString('fr-FR')}</td>
      <td>
        <button class="btn btn-danger" style="font-size:12px; padding:5px 10px;" onclick="deleteAffectation(${a.id})">
          Supprimer
        </button>
      </td>
    </tr>
  `).join('')
}

async function openModal() {
  // Charger les données pour les selects
  const [usersRes, stagesRes] = await Promise.all([
    apiRequest('/admin/users'),
    apiRequest('/admin/stages'),
  ])

  const users = usersRes.data.data
  const stages = stagesRes.data.data

  const stagiaires = users.filter(u => u.role === 'stagiaire')
  const tuteurs = users.filter(u => u.role === 'tuteur')

  document.getElementById('input-stagiaire').innerHTML = stagiaires.map(u =>
    `<option value="${u.id}">${u.prenom} ${u.nom}</option>`
  ).join('')

  document.getElementById('input-tuteur').innerHTML = tuteurs.map(u =>
    `<option value="${u.id}">${u.prenom} ${u.nom}</option>`
  ).join('')

  document.getElementById('input-stage').innerHTML = stages.map(s =>
    `<option value="${s.id}">${s.titre} — ${s.entreprise}</option>`
  ).join('')

  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
  document.getElementById('modal-error').style.display = 'none'
}

async function createAffectation() {
  const stagiaire_id = parseInt(document.getElementById('input-stagiaire').value)
  const tuteur_id = parseInt(document.getElementById('input-tuteur').value)
  const stage_id = parseInt(document.getElementById('input-stage').value)
  const errorDiv = document.getElementById('modal-error')

  const { response, data } = await apiRequest('/admin/affectations', 'POST', {
    stagiaire_id, tuteur_id, stage_id
  })

  if (response.ok) {
    closeModal()
    loadAffectations()
  } else {
    errorDiv.style.display = 'block'
    errorDiv.textContent = data.message || 'Erreur lors de la création.'
  }
}

async function deleteAffectation(id) {
  if (!confirm('Confirmer la suppression ?')) return
  await apiRequest(`/admin/affectations/${id}`, 'DELETE')
  loadAffectations()
}

loadAffectations()