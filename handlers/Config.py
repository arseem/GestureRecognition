from dataclasses import dataclass

@dataclass
class Config:


    # --- Paths ---------------------------------------------------------------------------------------------------------

    datasets_path: str = './data/'
    models_path: str = './models/'
    states_path: str = './states/'
    default_model = None


    #  --- Data capturing settings --------------------------------------------------------------------------------------

    dataset_name = 'data_{timestamp}'

    num_frames = 15
    num_takes = 10


    #  --- Detection settings -------------------------------------------------------------------------------------------

    #Gestures
    gestures_on = None
    gestures_action = None

    # Hands detection
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5

    # Gesture detection
    track_confidence_threshold: float = 0.3
    change_confidence_threshold: float = 0.6


    #  --- Training settings --------------------------------------------------------------------------------------------

    # Transfer learning
    freeze_weights: bool = False
    epochs: int = 100


    #  --- pyautogui settings --------------------------------------------------------------------------------------------

    specific_actions_dropdown = [
        { 'value': 'none', 'text': 'None' },
        { 'value': 'RECORDNEW', 'text': 'Record Custom Keys' },
        { 'value': 'volumeup', 'text': '(Volume) Up' },
        { 'value': 'volumedown', 'text': '(Volume) Down' },
        { 'value': 'volumemute', 'text': '(Volume) Mute' },
        { 'value': 'browserback', 'text': '(Browser) Back' },
        { 'value': 'browserforward', 'text': '(Browser) Forward' },
        { 'value': 'browserrefresh', 'text': '(Browser) Refresh' },
        { 'value': 'playpause', 'text': '(Media) Play/Pause' },
        { 'value': 'nexttrack', 'text': '(Media) Next Track' },
        { 'value': 'prevtrack', 'text': '(Media) Prev Track' },
        { 'value': 'MOVE', 'text': '(Mouse) Move Cursor' },
        { 'value': 'LEFT', 'text': '(Mouse) Left Click' },
        { 'value': 'RIGHT', 'text': '(Mouse) Right Click' },
        { 'value': 'DRAG', 'text': '(Mouse) Drag (Hold left + move)' },
        { 'value': 'SCROLL', 'text': '(Mouse) Scroll' },
    ]

    specific_actions = {action['value']: action['text'] for action in specific_actions_dropdown}

    possible_keys = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
                    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
                    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
                    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
                    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
                    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
                    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
                    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
                    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
                    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
                    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
                    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
                    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
                    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
                    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
                    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
                    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
                    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
                    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
                    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
                    'command', 'option', 'optionleft', 'optionright']
    
    javascript_keys = {
    'Tab': '\t',
    'Enter': '\n',
    'Space': ' ',
    'Digit1': '!',
    'Quote': '"',
    'Digit3': '#',
    'Digit4': '$',
    'Digit5': '%',
    'Digit7': '&',
    'Digit9': '(',
    'Digit0': ')',
    'Digit8': '*',
    'Equal': '+',
    'Comma': ',',
    'Minus': '-',
    'Period': '.',
    'Slash': '/',
    'Semicolon': ';',
    'BracketLeft': '[',
    'Backslash': '\\',
    'BracketRight': ']',
    'Backquote': '`',
    'KeyA': 'a',
    'KeyB': 'b',
    'KeyC': 'c',
    'KeyD': 'd',
    'KeyE': 'e',
    'KeyF': 'f',
    'KeyG': 'g',
    'KeyH': 'h',
    'KeyI': 'i',
    'KeyJ': 'j',
    'KeyK': 'k',
    'KeyL': 'l',
    'KeyM': 'm',
    'KeyN': 'n',
    'KeyO': 'o',
    'KeyP': 'p',
    'KeyQ': 'q',
    'KeyR': 'r',
    'KeyS': 's',
    'KeyT': 't',
    'KeyU': 'u',
    'KeyV': 'v',
    'KeyW': 'w',
    'KeyX': 'x',
    'KeyY': 'y',
    'KeyZ': 'z',
    'Accept': 'accept',
    'NumpadAdd': 'add',
    'AltLeft': 'alt',
    'AltRight': 'altright',
    'Backspace': 'backspace',
    'CapsLock': 'capslock',
    'Clear': 'clear',
    'ControlLeft': 'ctrl',
    'ControlRight': 'ctrlright',
    'Delete': 'del',
    'NumpadDivide': 'divide',
    'ArrowDown': 'down',
    'End': 'end',
    'Escape': 'esc',
    'Execute': 'execute',
    'F1': 'f1',
    'F10': 'f10',
    'F11': 'f11',
    'F12': 'f12',
    'F13': 'f13',
    'F14': 'f14',
    'F15': 'f15',
    'F16': 'f16',
    'F17': 'f17',
    'F18': 'f18',
    'F19': 'f19',
    'F2': 'f2',
    'F20': 'f20',
    'F21': 'f21',
    'F22': 'f22',
    'F23': 'f23',
    'F24': 'f24',
    'F3': 'f3',
    'F4': 'f4',
    'F5': 'f5',
    'F6': 'f6',
    'F7': 'f7',
    'F8': 'f8',
    'F9': 'f9',
    'Home': 'home',
    'Insert': 'insert',
    'Multiply': 'multiply',
    'Numpad0': 'num0',
    'Numpad1': 'num1',
    'Numpad2': 'num2',
    'Numpad3': 'num3',
    'Numpad4': 'num4',
    'Numpad5': 'num5',
    'Numpad6': 'num6',
    'Numpad7': 'num7',
    'Numpad8': 'num8',
    'Numpad9': 'num9',
    'PageDown': 'pagedown',
    'PageUp': 'pageup',
    'Pause': 'pause',
    'PrintScreen': 'printscreen',
    'ScrollLock': 'scrolllock',
    'Select': 'select',
    'Separator': 'separator',
    'ShiftLeft': 'shift',
    'ShiftRight': 'shiftright',
    'NumpadSubtract': 'subtract',
    'Tab': 'tab',
    'ArrowUp': 'up',
    'VolumeDown': 'volumedown',
    'VolumeMute': 'volumemute',
    'VolumeUp': 'volumeup',
    'MetaLeft': 'win',
    'MetaRight': 'winright'
    }
