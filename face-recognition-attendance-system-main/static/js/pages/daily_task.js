let allTasks = [];
let personnelList = [];
let taskPoll = null;

const taskModal = document.getElementById('taskModal');
const taskForm = document.getElementById('taskForm');
const taskFormMessage = document.getElementById('taskFormMessage');
const taskPersonnel = document.getElementById('taskPersonnel');
const taskRole = document.getElementById('taskRole');
const searchInput = document.getElementById('searchInput');
const themeToggle = document.getElementById('themeToggle');

themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

function getInitials(name) {
    return (name || 'UN')
        .split(' ')
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0].toUpperCase())
        .join('') || 'UN';
}

function getStatusMeta(status) {
    const normalized = String(status || '').toLowerCase();
    if (normalized === 'completed') {
        return { label: 'Completed', classes: 'bg-[#edf5ff] text-[#6b8cc8]', icon: 'check_circle' };
    }
    if (normalized === 'in progress') {
        return { label: 'In Progress', classes: 'bg-[#edf1ff] text-[#6578d8]', icon: 'schedule' };
    }
    if (normalized === 'delayed') {
        return { label: 'Delayed', classes: 'bg-[#ffe8e5] text-[#ef6b63]', icon: 'warning' };
    }
    return { label: 'Pending', classes: 'bg-slate-100 text-slate-500', icon: 'radio_button_checked' };
}

function showFormMessage(message, type = 'info') {
    taskFormMessage.textContent = message;
    taskFormMessage.className = `message-card ${type === 'success' ? 'tone-success' : type === 'error' ? 'tone-error' : 'tone-info'}`;
    taskFormMessage.classList.remove('hidden');
}

function clearFormMessage() {
    taskFormMessage.classList.add('hidden');
    taskFormMessage.textContent = '';
}

function openTaskModal(task = null) {
    clearFormMessage();
    document.getElementById('modalTitle').textContent = task ? 'Edit Daily Task' : 'Create Daily Task';
    document.getElementById('saveTaskButton').textContent = task ? 'Update Task' : 'Save Task';
    document.getElementById('taskId').value = task?.id || '';
    document.getElementById('taskTitle').value = task?.title || '';
    document.getElementById('taskLocation').value = task?.location || '';
    document.getElementById('taskDate').value = task?.date || new Date().toISOString().split('T')[0];
    document.getElementById('taskStartTime').value = task?.start_time || '';
    document.getElementById('taskEndTime').value = task?.end_time || '';
    document.getElementById('taskStatus').value = task?.status || 'Pending';
    document.getElementById('taskNotes').value = task?.notes || '';
    taskPersonnel.value = task?.assigned_emp_id || '';
    taskRole.value = task?.role || '';
    taskModal.classList.remove('hidden');
    taskModal.classList.add('flex');
    document.getElementById('taskTitle').focus();
}

function closeTaskModal() {
    taskModal.classList.add('hidden');
    taskModal.classList.remove('flex');
    taskForm.reset();
    document.getElementById('taskId').value = '';
    document.getElementById('taskDate').value = new Date().toISOString().split('T')[0];
    clearFormMessage();
}

function populatePersonnelOptions() {
    const currentValue = taskPersonnel.value;
    taskPersonnel.innerHTML = '<option value="">Unassigned</option>' + personnelList.map((person) => `
        <option value="${person.emp_id}">${person.name}${person.emp_id ? ` (${person.emp_id})` : ''}</option>
    `).join('');
    if (currentValue) {
        taskPersonnel.value = currentValue;
    }
}

function updateSummary(summary = {}, visibleCount = allTasks.length) {
    document.getElementById('activeTasksCount').textContent = summary.active ?? allTasks.length;
    document.getElementById('inProgressCount').textContent = summary.in_progress ?? 0;
    document.getElementById('delayedCount').textContent = summary.delayed ?? 0;
    document.getElementById('completedCount').textContent = summary.completed ?? 0;
    document.getElementById('taskCountSummary').textContent = `Showing ${visibleCount} live task${visibleCount === 1 ? '' : 's'}`;
    document.getElementById('taskPageStamp').textContent = `Last sync ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
}

function renderTasks(summary) {
    const query = searchInput.value.trim().toLowerCase();
    const filteredTasks = allTasks.filter((task) => {
        const haystack = [
            task.title,
            task.location,
            task.assigned_name,
            task.assigned_emp_id,
            task.role,
            task.status,
            task.notes,
        ].join(' ').toLowerCase();
        return haystack.includes(query);
    });

    const taskTableBody = document.getElementById('taskTableBody');
    if (!filteredTasks.length) {
        taskTableBody.innerHTML = '<div class="px-5 py-16 text-center text-sm text-slate-400">No tasks found. Create a new task to start live tracking.</div>';
        updateSummary(summary, 0);
        return;
    }

    taskTableBody.innerHTML = filteredTasks.map((task) => {
        const statusMeta = getStatusMeta(task.status);
        const timelineLabel = task.end_time ? `End ${formatTime(task.end_time)}` : 'No end time';
        const assignedName = task.assigned_name || 'Unassigned';
        const assignedRole = task.role || 'Employee';
        return `
            <article class="task-card">
                <div>
                    <p class="text-base font-extrabold text-[#243c63]">${escapeHtml(task.title)}</p>
                    <p class="mt-1 text-sm text-slate-500">${escapeHtml(task.location)}</p>
                    <p class="mt-1 text-xs text-slate-400">${escapeHtml(task.notes || 'No extra notes')}</p>
                </div>
                <div class="flex items-center gap-3" style="margin-top:0.85rem;">
                    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#243c63] text-sm font-extrabold text-white">${escapeHtml(getInitials(assignedName))}</div>
                    <div>
                        <p class="text-sm font-bold text-[#243c63]">${escapeHtml(assignedName)}</p>
                        <p class="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">${escapeHtml(assignedRole)}${task.assigned_emp_id ? ` · ${escapeHtml(task.assigned_emp_id)}` : ''}</p>
                    </div>
                </div>
                <div class="text-sm text-[#243c63]" style="margin-top:0.85rem;">
                    <p class="font-bold">${escapeHtml(formatDate(task.date))} · ${escapeHtml(formatTime(task.start_time))}</p>
                    <p class="mt-1 text-slate-500">${escapeHtml(timelineLabel)}</p>
                </div>
                <div style="margin-top:0.85rem;">
                    <span class="status-chip ${statusMeta.classes}">
                        <span class="material-symbols-outlined text-[14px]">${statusMeta.icon}</span>
                        ${statusMeta.label}
                    </span>
                </div>
                <div class="flex flex-wrap gap-2" style="margin-top:1rem;">
                    ${String(task.status).toLowerCase() !== 'completed' ? `<button class="row-action rounded-xl px-3 py-2 text-xs font-bold" data-complete="${task.id}">Complete</button>` : ''}
                    <button class="row-action rounded-xl px-3 py-2 text-xs font-bold" data-edit="${task.id}">Edit</button>
                    <button class="rounded-xl border border-rose-100 bg-rose-50 px-3 py-2 text-xs font-bold text-rose-600 transition hover:bg-rose-100" data-delete="${task.id}">Delete</button>
                </div>
            </article>
        `;
    }).join('');

    updateSummary(summary, filteredTasks.length);
}

function escapeHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatTime(value) {
    if (!value) return 'No time';
    const [hour, minute] = String(value).split(':');
    if (hour === undefined || minute === undefined) return value;
    const date = new Date();
    date.setHours(Number(hour), Number(minute), 0, 0);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(value) {
    if (!value) return 'Today';
    const parsed = new Date(value);
    if (isNaN(parsed)) return value;
    return parsed.toLocaleDateString();
}

async function loadTasks() {
    try {
        const response = await fetch('/get_daily_tasks');
        const data = await response.json();
        if (data.status !== 'success') {
            throw new Error(data.message || 'Unable to load tasks');
        }
        allTasks = Array.isArray(data.tasks) ? data.tasks : [];
        personnelList = Array.isArray(data.personnel) ? data.personnel : [];
        populatePersonnelOptions();
        renderTasks(data.summary || {});
    } catch (error) {
        document.getElementById('taskTableBody').innerHTML = `<div class="px-5 py-16 text-center text-sm text-rose-500">${escapeHtml(error.message)}</div>`;
    }
}

async function saveTask(payload) {
    const response = await fetch('/save_daily_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Unable to save task');
    }
    return data;
}

async function deleteTask(id) {
    const response = await fetch('/delete_daily_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
    });
    const data = await response.json();
    if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Unable to delete task');
    }
    return data;
}

taskPersonnel.addEventListener('change', () => {
    const selected = personnelList.find((person) => person.emp_id === taskPersonnel.value);
    if (selected && !taskRole.value.trim()) {
        taskRole.value = selected.role || 'Employee';
    }
});

taskForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const saveButton = document.getElementById('saveTaskButton');
    const payload = {
        id: document.getElementById('taskId').value,
        title: document.getElementById('taskTitle').value.trim(),
        location: document.getElementById('taskLocation').value.trim(),
        assigned_emp_id: taskPersonnel.value,
        role: taskRole.value.trim(),
        date: document.getElementById('taskDate').value,
        start_time: document.getElementById('taskStartTime').value,
        end_time: document.getElementById('taskEndTime').value,
        status: document.getElementById('taskStatus').value,
        notes: document.getElementById('taskNotes').value.trim(),
    };

    try {
        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';
        await saveTask(payload);
        showFormMessage('Task saved successfully.', 'success');
        await loadTasks();
        setTimeout(closeTaskModal, 600);
    } catch (error) {
        showFormMessage(error.message, 'error');
    } finally {
        saveButton.disabled = false;
        saveButton.textContent = document.getElementById('taskId').value ? 'Update Task' : 'Save Task';
    }
});

document.getElementById('taskTableBody').addEventListener('click', async (event) => {
    const editId = event.target.closest('[data-edit]')?.dataset.edit;
    const deleteId = event.target.closest('[data-delete]')?.dataset.delete;
    const completeId = event.target.closest('[data-complete]')?.dataset.complete;

    if (editId) {
        const task = allTasks.find((item) => item.id === editId);
        if (task) openTaskModal(task);
        return;
    }

    if (completeId) {
        const task = allTasks.find((item) => item.id === completeId);
        if (!task) return;
        try {
            await saveTask({ ...task, status: 'Completed' });
            await loadTasks();
        } catch (error) {
            alert(error.message);
        }
        return;
    }

    if (deleteId) {
        if (!confirm('Delete this task?')) return;
        try {
            await deleteTask(deleteId);
            await loadTasks();
        } catch (error) {
            alert(error.message);
        }
    }
});

searchInput.addEventListener('input', () => renderTasks({
    active: allTasks.length,
    in_progress: allTasks.filter((task) => String(task.status).toLowerCase() === 'in progress').length,
    delayed: allTasks.filter((task) => String(task.status).toLowerCase() === 'delayed').length,
    completed: allTasks.filter((task) => String(task.status).toLowerCase() === 'completed').length,
}));

document.getElementById('openNewTask').addEventListener('click', () => openTaskModal());
document.getElementById('closeModal').addEventListener('click', closeTaskModal);
document.getElementById('cancelTask').addEventListener('click', closeTaskModal);
document.getElementById('refreshTasks').addEventListener('click', loadTasks);

taskModal.addEventListener('click', (event) => {
    if (event.target === taskModal) {
        closeTaskModal();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !taskModal.classList.contains('hidden')) {
        closeTaskModal();
    }
});

document.getElementById('taskDate').value = new Date().toISOString().split('T')[0];
loadTasks();
taskPoll = setInterval(loadTasks, 10000);

window.addEventListener('beforeunload', () => {
    if (taskPoll) clearInterval(taskPoll);
});
