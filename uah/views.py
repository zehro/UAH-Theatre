from flask import Flask, render_template, request, redirect, url_for, flash
from uah import app
from uah.db import *
from time import gmtime, strftime

# Invalid/Error 404 Route
# All invalid URLs will be redirected to the 404 page
@app.route('/<path:path>')
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

# Login Routes
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # TODO: check user login
    return redirect(url_for('home_page'))

# Register Routes
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # TODO: add new user
    return redirect(url_for('login_page'))

# Main App / Default Routes
@app.route('/')
def index_page(path=None):
    return redirect(url_for('login_page'))

@app.route("/logout")
def logout():
    # TODO: clear session
    return redirect(url_for('index_page'))

# "Home" Routes -> will move to index/default when sessions are implemented
@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')

@app.route('/home', methods=['POST'])
def home():
    # an example SQL query to demo remote db execution
    result = connection.execute("INSERT INTO AUDIT(ACTION, TIME, USER) VALUES (1, %s ,1)", (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    return redirect(url_for('login_page'))

# Search Routes
@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

# Add Item Routes
@app.route('/additem', methods=['GET'])
def additem_page():
    return render_template('additem.html')

@app.route('/additem', methods=['POST'])
def additem():
    return redirect(url_for('home'))
