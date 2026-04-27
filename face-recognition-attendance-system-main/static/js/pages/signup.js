const signupForm = document.getElementById('signupForm');
const signupStatus = document.getElementById('signupStatus');

function setSignupError(id, message) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = message;
    }
}

function clearSignupErrors() {
    setSignupError('signupNameError', '');
    setSignupError('signupEmployeeIdError', '');
    setSignupError('signupDepartmentError', '');
    setSignupError('signupEmailError', '');
    setSignupError('signupPasswordError', '');
    setSignupError('signupConfirmPasswordError', '');
    setSignupError('signupTermsError', '');
    signupStatus.textContent = '';
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

signupForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearSignupErrors();

    const selectedRole = signupForm.dataset.role || 'employee';
    const fullName = document.getElementById('signupName').value.trim();
    const employeeId = document.getElementById('signupEmployeeId').value.trim();
    const department = document.getElementById('signupDepartment').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const acceptedTerms = document.getElementById('signupTerms').checked;
    let hasError = false;

    if (!fullName) {
        setSignupError('signupNameError', 'Full name is required.');
        hasError = true;
    }

    if (!employeeId) {
        setSignupError('signupEmployeeIdError', 'Employee ID is required.');
        hasError = true;
    }

    if (!department) {
        setSignupError('signupDepartmentError', 'Department is required.');
        hasError = true;
    }

    if (!email) {
        setSignupError('signupEmailError', 'Email is required.');
        hasError = true;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setSignupError('signupEmailError', 'Enter a valid email address.');
        hasError = true;
    }

    if (!password) {
        setSignupError('signupPasswordError', 'Password is required.');
        hasError = true;
    } else if (password.length < 4) {
        setSignupError('signupPasswordError', 'Password must be at least 4 characters.');
        hasError = true;
    }

    if (!confirmPassword) {
        setSignupError('signupConfirmPasswordError', 'Please confirm your password.');
        hasError = true;
    } else if (password !== confirmPassword) {
        setSignupError('signupConfirmPasswordError', 'Passwords do not match.');
        hasError = true;
    }

    if (!acceptedTerms) {
        setSignupError('signupTermsError', 'You must accept the terms to continue.');
        hasError = true;
    }

    if (hasError) {
        signupStatus.textContent = 'Please correct the form and try again.';
        return;
    }

    signupStatus.textContent = 'Creating employee account...';

    try {
        const response = await fetch('/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                role: selectedRole,
                full_name: fullName,
                employee_id: employeeId,
                department,
                email,
                password,
            }),
        });

        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            signupStatus.textContent = data.message || 'Signup failed.';
            return;
        }

        signupStatus.textContent = `${data.message} Redirecting to login...`;
        window.setTimeout(() => {
            window.location.href = data.redirect;
        }, 1000);
    } catch (error) {
        signupStatus.textContent = 'Unable to connect to the server.';
    }
});
