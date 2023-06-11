import cv2
import time

import mediapipe as mp


class VideoProcessor:
    def __init__(self, model_loader_instance):
        self.get_info_from_model_loader(model_loader_instance)
        self.width = 640
        self.height = 480

    def get_info_from_model_loader(self, model_loader_instance):
        self._model = model_loader_instance.model
        self._gestures = model_loader_instance.model_info['gestures']
        self._sequence_length = model_loader_instance.model_info['num_frames']

    def get_predictions(self, camera_feed, width=640, height=480):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands

        currentTime = 0
        previousTime = 0

        cam  =  cv2.VideoCapture(0)
        with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1
        ) as hands:
            
            while camera_feed.isOpened():
                _, frame = cam.read()
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                currentTime = time.time()
                fps = 1 / (currentTime-previousTime)
                previousTime = currentTime

                if results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        results.multi_hand_landmarks[0],
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style())
                    
                    index_finger_tip = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    x = int(index_finger_tip.x * image.shape[1])
                    y = int(index_finger_tip.y * image.shape[0])

                image = cv2.flip(image, 1)
                cv2.putText(image, str(int(fps))+" FPS", (10, 35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                
                if results.multi_hand_landmarks:
                    cv2.putText(image, f"Index position: {x}X {y}Y", (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                if self.width != width or self.height != height:
                    image = cv2.resize(image, (width, height))
                    self.width = width
                    self.height = height
                
                ret, jpeg = cv2.imencode('.jpg', image)
                
                if not ret:
                    break

                frame_bytes = jpeg.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')