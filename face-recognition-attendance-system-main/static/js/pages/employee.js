const currentTime = document.getElementById('currentTime');
const employeeStatusCard = document.getElementById('employeeStatusCard');
const employeeTasksList = document.getElementById('employeeTasksList');
const changePasswordForm = document.getElementById('changePasswordForm');
const passwordStatus = document.getElementById('passwordStatus');

function updateTime() {
    if (!currentTime) return;
    const now = new Date();
    currentTime.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function updateStatus(message, tone = 'default') {
    if (!employeeStatusCard) return;
    employeeStatusCard.textContent = message;
    employeeStatusCard.style.color = tone === 'success'
        ? '#1fa181'
        : tone === 'warning'
            ? '#bf7a16'
            : '#7f8e9d';
}

function formatTime(value) {
    if (!value) return '--';
    const parsed = new Date(`1970-01-01T${value}`);
    if (!isNaN(parsed)) {
        return parsed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return String(value);
}

function formatDate(value) {
    if (!value) return 'Today';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return String(value);
}

function renderEmployeeTasks(tasks) {
    if (!employeeTasksList) return;

    if (!Array.isArray(tasks) || !tasks.length) {
        employeeTasksList.innerHTML = `
            <div class="task-row">
                <div class="task-icon">
                    <span class="material-symbols-outlined">assignment_late</span>
                </div>
                <div class="task-copy">
                    <strong>No tasks assigned by admin yet.</strong>
                    <span>Your upcoming work items will appear here when available.</span>
                </div>
            </div>
        `;
        return;
    }

    employeeTasksList.innerHTML = tasks.slice(0, 5).map((task) => {
        const normalizedStatus = String(task.status || 'Pending').toLowerCase();
        const badgeClass = normalizedStatus.includes('urgent') || normalizedStatus.includes('late')
            ? 'high'
            : normalizedStatus.includes('progress') || normalizedStatus.includes('normal')
                ? 'medium'
                : 'low';

        return `
            <div class="task-row">
                <div class="task-icon">
                    <span class="material-symbols-outlined">assignment</span>
                </div>
                <div class="task-copy">
                    <strong>${task.title || 'Untitled Task'}</strong>
                    <span>${formatDate(task.date)} · ${task.location || 'No location'} · ${formatTime(task.start_time)}${task.end_time ? ` - ${formatTime(task.end_time)}` : ''}</span>
                </div>
                <span class="task-badge ${badgeClass}">${task.status || 'Pending'}</span>
            </div>
        `;
    }).join('');
}

async function loadEmployeeTasks() {
    if (!employeeTasksList) return;
    try {
        const response = await fetch('/get_employee_tasks');
        const data = await response.json();
        if (!(response.ok && data.status === 'success' && Array.isArray(data.tasks))) {
            renderEmployeeTasks([]);
            return;
        }
        renderEmployeeTasks(data.tasks);
        updateStatus(`Profile, attendance, and ${data.tasks.length} assigned task(s) are available to view.`, 'success');
    } catch (error) {
        renderEmployeeTasks([]);
        updateStatus('Unable to load employee workspace data right now.', 'warning');
    }
}

changePasswordForm?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const currentPassword = document.getElementById('currentPassword')?.value || '';
    const newPassword = document.getElementById('newPassword')?.value || '';

    if (!currentPassword || !newPassword) {
        if (passwordStatus) passwordStatus.textContent = 'Please fill both password fields.';
        return;
    }

    if (passwordStatus) passwordStatus.textContent = 'Updating password...';

    try {
        const response = await fetch('/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
            }),
        });

        const data = await response.json();
        if (passwordStatus) passwordStatus.textContent = data.message || 'Unable to update password.';

        if (response.ok && data.status === 'success') {
            changePasswordForm.reset();
        }
    } catch (error) {
        if (passwordStatus) passwordStatus.textContent = 'Server connection failed.';
    }
});

updateTime();
setInterval(updateTime, 1000 * 30);
loadEmployeeTasks();
