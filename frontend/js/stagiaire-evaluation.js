checkAuth()

const user = getUser()
if (user) {
  document.getElementById('user-name').textContent = user.prenom + ' ' + user.nom
  document.getElementById('user-avatar').textContent = user.prenom.charAt(0).toUpperCase()
}

async function loadEvaluation() {
  const container = document.getElementById('evaluation-content')

  const { response, data } = await apiRequest('/stagiaire/evaluation')

  if (response.status === 404) {
    container.innerHTML = `
      <div class="card" style="text-align:center; padding:48px;">
        <p style="font-size:18px; font-weight:600; color:#1E293B; margin-bottom:8px;">
          Aucune évaluation disponible
        </p>
        <p style="color:#64748B; font-size:14px;">
          Votre tuteur n'a pas encore rédigé votre évaluation de fin de stage.
        </p>
      </div>
    `
    return
  }

  const e = data.data

  container.innerHTML = `
    <div class="card" style="margin-bottom:20px; text-align:center; padding:40px;">
      <p style="font-size:14px; color:#64748B; margin-bottom:8px;">Note finale</p>
      <p style="font-size:56px; font-weight:800; color:${e.note >= 10 ? '#22C55E' : '#EF4444'};">
        ${e.note}<span style="font-size:24px; color:#64748B;">/20</span>
      </p>
      <p style="font-size:13px; color:#64748B; margin-top:8px;">
        Évaluation rédigée le ${new Date(e.date_redaction).toLocaleDateString('fr-FR')}
      </p>
    </div>

    <div class="card" style="margin-bottom:20px;">
      <p style="font-size:13px; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">
        Appréciation générale
      </p>
      <p style="line-height:1.8; font-size:15px; color:#1E293B;">${e.appreciation}</p>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
      ${e.points_forts ? `
      <div class="card" style="border-left:4px solid #22C55E;">
        <p style="font-size:13px; font-weight:600; color:#166534; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">
          Points forts
        </p>
        <p style="line-height:1.8; font-size:14px; color:#1E293B;">${e.points_forts}</p>
      </div>` : ''}
      ${e.points_ameliorer ? `
      <div class="card" style="border-left:4px solid #EF4444;">
        <p style="font-size:13px; font-weight:600; color:#991B1B; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">
          Points à améliorer
        </p>
        <p style="line-height:1.8; font-size:14px; color:#1E293B;">${e.points_ameliorer}</p>
      </div>` : ''}
    </div>
  `
}

loadEvaluation()