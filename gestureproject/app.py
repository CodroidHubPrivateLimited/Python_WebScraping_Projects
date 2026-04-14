import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def is_thumb_open(lm_list):
    tip_to_wrist = distance(lm_list[4], lm_list[0])
    joint_to_wrist = distance(lm_list[3], lm_list[0])

    if tip_to_wrist > joint_to_wrist + 10:
        return 1
    else:
        return 0

def count_fingers(lm_list):
    fingers = []


    fingers.append(is_thumb_open(lm_list))


    tips = [8, 12, 16, 20]
    for tip in tips:
        if lm_list[tip][1] < lm_list[tip - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    total_fingers = 0
    text = ""

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:

            lm_list = []
            h, w, c = img.shape

            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

         
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            fingers = count_fingers(lm_list)

            total_fingers += fingers.count(1)

    text = str(total_fingers)


    if total_fingers == 1:
        text = "Hello"
    elif total_fingers == 2:
        text = "Yes"
    elif total_fingers == 5:
        text = "Good"

 
    cv2.rectangle(img, (20, 20), (350, 120), (0, 0, 0), -1)

  
    cv2.putText(img, text, (50, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                2, (0, 255, 0), 3)

    cv2.imshow("Final Hand Gesture System", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()