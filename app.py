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
app.add_url_rule('/apply_changes/<gesture_name>/<action>/<detection_sensitivity>', view_func=routes.apply_changes)

if __name__ == '__main__':
    # app.run()
    ui = FlaskUI(app=app, server='flask').run()
    # webview.start()
