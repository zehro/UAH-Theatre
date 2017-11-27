from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from uah import app
from uah.db import *
from uah.image_uploader import *
from uah.sessions import *
import sys

# Sets up variables/functions for use in Jinja templates
@app.context_processor
def inject_isAdmin_function():
    def isAdmin():
        if g.user:
            return g.user['isAdmin']
    return dict(isAdmin=isAdmin)

@app.context_processor
def inject_convertTypeToString_function():
    def convertTypeToString(enum):
        if enum == 'c':
            return 'Costume'
        if enum == 'p':
            return 'Prop'
        return enum
    return dict(convertTypeToString=convertTypeToString)

@app.context_processor
def inject_fileExists_function():
    def fileExists(filename):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return os.path.exists(path)
    return dict(fileExists=fileExists)

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
                'USERNAME': session['user']
            })
            # Sets the user in the application context
            queryResult = result.fetchone()
            if (queryResult != None):
                g.user = {'UID'        : queryResult[0],
                          'Username'   : queryResult[1],
                          'isAdmin'    : queryResult[2],
                          'isVerified' : queryResult[3]}

# Invalid/Error 404 Route
# All invalid URLs will be redirected to the 404 page
@app.route('/<path:path>')
@app.errorhandler(404)
def page_not_found(path):
    return redirect(url_for('error_page'))

@app.route('/error')
def error_page():
    return render_template('error.html')

# Main App / Default Routes
@app.route('/')
def home_page(path=None):
    return redirect(url_for('search_page'))

# Logout Route
@app.route("/logout")
def logout():
    # Clear session
    session.clear()
    # Clear user from application context
    g.user = None

    return redirect(url_for('login_page'))

# Login Route: HTML Template
@app.route('/login', methods=['GET'])
def login_page():
    # If user manually navigates away from app, automatically logout
    if g.user != None:
        session.clear()

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
            'USERNAME' : username,
            'PASSWORD' : password,
        })
        queryResult = result.fetchall();
        if len(queryResult) != 1:
            flash(u'Invalid username or password.', 'danger')
            return login_page()
        # Sets the user in the application context
        g.user = {'UID'        : queryResult[0][0],
                  'Username'   : queryResult[0][1],
                  'isAdmin'    : queryResult[0][2],
                  'isVerified' : queryResult[0][3]}
        # Sets up a session with user from application context
        session['user'] = g.user['Username']
    # Navigates to the main page
    return redirect('/')

# Register Route: HTML Template
@app.route('/register', methods=['GET'])
def register_page():
    # If user manually navigates away from app, automatically logout
    if g.user != None:
        session.clear()

    return render_template('register.html')

# Register Route: POST method after form submission
@app.route('/register', methods=['POST'])
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
                'USERNAME'  : username,
                'PASSWORD'  : password,
                'FIRSTNAME' : firstName,
                'LASTNAME'  : lastName,
            })
            # Commits the transaction changes
            transaction.commit()
            flash(u'Successfully registered.', 'success')
        except:
            # Rollback and discard transaction changes upon failure
            transaction.rollback()
            flash(u'A registration error occurred.', 'danger')
            raise

    return redirect(url_for('login_page'))

# Search Route: HTML Template
@app.route('/search', methods=['GET'])
@login_required()
def search_page():
    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Condition.find_all).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Era.find_all).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Color.find_all).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Gets the search results
        searchResults = conn.execute(Item.find_all).fetchall()

    return render_template('search.html',
                            conditions = conditionList,
                            colors     = colorList,
                            eras       = eraList,
                            items      = searchResults)

# Search Route: POST method after form submission
@app.route('/search', methods=['POST'])
@login_required()
def search():
    # Checks if required fields exist in form
    if 'itemName' not in request.form or \
            'itemCategory' not in request.form or \
            'itemCondition' not in request.form or \
            'itemColor' not in request.form or \
            'itemEra' not in request.form or \
            'itemChecked' not in request.form or \
            'itemSize' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return search_page()

    # Get search bar input
    itemName = request.form['itemName'].capitalize()

    # get filter inputs
    itemCategory  = request.form['itemCategory'].capitalize()
    itemCondition = request.form['itemCondition'].capitalize()
    itemColor     = request.form['itemColor'].capitalize()
    itemEra       = request.form['itemEra'].capitalize()
    itemChecked   = request.form['itemChecked']
    itemSize      = request.form['itemSize'].capitalize()

    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Condition.find_all).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Era.find_all).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Color.find_all).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Get the search query
        searchQuery = buildSearch(itemName, convertCategory(itemCategory),
                                  itemCondition, itemColor, itemEra,
                                  convertChecked(itemChecked), itemSize)

        # Gets the search results
        searchResults = conn.execute(searchQuery).fetchall()

        return render_template('search.html',
                                conditions        = conditionList,
                                colors            = colorList,
                                eras              = eraList,
                                items             = searchResults,
                                itemName          = itemName,
                                itemSize          = itemSize,
                                selectedCategory  = itemCategory,
                                selectedCondition = itemCondition,
                                selectedColor     = itemColor,
                                selectedEra       = itemEra,
                                selectedChecked   = itemChecked)

# View Item Route: HTML Template
@app.route('/items/id/<int:oid>', methods=['GET'])
@login_required()
def item_page(oid):
    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Condition.find_all).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Era.find_all).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Color.find_all).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Get the item
        item = conn.execute(Item.findby_oid, {
            'OID' : oid,
        }).fetchone()

        # Get the item's images
        images = conn.execute(Item.get_images, {
            'OID' : oid,
        }).fetchall()

        # Get the item's colors
        colors = conn.execute(Item.get_colors, {
            'OID' : oid,
        }).fetchall()

        # Get the item's borrower, if it has one
        checkedTo = conn.execute(Item.get_borrower, {
            'OID' : oid,
        }).fetchone()
        if checkedTo:
            checkedTo = checkedTo[0]

    # Parse and format the item's colors
    itemColorArray = []
    for color in range(len(colors)):
        itemColorArray.append(colors[color][0])

    # Get a string of all the item's colors
    itemColors = ''
    if len(itemColorArray) == 0:
        itemColors = 'None'
    else:
        for color in range(len(itemColorArray)):
            itemColors += itemColorArray[color]
            if color < len(itemColorArray) - 1:
                itemColors += ', '

    return render_template('item.html',
                            currentUser    = g.user,
                            borrower       = checkedTo,
                            item           = item,
                            images         = images,
                            itemColors     = itemColors,
                            itemColorArray = itemColorArray,
                            conditions     = conditionList,
                            colors         = colorList,
                            eras           = eraList)

# View Item Route: HTML Template
@app.route('/items/id/<int:oid>', methods=['POST'])
@login_required()
def item_update(oid):
    # Checks if required fields exist in form
    if 'itemName' not in request.form or \
            'itemDescription' not in request.form or \
            'itemCategory' not in request.form or \
            'itemCondition' not in request.form or \
            'itemEra' not in request.form or \
            'itemColors' not in request.form or \
            'itemSize' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return item_page(oid)

    # Get search bar input
    itemName = request.form['itemName'].capitalize()

    # get detail inputs
    itemDescription = request.form['itemDescription'].capitalize()
    itemCategory    = request.form['itemCategory']
    itemCondition   = request.form['itemCondition']
    itemEra         = request.form['itemEra']
    itemColors      = request.form['itemColors']
    itemSize        = request.form['itemSize'].capitalize()

    with DatabaseConnection() as conn:
        # Begins a transaction
        transaction = conn.begin()
        try:
            # If updating
            if request.form['submit'] == 'Confirm':
                # Checks if required fields are empty
                if itemName == '':
                    flash(u'Name field cannot be empty.', 'danger')
                    return redirect(url_for('item_page', oid=oid))
                if itemCategory == '':
                    flash(u'Please select a category.', 'danger')
                    return redirect(url_for('item_page', oid=oid))
                if itemCondition == '':
                    flash(u'Please select a condition.', 'danger')
                    return redirect(url_for('item_page', oid=oid))

                # Parse the inputs
                if itemDescription == '':
                    itemDescription = None

                if itemSize == '':
                    itemSize = None

                eid = conn.execute(Era.find_by_name, {
                    'ERANAME' : itemEra.capitalize(),
                }).fetchone()
                if eid:
                    eid = eid[0]

                colorNames = itemColors.split(',')
                colorIDs = []
                for colorName in colorNames:
                    colorID = conn.execute(Color.find_by_name, {
                        'COLORNAME' : colorName.capitalize(),
                    }).fetchone()
                    if colorID:
                        colorIDs.append(colorID[0])

                cnid = conn.execute(Condition.find_by_name, {
                    'CNDTNNAME' : itemCondition.capitalize(),
                }).fetchone()
                if cnid:
                    cnid = cnid[0]

                # Updates the item
                conn.execute(Item.update, {
                    'OID'         : oid,
                    'OBJECTNAME'  : itemName,
                    'DESCRIPTION' : itemDescription,
                    'TYPE'        : convertCategory(itemCategory),
                    'SIZE'        : itemSize.capitalize(),
                    'CNID'        : cnid,
                    'EID'         : eid,
                })
                # Clears current colors then adds the new updated values
                conn.execute(Item.delete_colors, {
                    'OID' : oid,
                })
                for cid in colorIDs:
                    conn.execute(Item.insert_into_color, {
                        'OID' : oid,
                        'CID' : cid,
                    })

                # Commits the transaction changes
                transaction.commit()

                flash(u'Item updated.', 'success')
                return redirect(url_for('item_page', oid=oid))
            # If deleting
            elif request.form['submit'] == 'Delete':
                # Deletes associated item images
                images = conn.execute(Item.get_images, {
                    'OID' : oid,
                }).fetchall()
                for imageTuple in images:
                    delete_image(imageTuple[0])
                # Deletes the item
                conn.execute(Item.delete, {
                    'OID' : oid,
                })
                # Commits the transaction changes
                transaction.commit()

                flash(u'Item deleted.', 'success')
                return redirect(url_for('search_page'))
            # If checking out
            elif request.form['submit'] == 'Check Out':
                # Checks out the item
                conn.execute(Item.checkout, {
                    'OID' : oid,
                    'UID' : g.user['UID'],
                })
                # Commits the transaction changes
                transaction.commit()

                flash(u'Item checked out.', 'success')
                return redirect(url_for('item_page', oid=oid))
            # If checking in
            elif request.form['submit'] == 'Check In':
                # Checks in the item
                conn.execute(Item.checkin, {
                    'OID' : oid,
                })
                # Commits the transaction changes
                transaction.commit()

                flash(u'Item checked in.', 'success')
                return redirect(url_for('item_page', oid=oid))
        except:
            # Rollback and discard transaction changes upon failure
            transaction.rollback()
            flash(u'An error occurred.', 'success')
            raise

    return redirect(url_for('search_page'))

# Add Item Route: HTML Template
@app.route('/items/new', methods=['GET'])
@login_required()
def additem_page():
    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Condition.find_all).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Era.find_all).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Color.find_all).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

    return render_template('additem.html',
                            conditions = conditionList,
                            colors     = colorList,
                            eras       = eraList)

# Add Item Route: POST method after form submission
@app.route('/items/new', methods=['POST'])
@login_required()
def additem():
    # Checks if required fields exist in form
    if 'itemName' not in request.form or \
            'itemDescription' not in request.form or \
            'itemCategory' not in request.form or \
            'itemCondition' not in request.form or \
            'itemEra' not in request.form or \
            'itemColors' not in request.form or \
            'itemSize' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return additem_page()

    # Get search bar input
    itemName = request.form['itemName'].capitalize()

    # get detail inputs
    itemDescription = request.form['itemDescription'].capitalize()
    itemCategory    = request.form['itemCategory']
    itemCondition   = request.form['itemCondition']
    itemEra         = request.form['itemEra']
    itemColors      = request.form['itemColors']
    itemSize        = request.form['itemSize'].capitalize()

    # Checks if required fields are empty
    if itemName == '':
        flash(u'Name field cannot be empty.', 'danger')
        return additem_page()
    if itemCategory == '':
        flash(u'Please select a category.', 'danger')
        return additem_page()
    if itemCondition == '':
        flash(u'Please select a condition.', 'danger')
        return additem_page()

    # Handles image file uploading
    if request.files['image']:
        images = request.files.getlist('image')
    else:
        images = []

    with DatabaseConnection() as conn:
        # Begins a transaction
        transaction = conn.begin()
        try:
            # Parse the inputs
            if itemDescription == '':
                itemDescription = None

            if itemSize == '':
                itemSize = None

            cnid = conn.execute(Condition.find_by_name, {
                'CNDTNNAME' : itemCondition.capitalize(),
            }).fetchone()
            if cnid:
                cnid = cnid[0]

            eid = conn.execute(Era.find_by_name, {
                'ERANAME' : itemEra.capitalize(),
            }).fetchone()
            if eid:
                eid = eid[0]

            # Add the item
            conn.execute(Item.insert, {
                'OBJECTNAME'  : itemName,
                'DESCRIPTION' : itemDescription,
                'TYPE'        : convertCategory(itemCategory),
                'SIZE'        : itemSize,
                'CNID'        : cnid,
                'EID'         : eid,
            })

            oid = conn.execute(Item.get_next_oid).fetchone()
            if oid:
                oid = oid[0]

            colorNames = itemColors.split(',')
            colorIDs = []
            for colorName in colorNames:
                colorID = conn.execute(Color.find_by_name, {
                    'COLORNAME' : colorName.capitalize(),
                }).fetchone()
                if colorID:
                    colorIDs.append(colorID[0])

            for cid in colorIDs:
                conn.execute(Item.insert_into_color, {
                    'OID' : oid,
                    'CID' : cid,
                })

            for image in images:
                order = conn.execute(Item.get_picture_count, {
                    'OID' : oid,
                }).fetchone()[0]
                if order:
                    order += 1
                else:
                    order = 1
                imageName = save_image(image)
                conn.execute(Item.insert_into_picture, {
                    'OID'      : oid,
                    'IMAGE'    : imageName,
                    'OBJORDER' : order,
                })

            # Commits the transaction changes
            transaction.commit()
            flash(u'Item added.', 'success')
        except:
            # Rollback and discard transaction changes upon failure
            transaction.rollback()
            flash(u'An error occurred.', 'danger')
            raise
    return redirect(url_for('search_page'))

@app.route('/accounts', methods=['GET'])
@login_required()
def manage_accounts():
    with DatabaseConnection() as conn:
        accounts = conn.execute(User.find_all).fetchall()
    return render_template('manageAccounts.html', accounts=accounts)

@app.route('/account/verify/<int:userId>', methods=['POST'])
@login_required()
def toggle_account_status(userId):
    with DatabaseConnection() as conn:
        conn.execute(User.toggle_status, {
            'UID' : userId,
        })
    return redirect(url_for('manage_accounts'))

@app.route('/account/delete/<int:userId>', methods=['POST'])
@login_required()
def delete_account(userId):
    with DatabaseConnection() as conn:
        conn.execute(User.delete_one, {
            'UID' : userId,
        })
    return redirect(url_for('manage_accounts'))

@app.route('/options', methods=['GET'])
@login_required()
def manage_options():
    with DatabaseConnection() as conn:
        colors = conn.execute(Color.find_all).fetchall()
        eras = conn.execute(Era.find_all).fetchall()
    return render_template('manageOptions.html', colors=colors, eras=eras)

@app.route('/colors', methods=['POST'])
@login_required()
def add_color():
    if not len(request.form['newColorName']):
        flash(u'Please enter color name.', 'danger')
    else:
        newColorName = request.form['newColorName']
        with DatabaseConnection() as conn:
            conn.execute(Color.add, {
                'COLORNAME' : newColorName,
            })
    return redirect(url_for('manage_options'))

@app.route('/colors/<int:cid>', methods=['POST'])
@login_required()
def update_color(cid):
    newColorName = request.form['newColorName']
    if not len(newColorName):
        flash(u'Please enter new color name.', 'danger')
    else:
        with DatabaseConnection() as conn:
            conn.execute(Color.update, {
                'CID' : cid,
                'NEWCOLORNAME': newColorName
            })
    return redirect(url_for('manage_options'))

@app.route('/colors/delete/<int:cid>', methods=['POST'])
@login_required()
def delete_color(cid):
    with DatabaseConnection() as conn:
        conn.execute(Color.delete, {
            'CID' : cid,
        })
    return redirect(url_for('manage_options'))

@app.route('/eras', methods=['POST'])
@login_required()
def add_era():
    if not len(request.form['newEraName']):
        flash(u'Please enter era name.', 'danger')
    else:
        newEraName = request.form['newEraName']
        with DatabaseConnection() as conn:
            conn.execute(Era.add, {
                'ERANAME' : newEraName,
            })
    return redirect(url_for('manage_options'))

@app.route('/eras/<int:eid>', methods=['POST'])
@login_required()
def update_era(eid):
    newEraName = request.form['newEraName']
    if not len(newEraName):
        flash(u'Please enter new era name.', 'danger')
    else:
        with DatabaseConnection() as conn:
            conn.execute(Era.update, {
                'EID' : eid,
                'NEWERANAME': newEraName
            })
    return redirect(url_for('manage_options'))

@app.route('/eras/delete/<int:eid>', methods=['POST'])
@login_required()
def delete_era(eid):
    with DatabaseConnection() as conn:
        conn.execute(Era.delete, {
            'EID' : eid,
        })
    return redirect(url_for('manage_options'))
