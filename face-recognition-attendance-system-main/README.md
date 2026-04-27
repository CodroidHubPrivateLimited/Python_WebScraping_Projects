v # Face Recognition Attendance System with Registration

## Setup
1. Activate venv: `my_env\\Scripts\\activate.bat`
2. Install deps: `my_env\\Scripts\\pip.exe install -r my_env/requirements.txt` (or pip install deepface)
3. `python main.py`

## Usage
**Register new employee** (0): Input name → capture 5 face photos → saved in ./Images/
**Attendance** (1/2/3): CLI/GUI/Web → face match → log in attendance.xlsx

**Register first!** Then attendance works.
- Photos: {name}_1.jpg, {name}_2.jpg etc.
- Webcam issues: Check privacy settings.

## Features
- Dynamic registration
- Multiple modes
- Excel logs with time/date/status

Test: Register "test" → attendance shows "test Present".
