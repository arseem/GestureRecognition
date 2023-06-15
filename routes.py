import cv2
import os
import threading

import tkinter as tk
from tkinter import filedialog

from flask import render_template, make_response, request, jsonify

from handlers.Config import Config
from handlers.ModelLoader import ModelLoader
from handlers.VideoProcessor import VideoProcessor
from handlers.ActionHandler import ActionHandler
from handlers.Overlay import Overlay
from handlers.State import State
from handlers.RecordHandler import RecordHandler
from handlers.Gesture import Gesture
from handlers.TrainingHandler import TrainingHandler


GLOBAL_CONFIG = Config()
CURRENT_STATE = State(GLOBAL_CONFIG)
RECORD_HANDLER = RecordHandler(GLOBAL_CONFIG)
MODEL_LOADER = ModelLoader(CURRENT_STATE.model_path)
VIDEO_PROCESSOR = VideoProcessor(MODEL_LOADER, GLOBAL_CONFIG, CURRENT_STATE, RECORD_HANDLER)
ACTION_HANDLER = ActionHandler(VIDEO_PROCESSOR, GLOBAL_CONFIG.javascript_keys)
OVERLAY = Overlay(VIDEO_PROCESSOR)
TRAINING_HANDLER = TrainingHandler(GLOBAL_CONFIG, CURRENT_STATE, MODEL_LOADER)


def index():
    return render_template('index.html', gesture_list=list(CURRENT_STATE.gestures.keys()), gesture_on=[gesture.on for gesture in list(CURRENT_STATE.gestures.values())], len_gesture_list=len(list(CURRENT_STATE.gestures.keys())))


async def video_feed():
    cap = cv2.VideoCapture(0)

    # Create a response with the generator function as content
    if not RECORD_HANDLER.recording:
        if (request.args.get('height') and request.args.get('width')):
            print(str(request.args.get('width')) + "  " + str(request.args.get('height')))
            response = make_response(VIDEO_PROCESSOR.process_feed(cap, height=int(request.args.get('height')), width=int(request.args.get('width'))))

        else:
            response = make_response(VIDEO_PROCESSOR.process_feed(cap))
    
    else:
        if (request.args.get('height') and request.args.get('width')):
            print(str(request.args.get('width')) + "  " + str(request.args.get('height')))
            response = make_response(RECORD_HANDLER.record(cap, height=int(request.args.get('height')), width=int(request.args.get('width'))))

        else:
            response = make_response(RECORD_HANDLER.record(cap))

    # Add Cache-Control header to prevent caching
    response.headers['Content-Type'] = 'multipart/x-mixed-replace; boundary=frame'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


async def get_info():
    (current_predicted_gesture, current_score) = VIDEO_PROCESSOR.get_current_prediction()
    needs_training = set(CURRENT_STATE.gestures.keys()) != set(MODEL_LOADER._model_info['gestures'])
    try:
        return jsonify({
            'gestures': list(CURRENT_STATE.gestures.keys()),
            'current_scores': [str(round(x, 2)) for x in VIDEO_PROCESSOR.current_scores],
            'current_prediction': None if not current_predicted_gesture or not current_predicted_gesture.on else f'{current_predicted_gesture.name} ({round(current_score*100)/100})',
            'needs_training': needs_training
        })
    except TypeError:
        return jsonify({
            'gestures': list(CURRENT_STATE.gestures.keys()),
            'current_scores': [str(round(x, 2)) for x in VIDEO_PROCESSOR.current_scores],
            'current_prediction': None if not current_predicted_gesture or not current_predicted_gesture.on else f'{current_predicted_gesture.name}',
            'needs_training': needs_training
        })
    

async def get_fps():
    return jsonify({
        'fps': int(VIDEO_PROCESSOR.fps)
    })


async def toggle_overlay():
    OVERLAY.toggle()
    return jsonify({'success': True})


async def update_overlay_size(size):
    OVERLAY.scale = float(size)
    return jsonify({'success': True})


async def update_overlay_opacity(opacity):
    OVERLAY.opacity = float(opacity)
    return jsonify({'success': True})


async def toggle_recognition():
    VIDEO_PROCESSOR.toggle_recognition()
    return jsonify({'success': True})
    

async def get_dropdown_options(gesture_name):
    current_action = 'CUSTOM'
    for gesture in GLOBAL_CONFIG.specific_actions_dropdown:
        if gesture['value'] == CURRENT_STATE.gestures[gesture_name].action:
            current_action = gesture['text']
            break
            

    current_action = {'value':CURRENT_STATE.gestures[gesture_name].action, 'text':str(current_action)}
    dropdown = [current_action] + GLOBAL_CONFIG.specific_actions_dropdown if current_action['text'] not in GLOBAL_CONFIG.specific_actions.keys() else GLOBAL_CONFIG.specific_actions_dropdown
    gesture_type = CURRENT_STATE.gestures[gesture_name].one_shot
    return jsonify(gesture_type, dropdown, CURRENT_STATE.gestures[gesture_name].detection_sensitivity, CURRENT_STATE.gestures[gesture_name].tracking_sensitivity)


async def apply_changes(gesture_name, action, detection_sensitivity, tracking_sensitivity, mode):
    CURRENT_STATE.gestures[gesture_name].action = action
    CURRENT_STATE.gestures[gesture_name].detection_sensitivity = float(detection_sensitivity)
    CURRENT_STATE.gestures[gesture_name].tracking_sensitivity = float(tracking_sensitivity)
    CURRENT_STATE.gestures[gesture_name].one_shot = bool(int(mode))
    return jsonify({'success': True})


async def toggle_gesture(gesture_name):
    if gesture_name in MODEL_LOADER._model_info['gestures']:
        CURRENT_STATE.gestures[gesture_name].on = not CURRENT_STATE.gestures[gesture_name].on
        return jsonify({'success': True})

    else:
        return jsonify({'success': False})


async def load_state():
    root = tk.Tk()
    root.withdraw()

    state_name = filedialog.askopenfilename(initialdir=GLOBAL_CONFIG.states_path, title="Select state file", filetypes=[("State files", "*.json")])
    try:
        CURRENT_STATE.load(state_name)
        return jsonify({'success': True})
    
    except FileNotFoundError:
        return jsonify({'success': False})


async def save_state():
    root = tk.Tk()
    root.withdraw()

    state_name = filedialog.asksaveasfilename(initialdir=GLOBAL_CONFIG.states_path, title="Select state file", filetypes=[("State files", "*.json")])
    CURRENT_STATE.save(state_name)
    return jsonify({'success': True})


async def start_recording(gesture_name):
    if gesture_name in CURRENT_STATE.gestures.keys():
        return jsonify({'status': 403, 'message': 'Gesture already exists'})
    else:
        RECORD_HANDLER.start_recording(gesture_name)
        return jsonify({'status': 200, 'message': 'Recording started'})
    

async def stop_recording():
    CURRENT_STATE.gestures[RECORD_HANDLER._gesture_name] = Gesture(RECORD_HANDLER._gesture_name, on=False)
    return jsonify({'status': 200, 'message': 'Recording stopped'})


async def is_recording_done():
    if not RECORD_HANDLER.recording:
        return jsonify({'status': 200, 'message': 'Recording done'})
    else:
        return jsonify({'status': 403, 'message': 'Recording in progress'})
    

async def start_training():
    training_thread = threading.Thread(target=TRAINING_HANDLER.train, daemon=True)
    training_thread.start()
    return jsonify({'success': True})


async def is_training_done():
    if not TRAINING_HANDLER.training:
        return jsonify({'status': 200, 'message': 'Recording done'})
    else:
        return jsonify({'status': 403, 'message': 'Recording in progress'})


async def finish_training():
    MODEL_LOADER.switch_model(CURRENT_STATE.model_path)
    VIDEO_PROCESSOR._get_info_from_state(CURRENT_STATE)
    VIDEO_PROCESSOR._get_model_from_loader(MODEL_LOADER)
    return jsonify({'success': True})