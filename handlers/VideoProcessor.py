import cv2
import time
import asyncio
import numpy as np

import mediapipe as mp


class VideoProcessor:

    def __init__(self, model_loader_instance, config_instance):
        self.__get_info_from_model_loader(model_loader_instance)
        self.width = 640
        self.height = 480
        self._sequence = []
        self._last_index_position = None
        self._index_position_history = []
        self.new_prediction = asyncio.Event()

        self._track_threshold = config_instance.track_confidence_threshold
        self._change_threshold = config_instance.change_confidence_threshold
        self._gesture_history = []
        self._last_gesture = None
        self._history_length = 5

        self.fps = 0
        self.current_scores = [0]*len(self._gestures)
        self._current_prediciton = None
        self.current_prediction = None

    def __get_info_from_model_loader(self, model_loader_instance):
        self._model = model_loader_instance.model
        self._gestures = model_loader_instance._model_info['gestures']
        self._sequence_length = model_loader_instance._model_info['num_frames']

    def __get_predictions(self):
        input_details = self._model.get_input_details()
        output_details = self._model.get_output_details()
        self._model.set_tensor(input_details[0]['index'], np.expand_dims(self._sequence, axis=0))
        self._model.invoke()

        self.current_scores = self._model.get_tensor(output_details[0]['index'])[0]
        self._current_prediciton = self._gestures[np.argmax(self.current_scores)]
        self.new_prediction.set()
    
    def __prepare_data(self, data):
        current_landmarks = []
        for i in range(21):
            current_landmarks.append(data[0].landmark[i].x)
            current_landmarks.append(data[0].landmark[i].y)
            current_landmarks.append(data[0].landmark[i].z)

        current_landmarks = np.array(current_landmarks).astype(np.float32)

        if len(self._sequence)<self._sequence_length:
            self._sequence.append(current_landmarks)
        else:
            self._sequence = self._sequence[1:]
            self._sequence.append(current_landmarks)

    def __check_sequence(self):
        if len(self._sequence) == self._sequence_length:
            self.__get_predictions()
            return True
        else:
            self.current_scores = [0.0 for _ in range(len(self._gestures))]
            return False

    def process_feed(self, camera_feed, width=640, height=480):
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
                predictions_task = None
                self._last_gesture = None
                _, frame = cam.read()
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                currentTime = time.time()
                self.fps = 1 / (currentTime-previousTime)
                previousTime = currentTime

                if results.multi_hand_landmarks:
                    self.__prepare_data(results.multi_hand_landmarks)
                    #predictions_task = asyncio.create_task(self.__check_sequence())

                    mp_drawing.draw_landmarks(
                        image,
                        results.multi_hand_landmarks[0],
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style())
                    
                    index_finger_tip = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    x = int(index_finger_tip.x * image.shape[1])
                    y = int(index_finger_tip.y * image.shape[0])
                    self._last_index_position = (x, y)

                else:
                    self._sequence = self._sequence[1:]
                    self._last_index_position = None

                image = cv2.flip(image, 1)
                # cv2.putText(image, str(int(self.fps))+" FPS", (150, 35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                # cv2.putText(image, f"{'->'.join(self._gesture_history)}", (0, 480-35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                if self.__check_sequence():
                    # for i, (g, p) in enumerate(zip(self._gestures, self.current_scores)):
                    #     cv2.putText(image, f"{g}: {p:.2f}", (0, 35+i*20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                    if ((max(self.current_scores) > self._track_threshold and (self._gesture_history and self._gesture_history[-1] == self._current_prediciton)) or (max(self.current_scores) > self._change_threshold and (not self._gesture_history  or self._gesture_history[-1] != self._current_prediciton))):
                        # cv2.putText(image, self._current_prediciton, (150, 70), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                        self.current_prediction = self._current_prediciton
                        self._last_gesture = self._current_prediciton

                if self._last_gesture:
                    self._gesture_history.append(self._last_gesture)

                elif len(self._gesture_history) > 0:
                    self._gesture_history = self._gesture_history[1:]
                    self.current_prediction = None
                
                else:
                    self.current_prediction = None
                    
                if len(self._gesture_history) > self._history_length:
                    self._gesture_history = self._gesture_history[1:]

                if image.shape[1] != width or image.shape[0] != height:
                    image = cv2.resize(image, (width, height))
                    self.width = width
                    self.height = height
                
                ret, jpeg = cv2.imencode('.jpg', image)

                if not ret:
                    break

                frame_bytes = jpeg.tobytes()

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')