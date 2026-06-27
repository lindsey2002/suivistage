checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let currentStagiaireId = null

async function loadStagiaires() {
  const { data } = await apiRequest('/tuteur/stagiaires')
  const affectations = data.data
  const grid = document.getElementById('stagiaires-grid')

  if (affectations.length === 0) {
    grid.innerHTML = '<p style="color:#64748B;">Aucun stagiaire affecté.</p>'
    return
  }

  grid.innerHTML = affectations.map(a => `
    <div class="card" style="display:flex; flex-direction:column; gap:12px;">
      <div style="display:flex; align-items:center; gap:12px;">
        <div class="sidebar-avatar" style="width:48px; height:48px; font-size:18px; flex-shrink:0;">
          ${a.stagiaire.prenom.charAt(0).toUpperCase()}
        </div>
        <div>
          <p style="font-weight:600; font-size:15px;">${a.stagiaire.prenom} ${a.stagiaire.nom}</p>
          <p style="font-size:13px; color:#64748B;">${a.stagiaire.email}</p>
        </div>
      </div>
      <div style="background:#F8FAFC; border-radius:8px; padding:12px;">
        <p style="font-size:12px; color:#64748B; margin-bottom:4px;">Stage</p>
        <p style="font-size:14px; font-weight:500;">${a.stage.titre}</p>
        <p style="font-size:13px; color:#64748B;">${a.stage.entreprise}</p>
        <p style="font-size:12px; color:#64748B; margin-top:4px;">${a.stage.date_debut} → ${a.stage.date_fin}</p>
      </div>
      <button class="btn btn-primary" style="width:100%;" onclick="openEvalModal(${a.stagiaire.id}, '${a.stagiaire.prenom} ${a.stagiaire.nom}')">
        Rédiger une évaluation
      </button>
    </div>
  `).join('')
}

function openEvalModal(stagiaireId, nom) {
  currentStagiaireId = stagiaireId
  document.getElementById('modal-title').textContent = `Évaluation — ${nom}`
  document.getElementById('input-note').value = ''
  document.getElementById('input-appreciation').value = ''
  document.getElementById('input-points-forts').value = ''
  document.getElementById('input-points-ameliorer').value = ''
  document.getElementById('modal-error').style.display = 'none'
  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
}

async function submitEvaluation() {
  const note = parseFloat(document.getElementById('input-note').value)
  const appreciation = document.getElementById('input-appreciation').value
  const points_forts = document.getElementById('input-points-forts').value
  const points_ameliorer = document.getElementById('input-points-ameliorer').value
  const errorDiv = document.getElementById('modal-error')

  const { response, data } = await apiRequest(
    `/tuteur/stagiaires/${currentStagiaireId}/evaluation`,
    'POST',
    { note, appreciation, points_forts, points_ameliorer }
  )

  if (response.ok) {
    closeModal()
    alert('Évaluation enregistrée avec succès !')
  } else {
    errorDiv.style.display = 'block'
    errorDiv.textContent = data.message || 'Erreur lors de l\'enregistrement.'
  }
}

loadStagiaires()