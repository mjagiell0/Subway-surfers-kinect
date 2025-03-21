from time import sleep

import cv2
import mediapipe as mp

# Inicjalizacja modelu
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Otwórz wideo
cap = cv2.VideoCapture("assets/test3.mp4")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

upper_part = height // 5
lower_part = height - upper_part
left_part = width // 3
right_part = width - left_part

# Inicjalizacja pozycji
pos_vertical = "UNKNOWN"
pos_horizontal = "UNKNOWN"
prev_pos_vertical = "UNKNOWN"
prev_pos_horizontal = "UNKNOWN"

line_colour = (255, 0, 0)
text_colour = (0, 255, 0)

frame_counter = 0
access_count = 10 # Ze względu na brak GPU. W przeciwnym wypadku wstawić 1
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_counter % access_count == 0:
        # Konwersja do RGB (MediaPipe wymaga takiego formatu)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Przetwarzanie klatki przez model
        body = pose.process(rgb_frame)


        if body.pose_landmarks:
            # Pobranie pozycji środka bioder
            left_hip = body.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = body.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            left_thumb = body.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_THUMB]
            right_thumb = body.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_THUMB]

            # Sprawdzenie, czy wykryto poprawne punkty
            if left_hip.visibility > 0.5 and right_hip.visibility > 0.5:
                # Obliczenie średniej pozycji X
                center_x_hip = int((left_hip.x + right_hip.x) / 2 * frame.shape[1])
                center_y_thumbs = int((left_thumb.y + right_thumb.y) / 2 * frame.shape[0])
                # Określenie nowej pozycji
                new_pos_vertical = "UNKNOWN"
                if center_x_hip <= left_part:
                    new_pos_vertical = "LEFT"
                elif center_x_hip < right_part:
                    new_pos_vertical = "CENTRE"
                else:
                    new_pos_vertical = "RIGHT"

                new_pos_horizontal = "UNKNOWN"
                if center_y_thumbs <= upper_part:
                    new_pos_horizontal = "JUMP"
                elif center_y_thumbs < lower_part:
                    new_pos_horizontal = "NOTHING"
                else:
                    new_pos_horizontal = "CROUCH"

                # Zmieniamy `position` tylko, jeśli faktycznie zmieniła się strefa
                if new_pos_vertical != prev_pos_vertical:
                    # TODO: Dodać wysyłanie sygnałów strzałek do gry w przeglądarce
                    pos_vertical = new_pos_vertical
                    prev_pos_vertical = new_pos_vertical  # Aktualizacja historii pozycji

                if new_pos_horizontal != prev_pos_horizontal:
                    pos_horizontal = new_pos_horizontal
                    prev_pos_horizontal = new_pos_horizontal

    # Rysowanie linii podziału
    cv2.line(frame, (left_part, upper_part), (left_part, lower_part), line_colour, 2)
    cv2.line(frame, (right_part, upper_part), (right_part, lower_part), line_colour, 2)
    cv2.line(frame, (0, upper_part), (width, upper_part), line_colour, 2)
    cv2.line(frame, (0, lower_part), (width, lower_part), line_colour, 2)
    # Wyświetlenie pozycji na obrazie
    cv2.putText(frame, pos_vertical, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_colour, 2)
    cv2.putText(frame, pos_horizontal, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, text_colour, 2)

    cv2.imshow("Pose Tracking", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break
    frame_counter += 1


cap.release()
cv2.destroyAllWindows()
