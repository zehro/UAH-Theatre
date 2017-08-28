from flask import render_template, Response, json, jsonify
from uah import app

@app.route('/')
@app.route('/<path:path>')
def index(path=None):
    return render_template('index.html')
