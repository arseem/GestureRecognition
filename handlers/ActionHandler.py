import pyautogui
import threading


class ActionHandler:

    def __init__(self, video_processor_instance):
        self._gestures = video_processor_instance.gestures
        self._trigger = video_processor_instance.new_prediction

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

        self._scroll_mouse_thread = threading.Thread(target=self._scroll_mouse, daemon=True)    
        self._scroll_mouse_event = threading.Event()
        self._scroll_mouse_range = 0
        self._scroll_mouse_lock = threading.Lock()

    
    def _move_mouse(self):
        size = pyautogui.size()
        while True:
            if self._move_mouse_event.wait(20):
                with self._move_mouse_lock:
                    move_to = self._move_mouse_position
                    velocity = self._move_mouse_velocity if self._move_mouse_velocity > 0 else 30

                if pyautogui.position()[0] + move_to[0] in range(1, size[0]) and pyautogui.position()[1] + move_to[1] in range(1, size[1]):
                    pyautogui.moveRel(*move_to, duration = 1/velocity, _pause=False)

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
                pyautogui.click(button='left')
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