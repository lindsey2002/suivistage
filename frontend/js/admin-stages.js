checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let editingId = null

async function loadStages() {
  const { data } = await apiRequest('/admin/stages')
  const stages = data.data
  const tbody = document.getElementById('stages-table')

  if (stages.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B;">Aucun stage</td></tr>'
    return
  }

  tbody.innerHTML = stages.map(s => `
    <tr>
      <td><strong>${s.titre}</strong><br/><span style="font-size:12px; color:#64748B;">${s.description || ''}</span></td>
      <td>${s.entreprise}</td>
      <td>${s.date_debut}</td>
      <td>${s.date_fin}</td>
      <td>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="editStage(${s.id}, '${s.titre}', '${s.entreprise}', \`${s.description || ''}\`, '${s.date_debut}', '${s.date_fin}')">
          Modifier
        </button>
        <button class="btn btn-danger" style="font-size:12px; padding:5px 10px; margin-left:6px;" onclick="deleteStage(${s.id})">
          Supprimer
        </button>
      </td>
    </tr>
  `).join('')
}

function openModal() {
  editingId = null
  document.getElementById('modal-title').textContent = 'Nouveau stage'
  document.getElementById('btn-save').textContent = 'Créer'
  document.getElementById('input-titre').value = ''
  document.getElementById('input-entreprise').value = ''
  document.getElementById('input-description').value = ''
  document.getElementById('input-debut').value = ''
  document.getElementById('input-fin').value = ''
  document.getElementById('modal-overlay').classList.add('active')
}

function editStage(id, titre, entreprise, description, debut, fin) {
  editingId = id
  document.getElementById('modal-title').textContent = 'Modifier le stage'
  document.getElementById('btn-save').textContent = 'Modifier'
  document.getElementById('input-titre').value = titre
  document.getElementById('input-entreprise').value = entreprise
  document.getElementById('input-description').value = description
  document.getElementById('input-debut').value = debut
  document.getElementById('input-fin').value = fin
  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
  document.getElementById('modal-error').style.display = 'none'
}

async function saveStage() {
  const body = {
    titre: document.getElementById('input-titre').value,
    entreprise: document.getElementById('input-entreprise').value,
    description: document.getElementById('input-description').value,
    date_debut: document.getElementById('input-debut').value,
    date_fin: document.getElementById('input-fin').value,
  }
  const errorDiv = document.getElementById('modal-error')

  const { response, data } = editingId
    ? await apiRequest(`/admin/stages/${editingId}`, 'PUT', body)
    : await apiRequest('/admin/stages', 'POST', body)

  if (response.ok) {
    closeModal()
    showToast(editingId ? 'Stage mis à jour !' : 'Stage créé !')
    loadStages()
  } else {
    errorDiv.style.display = 'block'
    errorDiv.textContent = data.message || 'Erreur lors de la sauvegarde.'
  }
}

async function deleteStage(id) {
  confirmDelete('Voulez-vous vraiment supprimer ce stage ?', async () => {
    await apiRequest(`/admin/stages/${id}`, 'DELETE')
    showToast('Stage supprimé.', 'info')
    loadStages()
  })
}

loadStages()