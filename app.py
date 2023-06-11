from flask import Flask
from flaskwebgui import FlaskUI

import routes


app = Flask(__name__)

app.add_url_rule('/', view_func=routes.index)
app.add_url_rule('/video_feed', view_func=routes.video_feed)
app.add_url_rule('/get_info', view_func=routes.get_info)
app.add_url_rule('/get_fps', view_func=routes.get_fps)
app.add_url_rule('/toggle_gesture/<int:gesture_id>', view_func=routes.toggle_gesture)
app.add_url_rule('/record_gesture/<gesture_name>/<gesture_type>', view_func=routes.record_gesture)

if __name__ == '__main__':
    # app.run()
    ui = FlaskUI(app=app, server='flask').run()
