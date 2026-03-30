# Gesture Recognition Project

Improved hand gesture recognition using MediaPipe and OpenCV.

## Features
- 25+ gestures (Hello, Numbers 0-5, OK, Rock/Paper/Scissors, etc.)
- Fixed thumb detection, multi-hand support
- Gesture smoothing (anti-jitter)
- Live UI: FPS, confidence, history, hand count
- Audio feedback (tones)
- Controls: ESC=quit, S=screenshot, R=record, SPACE=mute, C=calibrate
- Logs to `gestures_log.csv`

## Setup
1. Activate env: `my_env\\Scripts\\activate`
2. Install deps: `pip install -r requirements.txt`
3. Run: `python app.py`

## Adding Gestures
Edit `gestures.py` GESTURES dict. Format: (thumb,index,middle,ring,pinky) -> (name, emoji)

## Logs
`gestures_log.csv`: Analyze with pandas.

