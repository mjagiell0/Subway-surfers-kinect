import cv2
import mediapipe as mp
from positions import Horizontal, Vertical
from pyautogui import press


# Inicjalizacja modelu
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Otwórz wideo
cap = cv2.VideoCapture(0)
# cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

upper_part = height // 3
lower_part = height - upper_part
left_part = width // 3 + 15
right_part = width - left_part

# Inicjalizacja pozycji
pos_vertical = Vertical.CENTER
pos_horizontal = Horizontal.NOTHING
prev_pos_vertical = Vertical.CENTER
prev_pos_horizontal = Horizontal.NOTHING

line_colour = (255, 0, 0)
text_colour = (0, 255, 0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

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

            cv2.circle(frame, (center_x_hip, int((left_hip.y + right_hip.y) / 2 * frame.shape[0])), 10, (0, 0, 255),
                       -1)
            cv2.circle(frame, (int((left_thumb.x + right_thumb.x) / 2 * frame.shape[1]), center_y_thumbs), 10,
                       (0, 0, 255),
                       -1)
            # Określenie nowej pozycji
            new_pos_vertical = Vertical.CENTER
            if center_x_hip <= left_part:
                new_pos_vertical = Vertical.LEFT
            elif center_x_hip < right_part:
                new_pos_vertical = Vertical.CENTER
            else:
                new_pos_vertical = Vertical.RIGHT

            new_pos_horizontal = Horizontal.NOTHING
            if center_y_thumbs <= upper_part:
                new_pos_horizontal = Horizontal.UP
            elif center_y_thumbs < lower_part:
                new_pos_horizontal = Horizontal.NOTHING
            else:
                new_pos_horizontal = Horizontal.DOWN

            # Zmieniamy `position` tylko, jeśli faktycznie zmieniła się strefa
            if new_pos_vertical != prev_pos_vertical:
                if prev_pos_vertical == Vertical.RIGHT and new_pos_vertical == Vertical.CENTER:
                    press("left")
                elif prev_pos_vertical == Vertical.LEFT and new_pos_vertical == Vertical.CENTER:
                    press("right")
                elif prev_pos_vertical == Vertical.CENTER:
                    press((str(new_pos_vertical)).lower())

                pos_vertical = new_pos_vertical
                prev_pos_vertical = new_pos_vertical

            if new_pos_horizontal != prev_pos_horizontal:
                if new_pos_horizontal == Horizontal.UP:
                    press("up")
                elif new_pos_horizontal == Horizontal.DOWN:
                    press("down")

                pos_horizontal = new_pos_horizontal
                prev_pos_horizontal = new_pos_horizontal

    # Rysowanie linii podziału
    cv2.line(frame, (left_part, upper_part), (left_part, lower_part), line_colour, 2)
    cv2.line(frame, (right_part, upper_part), (right_part, lower_part), line_colour, 2)
    cv2.line(frame, (0, upper_part), (width, upper_part), line_colour, 2)
    cv2.line(frame, (0, lower_part), (width, lower_part), line_colour, 2)
    # Wyświetlenie pozycji na obrazie
    cv2.putText(frame, str(pos_vertical), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_colour, 2)
    cv2.putText(frame, str(pos_horizontal), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, text_colour, 2)

    cv2.imshow("window", frame)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
