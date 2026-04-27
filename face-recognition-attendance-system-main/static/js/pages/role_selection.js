const roleCards = document.querySelectorAll('.role-card');
const roleSelectionStatus = document.getElementById('roleSelectionStatus');

roleCards.forEach((card) => {
    card.addEventListener('click', () => {
        roleCards.forEach((item) => item.classList.remove('is-selected'));
        card.classList.add('is-selected');

        const role = card.dataset.role || 'employee';
        if (role === 'admin') {
            roleSelectionStatus.textContent = 'Administrator selected. Redirecting to login...';
            window.location.href = '/login?role=admin';
            return;
        }

        roleSelectionStatus.textContent = 'Employee selected. Redirecting to login...';
        window.location.href = '/login?role=employee';
    });
});
