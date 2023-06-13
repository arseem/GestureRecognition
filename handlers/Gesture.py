from dataclasses import dataclass


@dataclass
class Gesture:
    name: str
    action: str = 'none'
    on: bool = True
    detection_sensitivity: float = 0.5
