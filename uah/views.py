from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from uah import app
from uah.db import *
from uah.sessions import *
from uah.image_uploader import save_image, load_image

import sys
# Sets up variables/functions for use in Jinja templates
@app.context_processor
def inject_isAdmin_function():
    def isAdmin():
        if g.user:
            return g.user['isAdmin'] == TRUE
    return dict(isAdmin=isAdmin)

# Request to be executed before all requests
@app.before_request
def before_request():
    # Clears user from application context
    g.user = None
    # Checks if there's a user in a session
    if 'user' in session:
        with DatabaseConnection() as conn:
            # Executes SQL query
            result = conn.execute(User.findby_username, {
                'Username': session['user']
            })
            # Sets the user in the application context
            queryResult = result.fetchone()
            g.user = {'Username' : queryResult[0],
                      'isAdmin'  : queryResult[1]}

# Invalid/Error 404 Route
# All invalid URLs will be redirected to the 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

# Main App / Default Routes
@app.route('/')
def index_page(path=None):
    return redirect(url_for('home_page'))

# Logout Route
@app.route("/logout")
def logout():
    # Clear session
    session.clear()
    return redirect(url_for('login_page'))

# Login Route: HTML Template
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Login Route: POST method after form submission
@app.route('/login', methods=['POST'])
def login():
    # Checks if required fields exist in form
    if 'username' not in request.form or \
            'password' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return login_page()

    # Get field inputs
    username = request.form['username']
    password = request.form['password']

    # Checks if required fields are empty
    if username == '':
        flash(u'Username field cannot be empty.', 'danger')
        return login_page()
    if password == '':
        flash(u'Password field cannot be empty.', 'danger')
        return login_page()

    # Checks user/password combination
    with DatabaseConnection() as conn:
        # Checks if there are any valid user/password combination
        result = conn.execute(User.check_login, {
            'Username'   : username,
            'Password'   : password
        })
        queryResult = result.fetchall();
        if len(queryResult) != 1:
            flash(u'Invalid username or password.', 'danger')
            return login_page()
        # Sets the user in the application context
        g.user = {'Username' : queryResult[0],
                  'isAdmin'  : queryResult[1]}
        # Sets up a session with user from application context
        session['user'] = g.user['Username']
    # Navigates to the main page
    return redirect('/')

# Register Route: HTML Template
@app.route('/users/new', methods=['GET'])
def register_page():
    return render_template('register.html')

# Register Route: POST method after form submission
@app.route('/users', methods=['POST'])
def register():
    # Checks if required fields exist in form
    if 'username' not in request.form or \
            'password' not in request.form or \
            'confirmPassword' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return register_page()

    # Get field inputs
    firstName       = request.form['firstName']
    lastName        = request.form['lastName']
    username        = request.form['username']
    password        = request.form['password']
    confirmPassword = request.form['confirmPassword']

    # Checks if required fields are empty
    if firstName == '' or lastName == '':
        flash(u'Name fields cannot be empty.', 'danger')
        return register_page()
    if username == '':
        flash(u'Username field cannot be empty.', 'danger')
        return register_page()
    if password == '':
        flash(u'Password field cannot be empty.', 'danger')
        return register_page()
    if confirmPassword == '':
        flash(u'Confirm Password field cannot be empty.', 'danger')
        return register_page()

    # Checks confirmation fields
    if password != confirmPassword:
        flash(u'Passwords did not match.', 'danger')
        return register_page()

    # Checks user/password combination
    with DatabaseConnection() as conn:
        # Begins a transaction
        transaction = conn.begin()
        try:
            # Checks if the username is used
            result = conn.execute(User.findby_username, {
                'Username': username
            })
            if len(result.fetchall()) > 0:
                flash(u'Username is already used.', 'danger')
                return register_page()
            # Registers the new user
            conn.execute(User.insert, {
                'Username' : username,
                'Password' : password
            })
            # Commits the transaction changes
            transaction.commit()
        except:
            # Rollback and discard transaction changes upon failure
            transaction.rollback()
            raise
    return redirect(url_for('login_page'))

# Homepage Route: HTML Template
@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')

# Homepage Route: POST method after form submission
@app.route('/home', methods=['POST'])
def home():
    # an example SQL query to demo remote db execution
    result = connection.execute("INSERT INTO AUDIT(ACTION, TIME, USER) VALUES (1, %s ,1)", (strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    return redirect(url_for('login_page'))

# Search Route: HTML Template
@app.route('/items', methods=['GET'])
def search_page():
    with DatabaseConnection() as conn:
        # Gets the color filters
        conditionResult = conn.execute(Item.get_condition_filters)
        conditionQuery = conditionResult.fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[0])

        # Gets the color filters
        colorResult = conn.execute(Item.get_color_filters)
        colorQuery = colorResult.fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[0])

        # Gets the color filters
        eraResult = conn.execute(Item.get_era_filters)
        eraQuery = eraResult.fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[0])

        items = conn.execute("SELECT * FROM OBJECT").fetchall()

    return render_template('search.html', conditions=conditionList, colors=colorList, eras=eraList, items=items)
# Search Route: POST method after form submission
@app.route('/items', methods=['POST'])
def search():
    # Checks if required fields exist in form
    if 'itemName' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return search_page()

    # Get search bar input
    itemName = request.form['itemName']
    # get filter inputs

    with DatabaseConnection() as conn:
        if len(itemName):
            items = conn.execute("SELECT * FROM OBJECT WHERE OBJECTNAME = %s", itemName).fetchall()
            # display results on page
            return render_template('search.html', items=items)
        else:
            return search_page()

# Add Item Route: HTML Template
@app.route('/items/new', methods=['GET'])
def additem_page():
    return render_template('additem.html')

# Add Item Route: POST method after form submission
@app.route('/items/new', methods=['POST'])
def additem():
    if request.files:
        image = request.files['image']
        imageName = save_image(image)
        return search_page()
    else:
        return redirect(url_for('home_page'))
