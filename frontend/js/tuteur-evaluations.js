checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

let allEvaluations = []

async function loadEvaluations() {
  const { data } = await apiRequest('/tuteur/evaluations')
  allEvaluations = data.data
  renderEvaluations(allEvaluations)
}

function renderEvaluations(evaluations) {
  const tbody = document.getElementById('evaluations-table')

  if (evaluations.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B;">Aucune évaluation rédigée</td></tr>'
    return
  }

  tbody.innerHTML = evaluations.map(e => `
    <tr>
      <td>${e.affectation.stagiaire.prenom} ${e.affectation.stagiaire.nom}</td>
      <td>${e.affectation.stage.titre}<br/>
        <span style="font-size:12px; color:#64748B;">${e.affectation.stage.entreprise}</span>
      </td>
      <td>
        <span style="font-size:20px; font-weight:700; color:${e.note >= 10 ? '#22C55E' : '#EF4444'};">
          ${e.note}/20
        </span>
      </td>
      <td>${new Date(e.date_redaction).toLocaleDateString('fr-FR')}</td>
      <td>
        <button class="btn btn-secondary" style="font-size:12px; padding:5px 10px;" onclick="viewEvaluation(${e.id})">
          Voir
        </button>
      </td>
    </tr>
  `).join('')
}

function viewEvaluation(id) {
  const e = allEvaluations.find(ev => ev.id === id)
  if (!e) return

  document.getElementById('modal-content').innerHTML = `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Stagiaire</p>
      <p style="font-weight:500;">${e.affectation.stagiaire.prenom} ${e.affectation.stagiaire.nom}</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Stage</p>
      <p style="font-weight:500;">${e.affectation.stage.titre} — ${e.affectation.stage.entreprise}</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Note</p>
      <p style="font-size:28px; font-weight:700; color:${e.note >= 10 ? '#22C55E' : '#EF4444'};">${e.note}/20</p>
    </div>
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Appréciation</p>
      <p style="line-height:1.6; background:#F8FAFC; padding:12px; border-radius:8px; font-size:14px;">${e.appreciation}</p>
    </div>
    ${e.points_forts ? `
    <div style="margin-bottom:16px;">
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Points forts</p>
      <p style="line-height:1.6; background:#DCFCE7; padding:12px; border-radius:8px; font-size:14px;">${e.points_forts}</p>
    </div>` : ''}
    ${e.points_ameliorer ? `
    <div>
      <p style="font-size:13px; color:#64748B; margin-bottom:4px;">Points à améliorer</p>
      <p style="line-height:1.6; background:#FEE2E2; padding:12px; border-radius:8px; font-size:14px;">${e.points_ameliorer}</p>
    </div>` : ''}
  `

  document.getElementById('modal-overlay').classList.add('active')
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active')
}

loadEvaluations()
loadSidebarBadge()