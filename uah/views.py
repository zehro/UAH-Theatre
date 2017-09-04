from flask import Flask, render_template, request, redirect, url_for
from uah import app

@app.route('/')
@app.route('/<path:path>') # all invalid urls will be redirected to index page
def index_page(path=None):
    # to be implemented: check auth, if user is authenticated, render home page. Otherwise, render login page.
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # auth; to be implemented using flask-login
        return redirect(url_for('home_page'))

@app.route("/logout")
def logout():
    return redirect(url_for('index_page'))

@app.route('/user/new', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/users', methods=['POST'])
def register():
    # add new user; to be implemented
    return redirect(url_for('login'))

@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')


@app.route('/additem', methods=['GET'])
def additem_page():
    return render_template('additem.html')
