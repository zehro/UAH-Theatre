import os
from flask import send_from_directory
from werkzeug.utils import secure_filename
from uah import app

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/images/inventory')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_image(image):
    # filename = secure_filename(image.filename)
    filename = 'uploaded.jpeg'
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename

@app.route('/static/images/inventory/<filename>')
def load_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
