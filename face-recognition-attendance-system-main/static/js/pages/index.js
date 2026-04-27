let videoStream = null;
let continuousInterval = null;
let attendancePoll = null;
let visitorContext = null;

const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const cameraToggle = document.getElementById('cameraToggle');
const singleMarkSidebar = document.getElementById('singleMarkSidebar');
const themeToggle = document.getElementById('themeToggle');
const checkOutButton = document.getElementById('checkOutButton');
const breakToggleButton = document.getElementById('breakToggleButton');
const attendanceDateFilter = document.getElementById('attendanceDateFilter');
const exportAttendanceButton = document.getElementById('exportAttendanceButton');
const exportVisitorsButton = document.getElementById('exportVisitorsButton');
const voiceCommandButton = document.getElementById('voiceCommandButton');
const voiceCommandStatus = document.getElementById('voiceCommandStatus');
const visitorModal = document.getElementById('visitorModal');
const visitorForm = document.getElementById('visitorForm');
const visitorQuestionsContainer = document.getElementById('visitorQuestions');
const visitorPreview = document.getElementById('visitorPreview');
const visitorImagePath = document.getElementById('visitorImagePath');
const visitorTokenInput = document.getElementById('visitorToken');
const visitorNameInput = document.getElementById('visitorName');
const visitorFeedbackRating = document.getElementById('visitorFeedbackRating');
const visitorFeedbackComments = document.getElementById('visitorFeedbackComments');
const visitorFormStatus = document.getElementById('visitorFormStatus');
const SpeechRecognitionApi = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSynthesisApi = window.speechSynthesis || null;
let voiceRecognition = null;
let voiceListening = false;
let breakModeActive = false;
let autoDateKey = getTodayDateValue();

function toneClass(type = 'info') {
    if (type === 'success') return 'tone-success';
    if (type === 'error') return 'tone-error';
    if (type === 'warning') return 'tone-warning';
    return 'tone-info';
}

themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

attendanceDateFilter.value = autoDateKey;
attendanceDateFilter.addEventListener('change', () => {
    loadAttendance();
});

cameraToggle.addEventListener('click', () => {
    if (videoStream) {
        stopMainCamera();
    } else {
        initMainCamera();
    }
});

singleMarkSidebar.addEventListener('click', handleStartAttendance);
document.getElementById('startAttendanceBig').addEventListener('click', handleStartAttendance);
checkOutButton.addEventListener('click', () => handleAttendanceAction('check_out'));
breakToggleButton.addEventListener('click', () => handleAttendanceAction('toggle_break'));
exportAttendanceButton.addEventListener('click', () => {
    window.location.href = '/export_attendance';
});
exportVisitorsButton.addEventListener('click', () => {
    window.location.href = '/export_visitors';
});
voiceCommandButton.addEventListener('click', startVoiceCommand);
document.getElementById('closeVisitorModal').addEventListener('click', hideVisitorModal);
document.getElementById('cancelVisitorButton').addEventListener('click', hideVisitorModal);
visitorForm.addEventListener('submit', submitVisitorForm);

function setCameraButton(active) {
    cameraToggle.innerHTML = `<span class="material-symbols-outlined">${active ? 'videocam_off' : 'videocam'}</span>`;
    cameraToggle.className = active ? 'chip-icon camera-live' : 'chip-icon';
}

function stopMainCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach((track) => track.stop());
        videoStream = null;
    }
    video.srcObject = null;
    video.classList.add('hidden');
    setCameraButton(false);
    showControlResult('Camera stopped.', 'info');
}

function showAttendanceActionResult(message, type = 'info') {
    const el = document.getElementById('attendanceActionResult');
    el.textContent = message;
    el.className = `message-card ${toneClass(type)}`;
}

function showAttendanceMarked(record) {
    const details = [
        `User Name: ${record.name || 'Unknown'}`,
        `User ID: ${record.emp_id || '-'}`,
        `Department: ${record.department || 'General'}`,
        'Status: Successful'
    ];
    showAttendanceActionResult(details.join(' | '), 'success');
    showControlResult(`Successful - Attendance marked for ${record.name || 'user'}.`, 'success');
}

function showVoiceCommandStatus(message, type = 'info') {
    voiceCommandStatus.textContent = message;
    voiceCommandStatus.className = `message-card ${toneClass(type)}`;
}

function setVoiceButtonState(listening) {
    voiceListening = listening;
    voiceCommandButton.disabled = listening;
    voiceCommandButton.innerHTML = listening
        ? '<span class="material-symbols-outlined animate-pulse text-[20px]">mic</span>Listening...'
        : '<span class="material-symbols-outlined text-[20px]">mic</span>Voice Command';
    voiceCommandButton.className = `secondary-button ${listening ? 'tone-success' : 'tone-info'}`;
}

function speakText(text, onEnd = null) {
    if (!speechSynthesisApi || !text) {
        if (typeof onEnd === 'function') {
            onEnd();
        }
        return;
    }

    speechSynthesisApi.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onend = () => {
        if (typeof onEnd === 'function') {
            onEnd();
        }
    };
    speechSynthesisApi.speak(utterance);
}

function normalizeVoiceCommand(command) {
    return String(command || '').toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

function getVoiceAttendanceMessage(data) {
    if (data.status === 'success') {
        return `Attendance marked successfully for ${data.name || 'user'}.`;
    }
    if (data.status === 'visitor_required') {
        return 'Face not registered. Visitor form has been opened.';
    }
    return data.message || 'Command completed.';
}

function getVoiceActionMessage(data, action) {
    if (action === 'check_out') {
        return data.message || 'Checked out successfully.';
    }
    if (data.attendance_action === 'take_break') {
        return data.message || 'You are on break.';
    }
    if (data.attendance_action === 'resume_work') {
        return data.message || 'Work resumed successfully.';
    }
    return data.message || 'Command completed successfully.';
}

function buildVoiceAction(command) {
    if (!command) {
        return null;
    }

    if (command.includes('check out') || command.includes('checkout')) {
        return {
            key: 'check_out',
            handler: () => handleAttendanceAction('check_out', { voiceMode: true }),
            reply: 'Checking out now.'
        };
    }

    if (command.includes('resume') || command.includes('continue work') || command.includes('back to work')) {
        return {
            key: 'resume_work',
            handler: () => handleAttendanceAction('toggle_break', { voiceMode: true }),
            reply: 'Resuming your work.'
        };
    }

    if (command.includes('break')) {
        return {
            key: 'take_break',
            handler: () => handleAttendanceAction('toggle_break', { voiceMode: true }),
            reply: breakModeActive ? 'Resuming your work.' : 'Starting your break.'
        };
    }

    if (command.includes('attendance') || command.includes('mark my attendance') || command.includes('mark attendance') || command.includes('check in')) {
        return {
            key: 'attendance',
            handler: () => handleStartAttendance({ voiceMode: true }),
            reply: 'Marking your attendance now.'
        };
    }

    return null;
}

function processVoiceTranscript(transcript) {
    const normalized = normalizeVoiceCommand(transcript);
    showVoiceCommandStatus(`Heard: "${normalized || transcript}"`, 'info');

    const action = buildVoiceAction(normalized);
    if (!action) {
        const message = 'Command not recognized. Try saying mark my attendance, take break, resume work, or check out.';
        showVoiceCommandStatus(message, 'error');
        showControlResult(message, 'error');
        speakText('Sorry, I could not understand the command.');
        return;
    }

    showVoiceCommandStatus(action.reply, 'success');
    showControlResult(action.reply, 'success');
    speakText(action.reply);
    action.handler();
}

function ensureVoiceRecognition() {
    if (!SpeechRecognitionApi) {
        return null;
    }

    if (voiceRecognition) {
        return voiceRecognition;
    }

    voiceRecognition = new SpeechRecognitionApi();
    voiceRecognition.lang = 'en-US';
    voiceRecognition.interimResults = false;
    voiceRecognition.maxAlternatives = 1;

    voiceRecognition.onstart = () => {
        setVoiceButtonState(true);
        showVoiceCommandStatus('Listening for your command...', 'warning');
    };

    voiceRecognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript || '';
        processVoiceTranscript(transcript);
    };

    voiceRecognition.onerror = (event) => {
        let message = 'Sorry, I could not understand.';
        if (event.error === 'not-allowed') {
            message = 'Microphone permission denied. Please allow mic access and try again.';
        } else if (event.error === 'no-speech') {
            message = 'No speech detected. Please try again.';
        }
        showVoiceCommandStatus(message, 'error');
        showControlResult(message, 'error');
        speakText(message);
    };

    voiceRecognition.onend = () => {
        setVoiceButtonState(false);
    };

    return voiceRecognition;
}

function startVoiceCommand() {
    const recognition = ensureVoiceRecognition();
    if (!recognition) {
        const message = 'Voice commands are not supported in this browser. Please use Google Chrome or Microsoft Edge.';
        showVoiceCommandStatus(message, 'error');
        showControlResult(message, 'error');
        return;
    }

    if (voiceListening) {
        return;
    }

    const prompt = 'Please give command';
    showVoiceCommandStatus(prompt, 'info');
    speakText(prompt, () => {
        try {
            recognition.start();
        } catch (error) {
            showVoiceCommandStatus('Voice recognition is already running. Please wait a moment.', 'warning');
            setVoiceButtonState(false);
        }
    });
}

function showVisitorFormStatus(message, type = 'info') {
    visitorFormStatus.textContent = message;
    visitorFormStatus.className = `message-card ${toneClass(type)}`;
}

function renderVisitorQuestions(questions = []) {
    visitorQuestionsContainer.innerHTML = questions.map((question, index) => `
        <div>
            <label class="small-copy" for="visitorQuestion_${question.id}">
                ${index + 1}. ${question.text}
            </label>
            <input
                id="visitorQuestion_${question.id}"
                data-question-id="${question.id}"
                data-question-text="${question.text}"
                type="text"
                class="visitor-question-input"
                placeholder="Enter response"
                required
            />
        </div>
    `).join('');
}

function showVisitorModal(data) {
    visitorContext = data;
    visitorForm.reset();
    visitorTokenInput.value = data.visitor_token || '';
    visitorPreview.src = data.visitor_image ? `data:image/png;base64,${data.visitor_image}` : '';
    visitorImagePath.textContent = data.visitor_image_path ? `Saved face image: ${data.visitor_image_path}` : '';
    renderVisitorQuestions(Array.isArray(data.questions) ? data.questions : []);
    showVisitorFormStatus('Complete the visitor details and required feedback to save the entry.', 'warning');
    visitorModal.classList.remove('hidden');
    visitorModal.classList.add('flex');
    visitorNameInput.focus();
}

function hideVisitorModal() {
    visitorModal.classList.add('hidden');
    visitorModal.classList.remove('flex');
    visitorContext = null;
    visitorForm.reset();
    visitorQuestionsContainer.innerHTML = '';
    showVisitorFormStatus('Complete all visitor fields to save the record to Excel.', 'info');
}

async function submitVisitorForm(event) {
    event.preventDefault();

    const submitButton = document.getElementById('submitVisitorButton');
    const original = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Saving...';

    try {
        const answers = {};
        document.querySelectorAll('.visitor-question-input').forEach((input) => {
            answers[input.dataset.questionId] = input.value.trim();
        });

        const formData = new FormData();
        formData.append('visitor_token', visitorTokenInput.value);
        formData.append('visitor_name', visitorNameInput.value.trim());
        formData.append('answers', JSON.stringify(answers));
        formData.append('feedback_rating', visitorFeedbackRating.value);
        formData.append('feedback_comments', visitorFeedbackComments.value.trim());

        const res = await fetch('/submit_visitor', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok || data.status !== 'success') {
            throw new Error(data.message || 'Unable to save visitor entry');
        }

        showVisitorFormStatus(data.message, 'success');
        showAttendanceActionResult(`Visitor saved | Name: ${visitorNameInput.value.trim()} | Face Image: ${data.face_image_path || '-'}`, 'success');
        showControlResult(data.message, 'success');
        overlay.textContent = data.message;
        overlay.className = 'overlay-badge tone-info';
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.add('hidden'), 3500);
        setTimeout(hideVisitorModal, 600);
    } catch (err) {
        showVisitorFormStatus(`Error: ${err.message}`, 'error');
    }

    submitButton.disabled = false;
    submitButton.textContent = original;
}

function setBreakButtonState(active) {
    breakModeActive = active;
    breakToggleButton.innerHTML = `
        <span class="inline-flex items-center gap-2">
            <span class="material-symbols-outlined text-[20px]">${active ? 'play_circle' : 'free_breakfast'}</span>
            <span>${active ? 'Resume Work' : 'Take Break'}</span>
        </span>
    `;
    breakToggleButton.className = active
        ? 'secondary-button tone-success'
        : 'secondary-button warning';
}

function getTodayDateValue() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

async function initMainCamera() {
    try {
        const constraints = { video: { facingMode: 'user', width: 1280, height: 720 } };
        videoStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = videoStream;
        video.classList.remove('hidden');
        setCameraButton(true);
        showControlResult('Camera connected. Ready for attendance capture.', 'success');
    } catch (err) {
        showControlResult(`Camera error: ${err.message}`, 'error');
    }
}

async function captureImage(videoEl = video) {
    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth || 1280;
    canvas.height = videoEl.videoHeight || 720;
    canvas.getContext('2d').drawImage(videoEl, 0, 0);
    return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
}

async function handleStartAttendance(options = {}) {
    const voiceMode = Boolean(options.voiceMode);
    const btn = document.getElementById('startAttendanceBig');
    const original = btn.innerHTML;
    btn.innerHTML = '<span class="inline-flex items-center gap-2"><span class="material-symbols-outlined animate-spin text-[20px]">autorenew</span>Processing...</span>';
    btn.disabled = true;

    try {
        if (!videoStream) {
            await initMainCamera();
        }
        if (!videoStream) {
            throw new Error('Camera not active');
        }

        const imageBlob = await captureImage();
        const formData = new FormData();
        formData.append('image', imageBlob, 'attendance.jpg');

        const res = await fetch('/mark_attendance', { method: 'POST', body: formData });
        const data = await res.json();

        overlay.textContent = data.name ? `${data.name} - ${data.message}` : data.message;
        overlay.className = `overlay-badge ${toneClass(
            data.status === 'success' ? 'success' :
                data.status === 'visitor_required' ? 'warning' : 'error'
        )}`;
        overlay.classList.remove('hidden');

        if (data.status === 'success') {
            showAttendanceMarked(data);
        } else if (data.status === 'visitor_required') {
            showAttendanceActionResult('Visitor detected. Complete the visitor form and required feedback.', 'warning');
            showControlResult('Visitor flow started. Finish the form to save the visitor in Excel.', 'warning');
            showVisitorModal(data);
        } else {
            showControlResult(data.message, 'error');
            showAttendanceActionResult(data.message, 'error');
        }

        if (voiceMode) {
            speakText(getVoiceAttendanceMessage(data));
        }

        setTimeout(() => overlay.classList.add('hidden'), 3500);
        loadAttendance();
    } catch (err) {
        overlay.textContent = `Error: ${err.message}`;
        overlay.className = 'overlay-badge tone-error';
        overlay.classList.remove('hidden');
        showControlResult(`Error: ${err.message}`, 'error');
        if (voiceMode) {
            speakText(`Error. ${err.message}`);
        }
        setTimeout(() => overlay.classList.add('hidden'), 3000);
    }

    btn.innerHTML = original;
    btn.disabled = false;
}

async function handleAttendanceAction(action, options = {}) {
    const voiceMode = Boolean(options.voiceMode);
    const targetButton = action === 'check_out' ? checkOutButton : breakToggleButton;
    const original = targetButton.innerHTML;
    targetButton.innerHTML = '<span class="material-symbols-outlined animate-spin text-[20px]">autorenew</span>Processing...';
    targetButton.disabled = true;

    try {
        if (!videoStream) {
            await initMainCamera();
        }
        if (!videoStream) {
            throw new Error('Camera not active');
        }

        const imageBlob = await captureImage();
        const formData = new FormData();
        formData.append('image', imageBlob, `${action}.jpg`);
        formData.append('action', action);

        const res = await fetch('/attendance_action', { method: 'POST', body: formData });
        const data = await res.json();

        if (!res.ok || data.status !== 'success') {
            throw new Error(data.message || 'Unable to process action');
        }

        overlay.textContent = `${data.name || 'User'} - ${data.message}`;
        overlay.className = `overlay-badge ${toneClass(
            data.attendance_action === 'take_break' ? 'warning' :
                data.attendance_action === 'resume_work' ? 'success' : 'info'
        )}`;
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.add('hidden'), 3500);

        setBreakButtonState(Boolean(data.break_active));
        showAttendanceActionResult(data.message, data.attendance_action === 'take_break' ? 'warning' : 'success');
        showControlResult(data.message, 'success');
        if (voiceMode) {
            speakText(getVoiceActionMessage(data, action));
        }
        loadAttendance();
    } catch (err) {
        overlay.textContent = `Error: ${err.message}`;
        overlay.className = 'overlay-badge tone-error';
        overlay.classList.remove('hidden');
        setTimeout(() => overlay.classList.add('hidden'), 3000);
        showAttendanceActionResult(`Error: ${err.message}`, 'error');
        showControlResult(`Error: ${err.message}`, 'error');
        if (voiceMode) {
            speakText(`Error. ${err.message}`);
        }
    }

    targetButton.disabled = false;
    if (action === 'check_out') {
        checkOutButton.innerHTML = original;
    } else {
        setBreakButtonState(breakModeActive);
    }
}

document.getElementById('singleMark').addEventListener('click', async () => {
    await handleStartAttendance();
});

document.getElementById('attendanceBody').addEventListener('click', async (event) => {
    const button = event.target.closest('.admin-checkout-btn');
    if (!button) return;

    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Saving...';

    try {
        const response = await fetch('/admin_manual_checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: button.dataset.userId,
                date: button.dataset.date,
            }),
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            throw new Error(data.message || 'Unable to check out user.');
        }

        showAttendanceActionResult(data.message, 'success');
        showControlResult(data.message, 'success');
        await loadAttendance();
    } catch (error) {
        button.disabled = false;
        button.textContent = originalText;
        showAttendanceActionResult(`Error: ${error.message}`, 'error');
        showControlResult(`Error: ${error.message}`, 'error');
    }
});

document.getElementById('continuousToggle').addEventListener('change', (e) => {
    const toggle = e.target;
    const label = document.getElementById('continuousLabel');

    if (toggle.checked) {
        if (!videoStream) {
            toggle.checked = false;
            showControlResult('Start camera first before enabling continuous mode.', 'error');
            return;
        }

        label.textContent = 'On';
        label.className = 'toggle-state active';

        continuousInterval = setInterval(async () => {
            try {
                const imageBlob = await captureImage();
                const formData = new FormData();
                formData.append('image', imageBlob, 'live.jpg');

                const res = await fetch('/mark_attendance', { method: 'POST', body: formData });
                const data = await res.json();

                if (data.status === 'success') {
                    overlay.textContent = `${data.name || 'Recognized'} - Successful`;
                    overlay.className = 'overlay-badge tone-success';
                    overlay.classList.remove('hidden');
                    setTimeout(() => overlay.classList.add('hidden'), 1500);
                    showAttendanceMarked(data);
                    loadAttendance();
                } else if (data.status === 'visitor_required') {
                    clearInterval(continuousInterval);
                    continuousInterval = null;
                    toggle.checked = false;
                    label.textContent = 'Off';
                    label.className = 'toggle-state';
                    overlay.textContent = 'Visitor detected - complete form';
                    overlay.className = 'overlay-badge tone-warning';
                    overlay.classList.remove('hidden');
                    setTimeout(() => overlay.classList.add('hidden'), 2500);
                    showVisitorModal(data);
                    showControlResult('Continuous mode paused for visitor form completion.', 'warning');
                }
            } catch (err) {
                showControlResult(`Continuous scan error: ${err.message}`, 'error');
            }
        }, 3000);

        showControlResult('Continuous mode enabled.', 'success');
    } else {
        label.textContent = 'Off';
        label.className = 'toggle-state';
        if (continuousInterval) {
            clearInterval(continuousInterval);
            continuousInterval = null;
        }
        showControlResult('Continuous mode disabled.', 'info');
    }
});

async function loadAttendance() {
    try {
        const currentToday = getTodayDateValue();
        if (attendanceDateFilter.value === autoDateKey && autoDateKey !== currentToday) {
            autoDateKey = currentToday;
            attendanceDateFilter.value = currentToday;
        }

        const selectedDate = attendanceDateFilter.value || currentToday;
        const res = await fetch(`/get_attendance?date=${encodeURIComponent(selectedDate)}`);
        const data = await res.json();
        const tbody = document.getElementById('attendanceBody');
        const countEl = document.getElementById('recordCount');
        const totalUsersEl = document.getElementById('totalUsers');
        const todayMarksEl = document.getElementById('todayMarks');
        const liveCountEl = document.getElementById('liveCount');

        if (data.status === 'success' && Array.isArray(data.attendance) && data.attendance.length > 0) {
            tbody.innerHTML = data.attendance.map((rec) => `
                <tr class="transition hover:bg-slate-50">
                    <td data-label="User Name" class="px-5 py-4 font-semibold text-slate-800">${rec.name || 'Unknown'}</td>
                    <td data-label="User ID" class="px-5 py-4 text-slate-500">${rec.emp_id || '-'}</td>
                    <td data-label="Department" class="px-5 py-4 text-slate-600">${rec.department || 'General'}</td>
                    <td data-label="Date" class="px-5 py-4 text-slate-600">${formatDate(rec.date)}</td>
                    <td data-label="IN Time" class="px-5 py-4 text-slate-600">${formatTime(rec.check_in || rec.time)}</td>
                    <td data-label="OUT Time" class="px-5 py-4 text-slate-600">${formatTime(rec.check_out)}</td>
                    <td data-label="Status" class="px-5 py-4">
                        <span class="status-pill ${getStatusPillClass(rec.display_status || rec.status)}">
                            ${rec.display_status || 'Successful'}
                        </span>
                    </td>
                    <td data-label="Action" class="px-5 py-4">${renderAdminCheckoutAction(rec, selectedDate)}</td>
                </tr>
            `).join('');

            countEl.textContent = data.attendance.length;
            todayMarksEl.textContent = data.attendance.length;
            liveCountEl.textContent = data.attendance.length;

            const uniqueUsers = new Set(data.attendance.map((rec) => rec.emp_id || rec.name || Math.random()));
            totalUsersEl.textContent = uniqueUsers.size;

            const withConfidence = data.attendance.filter((rec) => typeof rec.confidence === 'number');
            if (withConfidence.length) {
                const avg = withConfidence.reduce((sum, rec) => sum + rec.confidence, 0) / withConfidence.length;
                document.getElementById('accuracyRate').textContent = `${(avg * 100).toFixed(1)}%`;
            }

            const latestRecord = data.attendance[data.attendance.length - 1];
            setBreakButtonState(Boolean(latestRecord && String(latestRecord.status || '').toLowerCase() === 'on break' && !latestRecord.check_out));

            const latestDate = data.selected_date || selectedDate;
            const isTodayView = latestDate === currentToday;
            if (isTodayView && latestRecord) {
                showAttendanceActionResult(
                    `User Name: ${latestRecord.name || 'Unknown'} | User ID: ${latestRecord.emp_id || '-'} | Department: ${latestRecord.department || 'General'} | Status: ${latestRecord.display_status || 'Successful'}`,
                    (latestRecord.display_status || '').toLowerCase() === 'queued' ? 'warning' : 'success'
                );
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="8" class="px-5 py-14 text-center text-sm text-slate-400">No attendance records found for the selected date.</td></tr>';
            countEl.textContent = '0';
            todayMarksEl.textContent = '0';
            liveCountEl.textContent = '0';
            totalUsersEl.textContent = '0';
            setBreakButtonState(false);
            showAttendanceActionResult(`No attendance records found for ${formatDate(selectedDate)}.`, 'info');
        }
    } catch (err) {
        console.error('Attendance load error:', err);
        showControlResult('Unable to load attendance records.', 'error');
    }
}

function renderAdminCheckoutAction(record, selectedDate) {
    const hasCheckIn = Boolean(record.check_in || record.time);
    const hasCheckOut = Boolean(record.check_out);
    const userId = record.user_id || '';

    if (!hasCheckIn) {
        return '<span class="text-xs font-semibold text-slate-400">No Check-In</span>';
    }

    if (hasCheckOut) {
        return '<span class="rounded-xl bg-emerald-50 px-3 py-2 text-xs font-extrabold text-emerald-700">Checked Out</span>';
    }

    if (!userId) {
        return '<span class="text-xs font-semibold text-amber-600">No User Link</span>';
    }

    return `
        <button
            type="button"
            class="admin-checkout-btn rounded-xl bg-[#0a607b] px-4 py-2 text-xs font-extrabold text-white transition hover:bg-[#084f67]"
            data-user-id="${userId}"
            data-date="${selectedDate}"
        >
            Check-Out
        </button>
    `;
}

function formatDate(value) {
    if (!value) return '-';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleDateString();
    }
    const parts = String(value).split(' ');
    return parts[0] || value;
}

function formatTime(value) {
    if (!value) return '-';
    const parsed = new Date(value);
    if (!isNaN(parsed)) {
        return parsed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    const parts = String(value).split(' ');
    return parts.slice(1).join(' ') || value;
}

function showControlResult(message, type = 'info') {
    const el = document.getElementById('controlResult');
    el.textContent = message;
    el.className = `message-card ${toneClass(type)}`;
}

function getStatusPillClass(status) {
    const normalized = String(status || '').toLowerCase();
    if (['successful', 'present', 'on time', 'final out'].includes(normalized)) return 'tone-success';
    if (['on break', 'short leave', 'buffer'].includes(normalized)) return 'tone-warning';
    if (['late', 'half day', 'early exit', 'queued'].includes(normalized)) return 'tone-error';
    return 'tone-info';
}

setBreakButtonState(false);
initMainCamera();
loadAttendance();
attendancePoll = setInterval(loadAttendance, 3000);

window.addEventListener('beforeunload', () => {
    if (videoStream) videoStream.getTracks().forEach((track) => track.stop());
    if (continuousInterval) clearInterval(continuousInterval);
    if (attendancePoll) clearInterval(attendancePoll);
});
