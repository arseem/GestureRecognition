from dataclasses import dataclass

@dataclass
class Config:


    # --- Paths ---------------------------------------------------------------------------------------------------------

    datasets_path: str = './data/'
    models_path: str = './models/'
    default_model = None


    #  --- Data capturing settings --------------------------------------------------------------------------------------

    dataset_name = 'data_{timestamp}'


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