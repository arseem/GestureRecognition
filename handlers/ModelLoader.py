import os
import json

import tensorflow as tf


class ModelLoader:

    def __init__(self, model_path):
        self._path_to_models = './models'
        self._model_path = model_path
        self._model_folder_path = os.path.join(os.path.split(os.path.split(self._model_path)[0])[0])
        
        self._load_model()

    def _load_model(self):
        with open(os.path.join(self._model_folder_path, "info.json")) as f:
            self._model_info = json.load(f)
        self.model = tf.lite.Interpreter(model_path=self._model_path)
        self.model.allocate_tensors()

    def switch_model(self, model_path):
        self._model_path = model_path
        self._model_folder_path = os.path.join(os.path.split(os.path.split(self._model_path)[0])[0])
        self._load_model()

    def get_model_info(self):
        return self._model_info
    
    def get_available_models(self):
        return self.available_model_folders
    
    def get_current_model(self):
        return self.model