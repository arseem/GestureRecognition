import cv2
import mediapipe as mp

import numpy as np
import time

from flask import Flask, render_template, Response, make_response, request, current_app
from flaskwebgui import FlaskUI


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', gesture_list=gesture_list, gesture_on=gesture_on, len_gesture_list=len(gesture_list))


@app.route('/video_feed')
async def video_feed():
    cap = cv2.VideoCapture(0)        

    # Create a response with the generator function as content
    if (request.args.get('height') and request.args.get('width')):
        print(str(request.args.get('width')) + "  " + str(request.args.get('height')))
        response = make_response(generate_frames(cap, height=int(request.args.get('height')), width=int(request.args.get('width'))))

    else:
        response = make_response(generate_frames(cap))

    # Add Cache-Control header to prevent caching
    response.headers['Content-Type'] = 'multipart/x-mixed-replace; boundary=frame'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.route('/toggle_gesture/<int:gesture_id>')
def toggle_gesture(gesture_id):
    gesture_on[gesture_id] = not gesture_on[gesture_id]
    return str(gesture_on[gesture_id])


@app.route('/record_gesture/<gesture_name>/<gesture_type>')
def record_gesture(gesture_name, gesture_type):
    # Record the gesture here...
    print("Recording gesture: " + gesture_name + " of type: " + gesture_type)
    return "Recording gesture: " + gesture_name + " of type: " + gesture_type


if __name__ == '__main__':
    gesture_list = ["Gesture 1", "Gesture 2", "Gesture 3", "Gesture 4", "Gesture 5", "Gesture 6", "Gesture 7", "Gesture 8", "Gesture 9", "Gesture 10", "Gesture 11", "Gesture 12", "Gesture 13"]
    gesture_on = [False] * len(gesture_list)

    # app.run()
    ui = FlaskUI(app=app, server='flask').run()
