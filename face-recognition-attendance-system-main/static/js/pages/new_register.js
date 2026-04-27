let registerStream = null;
const requiredCaptures = 5;
let capturedImages = [];

const registerVideo = document.getElementById('registerVideo');
const captureButton = document.getElementById('captureButton');
const registerForm = document.getElementById('registerForm');
const regResult = document.getElementById('regResult');
const captureStatus = document.getElementById('captureStatus');
const lightingStatus = document.getElementById('lightingStatus');
const submitRegistration = document.getElementById('submitRegistration');
const captureCountText = document.getElementById('captureCountText');
const capturePreviewGrid = document.getElementById('capturePreviewGrid');
const resetCaptures = document.getElementById('resetCaptures');
const themeToggle = document.getElementById('themeToggle');

themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark-theme');
    const isDark = document.documentElement.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

async function initRegisterCamera() {
    if (registerStream) {
        return registerStream;
    }

    try {
        registerStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: 1280, height: 720 }
        });
        registerVideo.srcObject = registerStream;
        registerVideo.classList.remove('hidden');
        lightingStatus.textContent = 'Studio Quality Detected';
        captureStatus.textContent = 'Face Alignment Active';
        return registerStream;
    } catch (err) {
        showRegResult(`Camera error: ${err.message}`, 'error');
        lightingStatus.textContent = 'Camera Access Required';
        throw err;
    }
}

async function captureImage(videoEl) {
    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth || 1280;
    canvas.height = videoEl.videoHeight || 720;
    canvas.getContext('2d').drawImage(videoEl, 0, 0);
    return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
}

function showRegResult(message, type = 'info') {
    regResult.textContent = message;
    regResult.className = `status-box rounded-2xl px-4 py-4 text-sm font-semibold ${
        type === 'success' ? 'bg-emerald-50 text-emerald-700' :
            type === 'error' ? 'bg-rose-50 text-rose-700' :
                'bg-slate-50 text-slate-600'
    }`;
    regResult.classList.remove('hidden');
}

function updateCaptureUI() {
    captureCountText.textContent = `${capturedImages.length} / ${requiredCaptures} images captured`;
    captureStatus.textContent = capturedImages.length >= requiredCaptures
        ? 'Minimum Capture Complete'
        : `Capture ${requiredCaptures - capturedImages.length} more image(s)`;

    capturePreviewGrid.innerHTML = '';
    for (let i = 0; i < requiredCaptures; i += 1) {
        const slot = document.createElement('div');
        slot.className = 'thumb flex h-20 items-center justify-center overflow-hidden rounded-2xl text-xs font-bold';

        if (capturedImages[i]) {
            if (!capturedImages[i].previewUrl) {
                capturedImages[i].previewUrl = URL.createObjectURL(capturedImages[i]);
            }
            const img = document.createElement('img');
            img.src = capturedImages[i].previewUrl;
            img.className = 'h-full w-full object-cover';
            slot.appendChild(img);
        } else {
            slot.classList.add('text-slate-400');
            slot.textContent = String(i + 1);
        }

        capturePreviewGrid.appendChild(slot);
    }
}

captureButton.addEventListener('click', async () => {
    const original = captureButton.innerHTML;
    captureButton.innerHTML = '<span class="material-symbols-outlined animate-spin">autorenew</span> Capturing...';
    captureButton.disabled = true;

    try {
        await initRegisterCamera();
        const imageBlob = await captureImage(registerVideo);
        capturedImages.push(imageBlob);
        updateCaptureUI();

        if (capturedImages.length >= requiredCaptures) {
            showRegResult('5 face images captured. You can now complete enrollment.', 'success');
        } else {
            showRegResult(`Image ${capturedImages.length} captured. Please capture ${requiredCaptures - capturedImages.length} more.`, 'success');
        }
    } catch (err) {
        showRegResult(`Capture failed: ${err.message}`, 'error');
    }

    captureButton.innerHTML = original;
    captureButton.disabled = false;
});

resetCaptures.addEventListener('click', () => {
    capturedImages.forEach((blob) => {
        if (blob.previewUrl) {
            URL.revokeObjectURL(blob.previewUrl);
        }
    });
    capturedImages = [];
    updateCaptureUI();
    showRegResult('Captured images reset. Please capture 5 new images.', 'info');
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('regName').value.trim();
    const department = document.getElementById('regDepartment').value.trim();
    const empId = document.getElementById('regEmpId').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const purpose = document.getElementById('regPurpose').value.trim();
    const original = submitRegistration.innerHTML;

    submitRegistration.innerHTML = '<span class="material-symbols-outlined animate-spin">autorenew</span> Saving...';
    submitRegistration.disabled = true;

    try {
        if (capturedImages.length < requiredCaptures) {
            throw new Error(`Please capture at least ${requiredCaptures} images before saving`);
        }

        const formData = new FormData();
        formData.append('name', name);
        formData.append('department', department || 'General');
        formData.append('emp_id', empId);
        formData.append('email', email);
        formData.append('password', password);
        formData.append('purpose', purpose);
        capturedImages.forEach((imageBlob, index) => {
            formData.append('images', imageBlob, `face_${index + 1}.jpg`);
        });

        const res = await fetch('/register_face', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
            showRegResult(`Employee account created for ${name}. Login email: ${data.email || email}. Captured images: ${data.saved_count || capturedImages.length}.`, 'success');
            captureStatus.textContent = 'Enrollment Saved';
            registerForm.reset();
            capturedImages.forEach((blob) => {
                if (blob.previewUrl) {
                    URL.revokeObjectURL(blob.previewUrl);
                }
            });
            capturedImages = [];
            updateCaptureUI();
        } else {
            showRegResult(data.message || 'Registration failed.', 'error');
        }
    } catch (err) {
        showRegResult(`Error: ${err.message}`, 'error');
    }

    submitRegistration.innerHTML = original;
    submitRegistration.disabled = false;
});

initRegisterCamera().catch(() => {});
updateCaptureUI();

window.addEventListener('beforeunload', () => {
    capturedImages.forEach((blob) => {
        if (blob.previewUrl) {
            URL.revokeObjectURL(blob.previewUrl);
        }
    });
    if (registerStream) {
        registerStream.getTracks().forEach((track) => track.stop());
    }
});
