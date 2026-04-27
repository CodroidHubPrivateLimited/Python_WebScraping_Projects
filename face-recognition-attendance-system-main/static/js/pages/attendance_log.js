let allAttendanceRecords = [];
let selectedMonth = null;
let selectedYear = null;
const themeToggle = document.getElementById('themeToggle');

themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

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

function getStatusClass(status) {
    const normalized = String(status || '').toLowerCase();
    if (normalized === 'present') return 'status-pill status-present';
    if (normalized === 'on time') return 'status-pill status-present';
    if (normalized === 'buffer') return 'status-pill status-late';
    if (normalized === 'late') return 'status-pill status-late';
    if (normalized === 'half day') return 'status-pill status-late';
    if (normalized === 'early exit') return 'status-pill status-late';
    if (normalized === 'short leave') return 'status-pill status-late';
    return 'status-pill status-absent';
}

function getFilteredRecords() {
    if (!selectedMonth || !selectedYear) {
        return [...allAttendanceRecords].reverse();
    }

    return allAttendanceRecords
        .filter((rec) => {
            if (!rec.date) return false;
            const parsed = new Date(rec.date);
            return !isNaN(parsed) &&
                parsed.getMonth() + 1 === selectedMonth &&
                parsed.getFullYear() === selectedYear;
        })
        .reverse();
}

function updateMonthUI() {
    document.querySelectorAll('.month-chip').forEach((button) => {
        const isActive = Number(button.dataset.month) === selectedMonth;
        button.classList.toggle('active', isActive);
    });

    const clearButton = document.getElementById('clearMonthFilter');
    clearButton.classList.toggle('active', !selectedMonth);
    clearButton.classList.toggle('month-chip', !selectedMonth);
}

function renderAttendanceHistory() {
    const tbody = document.getElementById('attendanceTableBody');
    const records = getFilteredRecords();

    if (!records.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="px-5 py-14 text-center text-sm text-slate-400">No attendance history available for the selected month.</td></tr>';
        document.getElementById('attendanceRate').textContent = '0.0%';
        document.getElementById('absenceCount').textContent = '0';
        document.getElementById('avgHours').textContent = '0h 00m';
        document.getElementById('attendanceTrend').textContent = '+0.0%';
        return;
    }

    tbody.innerHTML = records.map((rec) => {
        const totalHours = rec.total_hours || '0h 00m';
        const displayCheckIn = rec.check_in || rec.time || '';
        const displayCheckOut = rec.check_out || '';
        const noteText = rec.notes ? `<div class="mt-1 text-xs text-slate-400">${rec.notes}</div>` : '';
        return `
            <tr class="transition hover:bg-slate-50">
              <td data-label="Date" class="px-5 py-5 align-top">
                <div class="font-bold text-slate-800">${formatDate(rec.date)}</div>
                <div class="mt-1 text-xs text-slate-400">${rec.date ? new Date(rec.date).toLocaleDateString([], { weekday: 'long' }) : '-'}</div>
              </td>
              <td data-label="Employee Name" class="px-5 py-5">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9e9fb] text-xs font-extrabold text-[#0d5a7d]">
                    ${(rec.name || 'U').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase()}
                  </div>
                  <div class="font-semibold text-slate-800">${rec.name || 'Unknown'}</div>
                </div>
              </td>
              <td data-label="Employee ID" class="px-5 py-5 text-sm text-slate-500">${rec.emp_id || '-'}</td>
              <td data-label="Check-In" class="px-5 py-5 font-semibold text-slate-800">${formatTime(displayCheckIn)}</td>
              <td data-label="Check-Out" class="px-5 py-5 font-semibold text-slate-500">${formatTime(displayCheckOut)}</td>
              <td data-label="Total Hours" class="px-5 py-5 font-bold text-[#0d5a7d]">${totalHours}</td>
              <td data-label="Status" class="px-5 py-5">
                <span class="${getStatusClass(rec.status)}">${rec.status || 'Absent'}</span>
                ${noteText}
              </td>
              <td data-label="Actions" class="px-5 py-5 text-xs font-semibold text-slate-400">${rec.in_status || '-'} / ${rec.out_status || '-'}</td>
            </tr>
          `;
    }).join('');

    const positiveStatuses = ['present', 'on time', 'buffer', 'final out'];
    const presentRecords = records.filter((rec) => positiveStatuses.includes(String(rec.status).toLowerCase()));
    const absentRecords = records.filter((rec) => ['absent', 'half day', 'early exit'].includes(String(rec.status).toLowerCase()));
    const attendanceRate = records.length ? ((presentRecords.length / records.length) * 100).toFixed(1) : '0.0';
    document.getElementById('attendanceRate').textContent = `${attendanceRate}%`;
    document.getElementById('attendanceTrend').textContent = `+${Math.max(0.1, (presentRecords.length * 0.2)).toFixed(1)}%`;
    document.getElementById('absenceCount').textContent = String(absentRecords.length);

    const avgMinutes = presentRecords.length
        ? Math.round(presentRecords.reduce((sum, rec) => {
            const hoursText = rec.total_hours || '0h 00m';
            const match = hoursText.match(/(\d+)h (\d+)m/);
            return sum + (match ? Number(match[1]) * 60 + Number(match[2]) : 0);
        }, 0) / presentRecords.length)
        : 0;
    document.getElementById('avgHours').textContent = `${Math.floor(avgMinutes / 60)}h ${String(avgMinutes % 60).padStart(2, '0')}m`;
}

async function loadAttendanceHistory() {
    try {
        const res = await fetch('/get_attendance');
        const data = await res.json();
        if (!(data.status === 'success' && Array.isArray(data.attendance))) {
            allAttendanceRecords = [];
            renderAttendanceHistory();
            return;
        }

        allAttendanceRecords = data.attendance;
        renderAttendanceHistory();
    } catch (err) {
        document.getElementById('attendanceTableBody').innerHTML = '<tr><td colspan="8" class="px-5 py-14 text-center text-sm text-rose-500">Unable to load attendance history.</td></tr>';
    }
}

document.querySelectorAll('.month-chip').forEach((button) => {
    button.addEventListener('click', () => {
        selectedMonth = Number(button.dataset.month);
        selectedYear = new Date().getFullYear();
        updateMonthUI();
        renderAttendanceHistory();
    });
});

document.getElementById('monthPicker').addEventListener('change', (e) => {
    if (!e.target.value) return;
    const [year, month] = e.target.value.split('-').map(Number);
    selectedYear = year;
    selectedMonth = month;
    updateMonthUI();
    renderAttendanceHistory();
});

document.getElementById('clearMonthFilter').addEventListener('click', () => {
    selectedMonth = null;
    selectedYear = null;
    document.getElementById('monthPicker').value = '';
    updateMonthUI();
    renderAttendanceHistory();
});

updateMonthUI();
loadAttendanceHistory();
setInterval(loadAttendanceHistory, 10000);
