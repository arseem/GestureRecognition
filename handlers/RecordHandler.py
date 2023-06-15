import cv2
import os
import time
from copy import deepcopy
import numpy as np
import json

import mediapipe as mp

from handlers.Gesture import Gesture


# class for handling recirding on new gestures
class RecordHandler:
    def __init__(self, config_instance):
        self._gesture_name = ''
        self._gesture_type = ''

        self._num_frames = config_instance.num_frames
        self._num_takes = config_instance.num_takes

        self._path_base = config_instance.datasets_path
        self._info_path = os.path.join(self._path_base, 'info.json')
        self._data_path = os.path.join(self._path_base, 'raw')
        self.recording = False

        self.width = 640
        self.height = 480


    def start_recording(self, gesture_name):
        self._gesture_name = gesture_name
        self.recording = True


    def record(self, cap, width=640, height=480):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands

        currentTime = 0
        previousTime = 0

        gestures_data = np.ndarray((self._num_takes, self._num_frames, 21, 3), dtype=np.float32)

        with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1
        ) as hands:
            _, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = cv2.flip(image, 1)
            image_copy = image

            cv2.putText(image_copy, f"Next gesture: {self._gesture_name}", (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
            cv2.putText(image_copy, f"Waiting...", (10, 75), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2) 
            #cv2.imshow("Data capture", image_copy)
            if image.shape[1] != width or image.shape[0] != height:
                image = cv2.resize(image, (width, height))
                self.width = width
                self.height = height
                
            _, jpeg = cv2.imencode('.jpg', image)

            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
            
            for take in range(self._num_takes):
                n_frame = 0
                cv2.putText(image_copy, f"Preparing for take {take+1}", (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                cv2.putText(image_copy, f"Waiting...", (10, 75), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2) 
                cv2.imshow("Data capture", image_copy)
                cv2.waitKey(1000)
                
                while n_frame<self._num_frames:
                    _, frame = cap.read()
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

                    image = cv2.flip(image, 1)
                    cv2.putText(image, str(int(fps))+" FPS", (10, 35), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                    image_copy = deepcopy(image)
                    if results.multi_hand_landmarks:
                        for kp in range(len(results.multi_hand_landmarks[0].landmark)):
                            gestures_data[take][n_frame][kp][0] = results.multi_hand_landmarks[0].landmark[kp].x
                            gestures_data[take][n_frame][kp][1] = results.multi_hand_landmarks[0].landmark[kp].y
                            gestures_data[take][n_frame][kp][2] = results.multi_hand_landmarks[0].landmark[kp].z

                        cv2.putText(image, f"Gesture: {self._gesture_name}", (10, 55), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                        cv2.putText(image, f"Take: {take+1}/{self._num_takes}", (10, 75), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)
                        cv2.putText(image, f"Frame: {n_frame}/{self._num_frames}", (10, 95), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), 2)

                        n_frame+=1
                        
                    #cv2.imshow("Data capture", image)

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
                    
                    if cv2.waitKey(5) & 0xFF == ord('q'):
                        break

            np.save(f"{self._data_path}/{self._gesture_name}.npy", np.concatenate((gestures_data, gestures_data)))
            
            with open(self._info_path, 'r+') as f:
                info = json.load(f)
                info['gestures'].append(self._gesture_name)
                f.seek(0)
                f.truncate()
                json.dump(info, f, indent=4)


            self.recording = False