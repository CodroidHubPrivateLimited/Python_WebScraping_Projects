let employeeAttendanceRecords = [];
let selectedMonth = null;
let selectedYear = null;
let currentPage = 1;
const pageSize = 5;

const themeToggle = document.getElementById('themeToggle');
const monthPicker = document.getElementById('monthPicker');
const clearMonthFilter = document.getElementById('clearMonthFilter');
const tableBody = document.getElementById('employeeAttendanceTableBody');
const searchInput = document.getElementById('attendanceSearchInput');
const statusFilter = document.getElementById('statusFilter');
const pager = document.getElementById('attendancePager');
const rangeLabel = document.getElementById('attendanceRangeLabel');
const trendChart = document.getElementById('trendChart');
const trendSummaryLabel = document.getElementById('trendSummaryLabel');
const exportSummaryText = document.getElementById('exportSummaryText');
const toggleAdvancedFilters = document.getElementById('toggleAdvancedFilters');
const advancedFiltersPanel = document.getElementById('advancedFiltersPanel');
const emailManagerButton = document.getElementById('emailManagerButton');

themeToggle?.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

toggleAdvancedFilters?.addEventListener('click', () => {
    advancedFiltersPanel?.classList.toggle('show');
});

emailManagerButton?.addEventListener('click', () => {
    window.location.href = 'mailto:?subject=Attendance Summary&body=Please find my attendance summary attached from SecureTrack.';
});

function formatDate(value) {
    if (!value) return '-';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return String(value);
}

function formatShortDate(value) {
    if (!value) return '';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    return String(value);
}

function formatWeekday(value) {
    if (!value) return '-';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString([], { weekday: 'short' });
    }
    return '-';
}

function formatTime(value) {
    if (!value) return '--:--';
    const parsed = new Date(`1970-01-01T${value}`);
    if (!isNaN(parsed)) {
        return parsed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return String(value);
}

function parseHoursToMinutes(value) {
    const match = String(value || '').match(/(\d+)h (\d+)m/);
    if (!match) return 0;
    return Number(match[1]) * 60 + Number(match[2]);
}

function formatAvgHours(minutes) {
    if (!minutes) return '0h 00m';
    return `${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, '0')}m`;
}

function getStatusClass(status) {
    const normalized = String(status || '').toLowerCase();
    if (['present', 'on time', 'buffer', 'final out'].includes(normalized)) return 'status-pill status-present';
    if (['late', 'half day', 'early exit', 'short leave', 'on break', 'queued'].includes(normalized)) return 'status-pill status-late';
    return 'status-pill status-absent';
}

function normalizeStatus(status) {
    return String(status || '').trim().toLowerCase();
}

function matchesStatusFilter(status) {
    const selected = String(statusFilter?.value || '').trim().toLowerCase();
    if (!selected) return true;
    const normalized = normalizeStatus(status);
    if (selected === 'present') return ['present', 'on time', 'buffer', 'final out'].includes(normalized);
    if (selected === 'late') return ['late', 'half day', 'early exit'].includes(normalized);
    return normalized === selected;
}

function getFilteredRecords() {
    const query = String(searchInput?.value || '').trim().toLowerCase();

    return employeeAttendanceRecords.filter((record) => {
        if (selectedMonth && selectedYear) {
            const parsed = new Date(record.date);
            if (isNaN(parsed) || parsed.getMonth() + 1 !== selectedMonth || parsed.getFullYear() !== selectedYear) {
                return false;
            }
        }

        if (!matchesStatusFilter(record.status)) {
            return false;
        }

        if (!query) {
            return true;
        }

        const haystack = [
            record.date,
            formatDate(record.date),
            record.check_in,
            record.check_out,
            record.total_hours,
            record.status,
            record.notes,
            record.emp_id,
        ].join(' ').toLowerCase();

        return haystack.includes(query);
    });
}

function getPagedRecords(records) {
    const totalPages = Math.max(1, Math.ceil(records.length / pageSize));
    if (currentPage > totalPages) currentPage = totalPages;
    const start = (currentPage - 1) * pageSize;
    return {
        rows: records.slice(start, start + pageSize),
        start,
        totalPages,
    };
}

function updateMonthUI() {
    document.querySelectorAll('.month-chip').forEach((button) => {
        button.classList.toggle('active', Number(button.dataset.month) === selectedMonth);
    });

    clearMonthFilter?.classList.toggle('active', !selectedMonth);
    clearMonthFilter?.classList.toggle('month-chip', !selectedMonth);
}

function renderSummary(records) {
    const presentStatuses = ['present', 'on time', 'buffer', 'final out'];
    const absentStatuses = ['absent', 'half day', 'early exit'];
    const presentRecords = records.filter((record) => presentStatuses.includes(normalizeStatus(record.status)));
    const absentRecords = records.filter((record) => absentStatuses.includes(normalizeStatus(record.status)));
    const avgMinutes = presentRecords.length
        ? Math.round(presentRecords.reduce((sum, record) => sum + parseHoursToMinutes(record.total_hours), 0) / presentRecords.length)
        : 0;

    document.getElementById('historyTotalDays').textContent = String(records.length);
    document.getElementById('historyPresentDays').textContent = String(presentRecords.length);
    document.getElementById('historyAbsenceDays').textContent = String(absentRecords.length);
    document.getElementById('historyAvgHours').textContent = formatAvgHours(avgMinutes);

    exportSummaryText.textContent = records.length
        ? `You currently have ${records.length} attendance record(s) available for export. Average tracked work time is ${formatAvgHours(avgMinutes)}.`
        : 'Generate a clean attendance export for reporting and personal tracking.';
}

function renderPager(totalPages) {
    if (!pager) return;
    if (totalPages <= 1) {
        pager.innerHTML = '';
        return;
    }

    const buttons = [];
    buttons.push(`<button type="button" data-page="${Math.max(1, currentPage - 1)}">&lsaquo;</button>`);
    for (let page = 1; page <= totalPages; page += 1) {
        buttons.push(`<button type="button" data-page="${page}" class="${page === currentPage ? 'active' : ''}">${page}</button>`);
    }
    buttons.push(`<button type="button" data-page="${Math.min(totalPages, currentPage + 1)}">&rsaquo;</button>`);
    pager.innerHTML = buttons.join('');
}

function renderTrend(records) {
    if (!trendChart) return;

    const monthBuckets = [];
    const now = new Date();
    for (let offset = 5; offset >= 0; offset -= 1) {
        const bucketDate = new Date(now.getFullYear(), now.getMonth() - offset, 1);
        monthBuckets.push({
            key: `${bucketDate.getFullYear()}-${bucketDate.getMonth()}`,
            label: bucketDate.toLocaleDateString([], { month: 'short' }).toUpperCase(),
            minutes: 0,
        });
    }

    records.forEach((record) => {
        const parsed = new Date(record.date);
        if (isNaN(parsed)) return;
        const key = `${parsed.getFullYear()}-${parsed.getMonth()}`;
        const bucket = monthBuckets.find((item) => item.key === key);
        if (!bucket) return;
        bucket.minutes += parseHoursToMinutes(record.total_hours);
    });

    const maxMinutes = Math.max(...monthBuckets.map((item) => item.minutes), 1);
    const peakBucket = monthBuckets.reduce((best, current) => current.minutes > best.minutes ? current : best, monthBuckets[0]);
    trendSummaryLabel.textContent = peakBucket ? `Peak month: ${peakBucket.label}` : 'Attendance distribution';

    trendChart.innerHTML = monthBuckets.map((bucket) => {
        const height = Math.max(24, Math.round((bucket.minutes / maxMinutes) * 140));
        const hours = (bucket.minutes / 60).toFixed(1);
        const isActive = bucket.key === peakBucket.key;
        return `
            <div class="trend-bar-wrap">
                <div class="trend-bar ${isActive ? 'active' : ''}" style="height:${height}px;"></div>
                <div class="trend-bar-label">${bucket.label}</div>
                <div class="trend-bar-value">${hours}h</div>
            </div>
        `;
    }).join('');
}

function renderAttendanceHistory() {
    const filteredRecords = getFilteredRecords();
    renderSummary(filteredRecords);
    renderTrend(filteredRecords);

    if (!filteredRecords.length) {
        tableBody.innerHTML = '<tr><td colspan="6" class="px-5 py-14 text-center text-sm text-slate-400">No attendance history found for this employee.</td></tr>';
        rangeLabel.textContent = 'Showing 0 to 0 of 0 records';
        renderPager(0);
        return;
    }

    const { rows, start, totalPages } = getPagedRecords(filteredRecords);

    tableBody.innerHTML = rows.map((record) => {
        const notes = record.notes
            ? `<div class="mt-1 text-xs text-slate-400">${record.notes}</div>`
            : '<span class="text-slate-400">Standard working day</span>';

        return `
            <tr class="transition hover:bg-slate-50">
                <td data-label="Date" class="px-5 py-5 align-top">
                    <div class="font-bold text-slate-800">${formatShortDate(record.date)}</div>
                    <div class="mt-1 text-xs text-slate-400">${formatWeekday(record.date)}, ${new Date(record.date).getFullYear()}</div>
                </td>
                <td data-label="Clock-In" class="px-5 py-5 font-semibold text-slate-800">${formatTime(record.check_in || record.time)}</td>
                <td data-label="Clock-Out" class="px-5 py-5 font-semibold text-slate-500">${formatTime(record.check_out)}</td>
                <td data-label="Total Hours" class="px-5 py-5 font-bold text-[#0d5a7d]">${record.total_hours || '0h 00m'}</td>
                <td data-label="Status" class="px-5 py-5">
                    <span class="${getStatusClass(record.status)}">${String(record.status || 'Unknown').toUpperCase()}</span>
                </td>
                <td data-label="Notes" class="px-5 py-5 text-sm text-slate-500">${notes}</td>
            </tr>
        `;
    }).join('');

    rangeLabel.textContent = `Showing ${start + 1} to ${start + rows.length} of ${filteredRecords.length} records`;
    renderPager(totalPages);
}

async function loadEmployeeAttendanceHistory() {
    try {
        const response = await fetch('/get_employee_attendance_history');
        const data = await response.json();

        if (!(response.ok && data.status === 'success' && Array.isArray(data.attendance))) {
            employeeAttendanceRecords = [];
            renderAttendanceHistory();
            return;
        }

        employeeAttendanceRecords = [...data.attendance].sort((a, b) => {
            const left = `${a.date || ''} ${a.check_in || a.time || ''}`;
            const right = `${b.date || ''} ${b.check_in || b.time || ''}`;
            return right.localeCompare(left);
        });
        renderAttendanceHistory();
    } catch (error) {
        tableBody.innerHTML = '<tr><td colspan="6" class="px-5 py-14 text-center text-sm text-rose-500">Unable to load attendance history.</td></tr>';
        rangeLabel.textContent = 'Unable to load records';
    }
}

document.querySelectorAll('.month-chip').forEach((button) => {
    button.addEventListener('click', () => {
        selectedMonth = Number(button.dataset.month);
        selectedYear = new Date().getFullYear();
        currentPage = 1;
        updateMonthUI();
        renderAttendanceHistory();
    });
});

monthPicker?.addEventListener('change', (event) => {
    if (!event.target.value) return;
    const [year, month] = event.target.value.split('-').map(Number);
    selectedYear = year;
    selectedMonth = month;
    currentPage = 1;
    updateMonthUI();
    renderAttendanceHistory();
});

clearMonthFilter?.addEventListener('click', () => {
    selectedMonth = null;
    selectedYear = null;
    currentPage = 1;
    if (monthPicker) monthPicker.value = '';
    updateMonthUI();
    renderAttendanceHistory();
});

searchInput?.addEventListener('input', () => {
    currentPage = 1;
    renderAttendanceHistory();
});

statusFilter?.addEventListener('change', () => {
    currentPage = 1;
    renderAttendanceHistory();
});

pager?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-page]');
    if (!button) return;
    currentPage = Number(button.dataset.page);
    renderAttendanceHistory();
});

updateMonthUI();
loadEmployeeAttendanceHistory();
