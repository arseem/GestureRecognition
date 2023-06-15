import pyautogui
import threading
import math
import json


class ActionHandler:

    def __init__(self, video_processor_instance, js_keys):
        self._scroll_sensitivity = 5
        self._cursor_sensitivity = 10
        self._trigger = video_processor_instance.new_prediction
        self._trigger_lock = video_processor_instance.prediction_lock
        self._video_processor = video_processor_instance

        self._js_keys = js_keys

        self._click_button = 'left'
        self._keys_to_press = []

        self._move_mouse_thread = threading.Thread(target=self._move_mouse, daemon=True)
        self._move_mouse_event = threading.Event()
        self._move_mouse_position = (0, 0)
        self._move_mouse_velocity = 0
        self._move_mouse_lock = threading.Lock()
        
        self._hold_mouse_thread = threading.Thread(target=self._hold_mouse, daemon=True)
        self._hold_mouse_down_event = threading.Event()
        self._hold_mouse_up_event = threading.Event()

        self._click_mouse_thread = threading.Thread(target=self._click_mouse, daemon=True)
        self._click_mouse_event = threading.Event()
        self._click_mouse_lock = threading.Lock()

        self._scroll_mouse_thread = threading.Thread(target=self._scroll_mouse, daemon=True)    
        self._scroll_mouse_event = threading.Event()
        self._scroll_mouse_range = 0
        self._scroll_mouse_lock = threading.Lock()

        self._press_keys_thread = threading.Thread(target=self._press_keys, daemon=True)
        self._press_keys_event = threading.Event()
        self._press_keys_lock = threading.Lock()

        self._notifier_thread = threading.Thread(target=self._notifier, daemon=True)

        self._notifier_thread.start()
        self._move_mouse_thread.start()
        self._hold_mouse_thread.start()
        self._click_mouse_thread.start()
        self._scroll_mouse_thread.start()
        self._press_keys_thread.start()


    def _notifier(self):
        while True:
            if self._trigger.wait(20):
                self._trigger.clear()
                self._handle_action()


    def _handle_action(self):
        (current_prediction, _) = self._video_processor.get_current_prediction()
        index_position_history = self._video_processor._index_position_history

        if current_prediction.on:

            if current_prediction.action == 'MOVE' or current_prediction.action == 'DRAG':
                with self._move_mouse_lock:
                    sens_x = self._cursor_sensitivity if abs((index_position_history[-2][0] - index_position_history[-1][0])) > 1 else 1
                    sens_y = self._cursor_sensitivity if abs((index_position_history[-1][1] - index_position_history[-2][1])) > 1 else 1

                    self._move_mouse_position = ((index_position_history[-2][0] - index_position_history[-1][0])*sens_x, (index_position_history[-1][1] - index_position_history[-2][1])*sens_y)
                    self._move_mouse_velocity = math.sqrt((index_position_history[-2][0] - index_position_history[-1][0])**2 + (index_position_history[-1][1] - index_position_history[-2][1])**2) * self._video_processor.fps
                self._move_mouse_event.set()
                if current_prediction.action == 'DRAG':
                    self._hold_mouse_down_event.set()

            elif current_prediction.action == 'LEFT':
                with self._click_mouse_lock:
                    self._click_button = 'left'
                self._click_mouse_event.set()

            elif current_prediction.action == 'RIGHT':
                with self._click_mouse_lock:
                    self._click_button = 'right'
                self._click_mouse_event.set()

            elif current_prediction.action == 'SCROLL':
                with self._scroll_mouse_lock:
                    self._scroll_mouse_range = self._scroll_sensitivity * (index_position_history[-1][1] - index_position_history[-2][1])
                self._scroll_mouse_event.set()

            elif current_prediction.action == 'none':
                pass

            else:
                if current_prediction.one_shot and (len(self._video_processor._gesture_history) < 2 or self._video_processor._gesture_history[-2] != current_prediction.name) or not current_prediction.one_shot:
                    try:
                        with self._press_keys_lock:
                            self._keys_to_press = json.loads(current_prediction.action) if current_prediction.action[0] == '[' else [{'key':current_prediction.action, 'action':'down'}]
                        self._press_keys_event.set()
                    except json.JSONDecodeError:
                        pass

    
    def _move_mouse(self):
        size = pyautogui.size()
        while True:
            if self._move_mouse_event.wait(20):
                with self._move_mouse_lock:
                    move_to = self._move_mouse_position
                    velocity = self._move_mouse_velocity if self._move_mouse_velocity > 0 else 30

                if pyautogui.position()[0] + move_to[0] in range(1, size[0]) and pyautogui.position()[1] + move_to[1] in range(1, size[1]):
                    try:
                        pyautogui.moveRel(*move_to, duration = 1/velocity, _pause=False)

                    except pyautogui.FailSafeException:
                        pass

                self._move_mouse_event.clear()


    def _hold_mouse(self):
        while True:
            if self._hold_mouse_down_event.wait(20):
                pyautogui.mouseDown(button='left')
                self._hold_mouse_up_event.wait()
                pyautogui.mouseUp(button='left')
                self._hold_mouse_up_event.clear()
                self._hold_mouse_down_event.clear()


    def _click_mouse(self):
        while True:
            if self._click_mouse_event.wait(20):
                pyautogui.click(button=self._click_button)
                self._click_mouse_event.clear()


    def _scroll_mouse(self):
        while True:
            if self._scroll_mouse_event.wait(20):
                with self._scroll_mouse_lock:
                    scroll_range = self._scroll_mouse_range

                pyautogui.scroll(scroll_range, _pause=False)
                self._scroll_mouse_event.clear()

                while scroll_range>1:
                    scroll_range = scroll_range//2
                    pyautogui.scroll(scroll_range, _pause=False)
                    if self._scroll_mouse_event.wait(1/60*1000):
                        break

    def _press_keys(self):
        while True:
            if self._press_keys_event.wait(20):
                keys_down = []

                for action in self._keys_to_press:
                    if action['action'] == 'down':
                        keys_down.append(self._js_keys[action['key']] if action['key'] in self._js_keys else action['key'])
                        pyautogui.keyDown(self._js_keys[action['key']] if action['key'] in self._js_keys else action['key'], _pause=False)
                    elif action['action'] == 'up':
                        try:
                            keys_down.remove(self._js_keys[action['key']] if action['key'] in self._js_keys else action['key'])
                        except ValueError:
                            pyautogui.keyDown(self._js_keys[action['key']] if action['key'] in self._js_keys else action['key'], _pause=False)
                        pyautogui.keyUp(self._js_keys[action['key']] if action['key'] in self._js_keys else action['key'], _pause=False)

                for key in keys_down:
                    pyautogui.keyUp(key)

                self._press_keys_event.clear()