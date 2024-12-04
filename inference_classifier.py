import pickle
import random
import cv2
import mediapipe as mp
import numpy as np
import time

# Load the trained model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Initialize webcam
cap = cv2.VideoCapture(0)

# Mediapipe configurations
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Label dictionary
labels_dict = {
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'E',
    5: 'F',
    6: 'G',
    7: 'H',
    8: 'I',
    9: 'J',
    10: 'K',
    11: 'L',
    12: 'M',
    13: 'N',
    14: 'O',
    15: 'P',
    16: 'Q',
    17: 'R',
    18: 'S',
    19: 'T',
    20: 'U',
    21: 'V',
    22: 'W',
    23: 'X',
    24: 'Y',
    25: 'Z',
    26: 'nothing',
    27: 'del',
    28: 'space'
}

# Game settings
score = 0
time_limit = 30  # seconds
start_time = time.time()

# Function to display a random target letter
def get_random_letter():
    return random.choice(list(labels_dict.values())[:26])  # Only letters A-Z

# Start the game
target_letter = get_random_letter()

while True:
    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()
    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            # Ensure data_aux has the expected feature size (84 features)
            required_size = 84
            if len(data_aux) < required_size:
                data_aux += [0] * (required_size - len(data_aux))
            elif len(data_aux) > required_size:
                data_aux = data_aux[:required_size]

            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]

            # Check if the predicted character matches the target letter
            if predicted_character == target_letter:
                score += 1
                target_letter = get_random_letter()  # Generate a new target letter

    # Display target letter, score, and remaining time
    remaining_time = time_limit - int(time.time() - start_time)
    font = cv2.FONT_HERSHEY_SIMPLEX  
    thickness = 3  # Bold effect

    target_text = f"Target: {target_letter}"
    target_size = cv2.getTextSize(target_text, font, 1.2, thickness)[0]
    target_x = (W - target_size[0]) // 2
    target_y = 70

    # Target
    cv2.rectangle(frame, (target_x - 10, target_y - 40), (target_x + target_size[0] + 10, target_y + 10), (255, 255, 255), -1)
    cv2.putText(frame, target_text, (target_x, target_y), font, 1.2, (0, 0, 0), thickness)

    # Score
    cv2.rectangle(frame, (10, 20), (300, 80), (255, 255, 255), -1)
    cv2.putText(frame, f"Score: {score}", (20, 50), font, 1.2, (0, 0, 0), thickness)

    # Time remaining
    cv2.rectangle(frame, (10, 80), (300, 140), (255, 255, 255), -1)
    cv2.putText(frame, f"Time: {remaining_time}s", (20, 110), font, 1.2, (0, 0, 0), thickness)

    # End game if time is up
    if remaining_time <= 0:
        # Draw white rectangle for "Game Over!"
        cv2.rectangle(frame, (W // 2 - 200, H // 2 - 50), (W // 2 + 200, H // 2 + 100), (255, 255, 255), -1)
        cv2.putText(frame, "Game Over!", (W // 2 - 180, H // 2), font, 2, (0, 0, 0), 4)

        s = f"Your final score is: {score}"
        cv2.putText(frame, s, (W // 2 - 180, H // 2 + 50), font, 1, (0, 0, 0), 3)

        cv2.imshow('Game', frame)
        cv2.waitKey(5000)
        break

    cv2.imshow('Game', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"Your final score is: {score}")