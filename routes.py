import cv2

from flask import render_template, make_response, request, jsonify

from handlers.Config import Config
from handlers.ModelLoader import ModelLoader
from handlers.VideoProcessor import VideoProcessor


GLOBAL_CONFIG = Config()
MODEL_LOADER = ModelLoader(GLOBAL_CONFIG.default_model)
VIDEO_PROCESSOR = VideoProcessor(MODEL_LOADER, GLOBAL_CONFIG)

gesture_list = MODEL_LOADER.get_model_info()['gestures']
gesture_on = GLOBAL_CONFIG.gestures_on if GLOBAL_CONFIG.gestures_on else [True for _ in gesture_list]


def index():
    return render_template('index.html', gesture_list=gesture_list, gesture_on=gesture_on, len_gesture_list=len(gesture_list))


async def video_feed():
    cap = cv2.VideoCapture(0)        

    # Create a response with the generator function as content
    if (request.args.get('height') and request.args.get('width')):
        print(str(request.args.get('width')) + "  " + str(request.args.get('height')))
        response = make_response(VIDEO_PROCESSOR.process_feed(cap, height=int(request.args.get('height')), width=int(request.args.get('width'))))

    else:
        response = make_response(VIDEO_PROCESSOR.process_feed(cap))

    # Add Cache-Control header to prevent caching
    response.headers['Content-Type'] = 'multipart/x-mixed-replace; boundary=frame'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


async def get_info():
    return jsonify({
        'gestures': gesture_list,
        'current_scores': [str(round(x, 2)) for x in VIDEO_PROCESSOR.current_scores],
        'current_prediction': VIDEO_PROCESSOR.current_prediction
    })


async def get_fps():
    return jsonify({
        'fps': int(VIDEO_PROCESSOR.fps)
    })


def toggle_gesture(gesture_id):
    gesture_on[gesture_id] = not gesture_on[gesture_id]
    return str(gesture_on[gesture_id])


def record_gesture(gesture_name, gesture_type):
    # Record the gesture here...
    print("Recording gesture: " + gesture_name + " of type: " + gesture_type)
    return "Recording gesture: " + gesture_name + " of type: " + gesture_type
