from flask import Flask, render_template, request, redirect, url_for
from uah import app

# Invalid/Error 404 Route
# All invalid URLs will be redirected to the 404 page
@app.route('/<path:path>')
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

@app.route("/logout")
def logout():
    return redirect(url_for('index_page'))

# Default app page route
@app.route('/')
def index_page(path=None):
    # to be implemented: check auth, if user is authenticated, render home page. Otherwise, render login page.
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # auth; to be implemented using flask-login
    return redirect(url_for('home_page'))

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # add new user; to be implemented
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')
