const loginForm = document.getElementById('loginForm');
const loginStatus = document.getElementById('loginStatus');
const selectedRole = loginForm?.dataset.role || 'employee';

function setError(id, message) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = message;
    }
}

function clearLoginErrors() {
    setError('loginUsernameError', '');
    setError('loginPasswordError', '');
    loginStatus.textContent = '';
}

document.querySelectorAll('.toggle-password').forEach((button) => {
    button.addEventListener('click', () => {
        const targetId = button.dataset.target;
        const input = document.getElementById(targetId);
        const icon = button.querySelector('.material-symbols-outlined');
        if (!input || !icon) {
            return;
        }

        const isHidden = input.type === 'password';
        input.type = isHidden ? 'text' : 'password';
        icon.textContent = isHidden ? 'visibility_off' : 'visibility';
    });
});

loginForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearLoginErrors();

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    let hasError = false;

    if (!username) {
        setError('loginUsernameError', 'Username is required.');
        hasError = true;
    }

    if (!password) {
        setError('loginPasswordError', 'Password is required.');
        hasError = true;
    }

    if (hasError) {
        loginStatus.textContent = 'Please fix the highlighted fields.';
        return;
    }

    loginStatus.textContent = 'Checking credentials...';

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                role: selectedRole,
                username,
                password,
            }),
        });

        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            loginStatus.textContent = data.message || 'Login failed.';
            return;
        }

        loginStatus.textContent = 'Login successful. Redirecting...';
        window.location.href = data.redirect;
    } catch (error) {
        loginStatus.textContent = 'Unable to connect to the server.';
    }
});
