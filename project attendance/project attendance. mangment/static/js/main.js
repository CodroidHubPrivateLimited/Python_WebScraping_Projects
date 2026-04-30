document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if(loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log("Attempting Login...");
            // Add AJAX/Fetch logic here
        });
    }

    if(signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log("Creating Account...");
            // Add AJAX/Fetch logic here
        });
    }
});
