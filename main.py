from time import sleep

import cv2
import mediapipe as mp

# Inicjalizacja modelu
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Otwórz wideo
cap = cv2.VideoCapture("assets/test2.mp4")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

left_part = width // 3
right_part = (width // 3) * 2

# Inicjalizacja pozycji
position = "UNKNOWN"
previous_position = "UNKNOWN"

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
        results = pose.process(rgb_frame)



        if results.pose_landmarks:
            # Pobranie pozycji środka bioder
            left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

            # Sprawdzenie, czy wykryto poprawne punkty
            if left_hip.visibility > 0.5 and right_hip.visibility > 0.5:
                # Obliczenie średniej pozycji X
                center_x = int((left_hip.x + right_hip.x) / 2 * frame.shape[1])

                # Określenie nowej pozycji
                new_position = "UNKNOWN"
                if center_x <= left_part:
                    new_position = "LEFT"
                elif center_x < right_part:
                    new_position = "CENTRE"
                else:
                    new_position = "RIGHT"

                # Zmieniamy `position` tylko, jeśli faktycznie zmieniła się strefa
                if new_position != previous_position:
                    # TODO: Dodać wysyłanie sygnałów strzałek do gry w przeglądarce
                    position = new_position
                    previous_position = new_position  # Aktualizacja historii pozycji

    # Rysowanie linii podziału
    cv2.line(frame, (left_part, 0), (left_part, height), (255, 0, 0), 2)
    cv2.line(frame, (right_part, 0), (right_part, height), (255, 0, 0), 2)
    # Wyświetlenie pozycji na obrazie
    cv2.putText(frame, position, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Pose Tracking", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break
    frame_counter += 1


cap.release()
cv2.destroyAllWindows()
