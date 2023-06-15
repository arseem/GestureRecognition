from flask import Flask
from flaskwebgui import FlaskUI
import webview

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import routes


app = Flask(__name__)
# window = webview.create_window('Gesture Recognition', app)

app.add_url_rule('/', view_func=routes.index)
app.add_url_rule('/video_feed', view_func=routes.video_feed)
app.add_url_rule('/get_info', view_func=routes.get_info)
app.add_url_rule('/get_fps', view_func=routes.get_fps)
app.add_url_rule('/get_dropdown_options/<gesture_name>', view_func=routes.get_dropdown_options)
app.add_url_rule('/toggle_gesture/<gesture_name>', view_func=routes.toggle_gesture)
app.add_url_rule('/record_gesture/<gesture_name>/<gesture_type>', view_func=routes.record_gesture)
app.add_url_rule('/apply_changes/<gesture_name>/<action>/<detection_sensitivity>/<tracking_sensitivity>/<mode>', view_func=routes.apply_changes)
app.add_url_rule('/toggle_overlay', view_func=routes.toggle_overlay)
app.add_url_rule('/update_overlay_size/<size>', view_func=routes.update_overlay_size)
app.add_url_rule('/update_overlay_opacity/<opacity>', view_func=routes.update_overlay_opacity)
app.add_url_rule('/toggle_recognition', view_func=routes.toggle_recognition)
app.add_url_rule('/load_state', view_func=routes.load_state)
app.add_url_rule('/save_state', view_func=routes.save_state)
app.add_url_rule('/start_recording/<gesture_name>', view_func=routes.start_recording)
app.add_url_rule('/stop_recording/', view_func=routes.stop_recording)
app.add_url_rule('/is_recording_done/', view_func=routes.is_recording_done)

if __name__ == '__main__':
    # app.run()
    ui = FlaskUI(app=app, server='flask').run()
    # webview.start()
