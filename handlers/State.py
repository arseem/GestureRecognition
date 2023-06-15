from dataclasses import asdict
import json
import os

from handlers.Gesture import Gesture

class State:
    def __init__(self, global_config):
        self._states_path = global_config.states_path
        self.gestures = {}
        self.model_path = ''

        self.available_states = self.get_available_models()
        self.load(os.path.basename(max(self.available_states, key=os.path.getmtime))[:-5])

    
    def save(self, state_name):
        output =  {'gestures': [asdict(gesture) for gesture in list(self.gestures.values())], 'model_path': self.model_path}
        state_name = state_name[:-5] if state_name.endswith('.json') else state_name
        with open(f"{state_name}.json", 'w') as f:
            json.dump(output, f, indent=4)


    def load(self, state_name):
        state_name = os.path.basename(state_name)[:-5] if state_name.endswith('.json') else state_name
        with open(f"{self._states_path}/{state_name}.json") as f:
            state = json.load(f)

        temp_gestures ={g['name'] : Gesture(g['name'], g['action'], g['on'], float(g['detection_sensitivity']), float(g['tracking_sensitivity']), g['one_shot']) for g in state['gestures']}
        self.gestures.clear()
        self.gestures.update(temp_gestures)
        self.model_path = state['model_path']


    def get_available_models(self):
        return [os.path.join(self._states_path, f) for f in os.listdir(self._states_path) if os.path.isfile(os.path.join(self._states_path, f)) and f.endswith(".json")]