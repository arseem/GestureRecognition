import os
import json

import tensorflow as tf


class ModelLoader:

    def __init__(self, model_path=None):
        self._path_to_models = './models'
        self._model_folders = [os.path.join(self._path_to_models, d) for d in os.listdir(self._path_to_models) if os.path.isdir(os.path.join(self._path_to_models, d))]
        if not model_path:
            # Get the latest models
            path_model = max(self._model_folders, key=os.path.getmtime)
        else:
            path_model = '/'.join(model_path.split('/')[:-2])
        
        self.available_model_folders = [os.path.basename(d) for d in self._model_folders]
        self.model_folder_name = os.path.basename(path_model)

        available_models = [f for f in os.listdir(f"{path_model}/models") if os.path.isfile(os.path.join(f"{path_model}/models", f)) and f.endswith(".tflite")]
        self._model_name = available_models[0]
        self._model_path = os.path.join(path_model, "models", self._model_name)

        with open(os.path.join(path_model, "info.json")) as f:
            self._model_info = json.load(f)

        self._load_model()

    def _load_model(self):
        self.model = tf.lite.Interpreter(model_path=self._model_path)
        self.model.allocate_tensors()

    def switch_model(self, model_name):
        self.model_name = model_name
        self.model_path = os.path.join(self._path_to_models, self.model_name)
        self._load_model()

    def get_model_info(self):
        return self._model_info
    
    def get_available_models(self):
        return self.available_model_folders
    
    def get_current_model(self):
        return self.model