document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const userStatusDiv = document.getElementById('user-status');

    // Logique pour la page de connexion
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorMessageDiv = document.getElementById('error-message');

            errorMessageDiv.textContent = ''; // Vider les anciens messages d'erreur

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    // Stocker le token et le rôle
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('role', data.role);
                    
                    // Rediriger vers une page protégée (à créer)
                    window.location.href = '/dashboard'; // Exemple de redirection
                } else {
                    errorMessageDiv.textContent = data.message || 'Une erreur est survenue.';
                }
            } catch (error) {
                console.error('Erreur de connexion:', error);
                errorMessageDiv.textContent = 'Impossible de se connecter au serveur.';
            }
        });
    }

    // Logique pour la page d'inscription
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.getElementById('role').value;
            const errorMessageDiv = document.getElementById('error-message');
            const successMessageDiv = document.getElementById('success-message');

            errorMessageDiv.textContent = '';
            successMessageDiv.textContent = '';

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password, role }),
                });

                const data = await response.json();

                if (response.ok) {
                    successMessageDiv.textContent = 'Inscription réussie ! Vous pouvez maintenant vous connecter.';
                    registerForm.reset();
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else {
                    errorMessageDiv.textContent = data.message || 'Une erreur est survenue.';
                }
            } catch (error) {
                console.error("Erreur d'inscription:", error);
                errorMessageDiv.textContent = 'Impossible de se connecter au serveur.';
            }
        });
    }

    // Logique pour la page d'accueil (ou autres pages)
    if (userStatusDiv) {
        const token = localStorage.getItem('token');
        if (token) {
            // Idéalement, vous devriez vérifier la validité du token ici en appelant une API
            const role = localStorage.getItem('role');
            userStatusDiv.innerHTML = `
                <p>Vous êtes connecté en tant que <strong>${role}</strong>.</p>
                <a href="#" id="logout-btn" class="btn btn-secondary">Se déconnecter</a>
            `;
            document.getElementById('logout-btn').addEventListener('click', () => {
                localStorage.clear();
                window.location.reload();
            });
        }
    }
});