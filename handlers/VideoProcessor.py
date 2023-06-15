import copy
import cv2
import time
import numpy as np
import threading

import mediapipe as mp


class VideoProcessor:

    def __init__(self, model_loader_instance, config_instance, state_instance, record_handler_instance):
        self._record_handler = record_handler_instance
        self.__get_model_from_loader(model_loader_instance)
        self.__get_info_from_state(state_instance)
        self.width = 640
        self.height = 480
        self._sequence = []
        self._last_index_position = None
        self._index_position_history = []
        self.new_prediction = threading.Event()
        self.prediction_lock = threading.Lock()
        self.hand_detection_lock = threading.Lock()

        self._track_threshold = config_instance.track_confidence_threshold
        self._change_threshold = config_instance.change_confidence_threshold
        self._gesture_history = []
        self._last_gesture = None
        self._history_length = 5

        self.fps = 0
        self.current_scores = [0]*len(self._gestures)
        self._current_prediction = None
        self.current_prediction = None
        self.current_prediction_data = None
        self.current_prediction_score = 0
        self.hand_detection_results = None
        self.detection_enabled = True


    def __get_model_from_loader(self, model_loader_instance):
        self._model = model_loader_instance.model
        self._sequence_length = model_loader_instance._model_info['num_frames']


    def __get_info_from_state(self, state_instance):
        self._gestures = [gesture for gesture in state_instance.gestures]
        self.gestures = state_instance.gestures


    def __get_predictions(self):
        input_details = self._model.get_input_details()
        output_details = self._model.get_output_details()
        self._model.set_tensor(input_details[0]['index'], np.expand_dims(self._sequence, axis=0))
        self._model.invoke()

        self.current_scores = self._model.get_tensor(output_details[0]['index'])[0]
        self._current_prediction = self._gestures[np.argmax(self.current_scores)]

    
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
            # get x and y coords from sequence
            sequence = np.array(self._sequence).astype(np.float32)
            x_coords = sequence[:, 0::3]
            y_coords = sequence[:, 1::3]
            max_x = x_coords.max()
            min_x = x_coords.min()
            max_y = y_coords.max()
            min_y = y_coords.min()

            # normalize sequence
            sequence[:, 0::3] = (x_coords - min_x) / (max_x - min_x)
            sequence[:, 1::3] = (y_coords - min_y) / (max_y - min_y)

            self._sequence = list(sequence)
            self.__get_predictions()
            return True
        else:
            self.current_scores = [0.0 for _ in range(len(self._gestures))]
            self.current_prediction_data = None
            self.current_prediction_score = 0
            self._current_prediction = None
            return False


    def get_current_prediction(self):
        with self.prediction_lock:
            return self.current_prediction_data, self.current_prediction_score if self._current_prediction else (None, None)
        
    def toggle_recognition(self):
        self.detection_enabled = not self.detection_enabled


    def process_feed(self, camera_feed, width=640, height=480):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands

        currentTime = 0
        previousTime = 0

        cam = cv2.VideoCapture(0)
        with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1
        ) as hands:
            
            while camera_feed.isOpened() and not self._record_handler.recording:
                self._last_gesture = None
                _, frame = cam.read()
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                if self.detection_enabled:
                    results = hands.process(image)
                else:
                    results = None
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                currentTime = time.time()
                self.fps = 1 / (currentTime-previousTime)
                previousTime = currentTime

                with self.hand_detection_lock:
                    self.hand_detection_results = results

                if hasattr(results, 'multi_hand_landmarks') and results.multi_hand_landmarks:
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
                    self._index_position_history.append((x, y))
                    if len(self._index_position_history) > 10:
                        self._index_position_history = self._index_position_history[1:]

                    for i, (x, y) in enumerate(self._index_position_history):
                        cv2.circle(image, (x, y), 1+i, (255, 0, 255), 2)

                else:
                    self._sequence = self._sequence[1:]
                    self._last_index_position = None

                image = cv2.flip(image, 1)
                # cv2.putText(image, str(int(self.fps))+" FPS", (150, 35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                # cv2.putText(image, f"{'->'.join(self._gesture_history)}", (0, 480-35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                if self.__check_sequence():
                    # for i, (g, p) in enumerate(zip(self._gestures, self.current_scores)):
                    #     cv2.putText(image, f"{g}: {p:.2f}", (0, 35+i*20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                    #if ((max(self.current_scores) > self._track_threshold and (self._gesture_history and self._gesture_history[-1] == self._current_prediction)) or (max(self.current_scores) > self._change_threshold and (not self._gesture_history  or self._gesture_history[-1] != self._current_prediction))):
                    ## TU ZROBIC ZE JESLI TRACK TO TRACK A JESLI NIE TO ITERUJE AŻ ZNAJDZIE NAJWYZSZY KTORY PASUJE DO DETECTION
                    if (max(self.current_scores) >= self.gestures[self._current_prediction].tracking_sensitivity and (self._gesture_history and self._gesture_history[-1] == self._current_prediction)):
                        # cv2.putText(image, self._current_prediction, (150, 70), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                        self.current_prediction = self._current_prediction
                        self._last_gesture = self._current_prediction
                    
                    else:
                        temp_current_scores = list(copy.deepcopy(self.current_scores))
                        temp_gestures = list(copy.deepcopy(self._gestures))

                        while len(temp_current_scores)>0:
                            if max(temp_current_scores) >= self.gestures[self._gestures[np.argmax(temp_current_scores)]].detection_sensitivity:
                                self._current_prediction = self._gestures[np.argmax(temp_current_scores)]
                                self._last_gesture = self._current_prediction
                                break

                            else:
                                temp_gestures.pop(np.argmax(temp_current_scores))
                                temp_current_scores.pop(np.argmax(temp_current_scores))


                if self._last_gesture:
                    self._gesture_history.append(self._last_gesture)
                    self.current_prediction_data = self.gestures[self._current_prediction]
                    self.current_prediction_score = self.current_scores[np.argmax(self.current_scores)]
                    self.new_prediction.set()

                elif len(self._gesture_history) > 0:
                    self._gesture_history = self._gesture_history[1:]
                    self.current_prediction = None
                    self._current_prediction = None
                
                else:
                    self.current_prediction = None
                    self._current_prediction = None
                    
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
            
            cam.release()
