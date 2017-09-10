from flask import Flask, render_template, request, redirect, url_for
from uah import app
from uah.db import *
from time import gmtime, strftime

# Invalid/Error 404 Route
# All invalid URLs will be redirected to the 404 page
@app.route('/<path:path>')
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

# Login
>>>>>>> origin/master
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # auth; to be implemented using flask-login
    return redirect(url_for('home_page'))

# Register
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # add new user; to be implemented
    return redirect(url_for('login_page'))

# Main App / Default Routes
@app.route('/')
def index_page(path=None):
    # to be implemented: check auth, if user is authenticated, render home page. Otherwise, render login page.
    return redirect(url_for('login_page'))

@app.route("/logout")
def logout():
    return redirect(url_for('index_page'))

@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')

@app.route('/home', methods=['POST'])
def home():
    # an example SQL query to demo remote db execution
    result = connection.execute("INSERT INTO AUDIT(ACTION, TIME, USER) VALUES (1, %s ,1)", (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    return redirect(url_for('login_page'))

# Search
@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

# Add Item
@app.route('/additem', methods=['GET'])
def additem_page():
    return render_template('additem.html')

@app.route('/additem', methods=['POST'])
def additem():
    return redirect(url_for('home'))
