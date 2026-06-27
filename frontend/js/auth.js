const API_URL = 'http://localhost:8002/api/v1'

document.getElementById('login-form').addEventListener('submit', async function (e) {
  e.preventDefault()

  const email = document.getElementById('email').value
  const mot_de_passe = document.getElementById('mot_de_passe').value
  const btnSubmit = document.getElementById('btn-submit')
  const alertError = document.getElementById('alert-error')

  // Désactiver le bouton pendant la requête
  btnSubmit.textContent = 'Connexion...'
  btnSubmit.disabled = true
  alertError.style.display = 'none'

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, mot_de_passe }),
    })

    const data = await response.json()

    if (response.ok) {
      // Sauvegarder le token et les infos utilisateur
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))

      // Rediriger selon le rôle
      const role = data.user.role
      if (role === 'administrateur') {
        window.location.href = 'admin/dashboard.html'
      } else if (role === 'tuteur') {
        window.location.href = 'tuteur/dashboard.html'
      } else {
        window.location.href = 'stagiaire/dashboard.html'
      }
    } else {
      alertError.style.display = 'block'
      alertError.textContent = data.message || 'Identifiants incorrects.'
    }

  } catch (error) {
    alertError.style.display = 'block'
    alertError.textContent = 'Erreur de connexion au serveur.'
  } finally {
    btnSubmit.textContent = 'Se connecter'
    btnSubmit.disabled = false
  }
})