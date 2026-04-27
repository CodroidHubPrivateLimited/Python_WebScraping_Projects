let allVisitorRecords = [];
const themeToggle = document.getElementById('themeToggle');
const visitorDateFilter = document.getElementById('visitorDateFilter');

themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

function getTodayDateValue() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDate(value) {
    if (!value) return '-';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return String(value);
}

function formatTime(value) {
    if (!value) return '--';
    const parsed = new Date(`1970-01-01T${value}`);
    if (!isNaN(parsed)) {
        return parsed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return String(value);
}

function getFilteredVisitors() {
    const selectedDate = visitorDateFilter.value;
    if (!selectedDate) {
        return [...allVisitorRecords];
    }
    return allVisitorRecords.filter((visitor) => String(visitor.date || '') === selectedDate);
}

function renderVisitors() {
    const tbody = document.getElementById('visitorTableBody');
    const filteredVisitors = getFilteredVisitors();
    const todayKey = getTodayDateValue();
    const todayVisitors = allVisitorRecords.filter((visitor) => String(visitor.date || '') === todayKey);

    document.getElementById('totalVisitors').textContent = String(allVisitorRecords.length);
    document.getElementById('todayVisitors').textContent = String(todayVisitors.length);
    document.getElementById('filteredVisitors').textContent = String(filteredVisitors.length);

    if (!filteredVisitors.length) {
        tbody.innerHTML = '<tr><td colspan="11" class="px-5 py-14 text-center text-sm text-slate-400">No visitor records found for the selected date.</td></tr>';
        return;
    }

    tbody.innerHTML = filteredVisitors.map((visitor) => `
        <tr class="transition hover:bg-slate-50">
          <td data-label="Date" class="px-5 py-5 font-semibold text-slate-800">${formatDate(visitor.date)}</td>
          <td data-label="Time" class="px-5 py-5 text-sm text-slate-500">${formatTime(visitor.time)}</td>
          <td data-label="Visitor Name" class="px-5 py-5 font-semibold text-slate-800">${visitor.name || '-'}</td>
          <td data-label="Purpose" class="px-5 py-5 text-sm text-slate-500">${visitor.purpose || '-'}</td>
          <td data-label="Person to Meet" class="px-5 py-5 text-sm text-slate-500">${visitor.person_to_meet || '-'}</td>
          <td data-label="Question Responses" class="px-5 py-5 text-sm text-slate-500">${visitor.question_responses || '-'}</td>
          <td data-label="Face Image" class="px-5 py-5 text-sm text-slate-500">${renderVisitorImage(visitor)}</td>
          <td data-label="Feedback" class="px-5 py-5 text-sm text-slate-500">${visitor.feedback || '-'}</td>
          <td data-label="Check Out" class="px-5 py-5 text-sm text-slate-500">${renderCheckoutInfo(visitor)}</td>
          <td data-label="Status" class="px-5 py-5 text-sm font-semibold ${String(visitor.status || '').toLowerCase() === 'checked out' ? 'text-emerald-700' : 'text-amber-700'}">${visitor.status || 'Checked In'}</td>
          <td data-label="Action" class="px-5 py-5 text-sm text-slate-500">${renderCheckoutButton(visitor)}</td>
        </tr>
      `).join('');
}

function renderVisitorImage(visitor) {
    if (!visitor.face_image_path) {
        return '-';
    }

    const imageUrl = `/visitor_face?path=${encodeURIComponent(visitor.face_image_path)}`;
    const altText = visitor.name ? `${visitor.name} face` : 'Visitor face';
    return `<a href="${imageUrl}" target="_blank" rel="noopener noreferrer"><img src="${imageUrl}" alt="${altText}" class="visitor-thumb" /></a>`;
}

function renderCheckoutInfo(visitor) {
    if (!visitor.check_out_date && !visitor.check_out_time) {
        return '-';
    }
    return `${formatDate(visitor.check_out_date)}<div class="mt-1 text-xs text-slate-400">${formatTime(visitor.check_out_time)}</div>`;
}

function renderCheckoutButton(visitor) {
    if (String(visitor.status || '').toLowerCase() === 'checked out') {
        return '<span class="rounded-xl bg-emerald-50 px-3 py-2 text-xs font-extrabold text-emerald-700">Completed</span>';
    }
    return `<button type="button" data-row-id="${visitor.row_id}" class="visitor-checkout-btn rounded-xl bg-[#0a607b] px-4 py-2 text-xs font-extrabold text-white transition hover:bg-[#084f67]">Check Out</button>`;
}

async function handleVisitorCheckout(rowId) {
    const formData = new FormData();
    formData.append('row_id', String(rowId));

    const response = await fetch('/visitor_checkout', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok || data.status !== 'success') {
        throw new Error(data.message || 'Unable to check out visitor');
    }

    await loadVisitors();
}

async function loadVisitors() {
    try {
        const response = await fetch('/get_visitors');
        const data = await response.json();

        if (!(data.status === 'success' && Array.isArray(data.visitors))) {
            allVisitorRecords = [];
            renderVisitors();
            return;
        }

        allVisitorRecords = data.visitors;
        renderVisitors();
    } catch (error) {
        document.getElementById('visitorTableBody').innerHTML = '<tr><td colspan="11" class="px-5 py-14 text-center text-sm text-rose-500">Unable to load visitor records.</td></tr>';
    }
}

visitorDateFilter.value = getTodayDateValue();
visitorDateFilter.addEventListener('change', renderVisitors);
document.getElementById('clearVisitorFilter').addEventListener('click', () => {
    visitorDateFilter.value = '';
    renderVisitors();
});

document.getElementById('visitorTableBody').addEventListener('click', async (event) => {
    const button = event.target.closest('.visitor-checkout-btn');
    if (!button) {
        return;
    }

    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Saving...';

    try {
        await handleVisitorCheckout(button.dataset.rowId);
    } catch (error) {
        button.disabled = false;
        button.textContent = originalText;
        alert(error.message);
    }
});

loadVisitors();
setInterval(loadVisitors, 10000);
