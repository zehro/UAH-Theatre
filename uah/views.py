from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from uah import app
from uah.db import *
from uah.image_uploader import save_image, load_image
from uah.sessions import *

import sys

# Sets up variables/functions for use in Jinja templates
@app.context_processor
def inject_isAdmin_function():
    def isAdmin():
        if g.user:
            return g.user['isAdmin'] == TRUE
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
            'Username' : username,
            'Password' : password
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
                'Username' : username,
                'Password' : password
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
        conditionQuery = conn.execute(Item.get_condition_filters).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Item.get_color_filters).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Item.get_era_filters).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the size filters
        sizeQuery = conn.execute(Item.get_size_filters).fetchall()
        sizeList = []
        for sizeTuple in sizeQuery:
            sizeList.append(sizeTuple[1])

        # Gets the dimension filters
        dimensionQuery = conn.execute(Item.get_dimension_filters).fetchall()
        dimensionList = []
        for dimensionTuple in dimensionQuery:
            dimensionList.append(dimensionTuple[1])

        # Get all search results and no filters
        searchQuery = buildSearch('', '', '', '', '', '', '', '', '')

        # Gets the search results
        searchResults = conn.execute(searchQuery).fetchall()

    return render_template('search.html',
                            conditions = conditionList,
                            colors     = colorList,
                            eras       = eraList,
                            sizes      = sizeList,
                            dimensions = dimensionList,
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
            'itemSize' not in request.form or \
            'itemDimension' not in request.form:
        flash(u'Required fields do not exist.', 'danger')
        return search_page()

    # Get search bar input
    itemName = request.form['itemName']

    # get filter inputs
    itemCategory  = request.form['itemCategory']
    itemCondition = request.form['itemCondition']
    itemColor     = request.form['itemColor']
    itemEra       = request.form['itemEra']
    itemChecked   = request.form['itemChecked']

    # check optional filters
    itemSize      = request.form['itemSize'].upper()
    itemDimension = request.form['itemDimension'].capitalize()

    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Item.get_condition_filters).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Item.get_color_filters).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Item.get_era_filters).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the size filters
        sizeQuery = conn.execute(Item.get_size_filters).fetchall()
        sizeList = []
        for sizeTuple in sizeQuery:
            sizeList.append(sizeTuple[1])

        # Gets the dimension filters
        dimensionQuery = conn.execute(Item.get_dimension_filters).fetchall()
        dimensionList = []
        for dimensionTuple in dimensionQuery:
            dimensionList.append(dimensionTuple[1])

        # Get the search query
        searchQuery = buildSearch('', itemName, convertCategory(itemCategory),
                                  itemCondition, itemColor, itemEra,
                                  convertChecked(itemChecked),
                                  itemSize, itemDimension)

        # Gets the search results
        searchResults = conn.execute(searchQuery).fetchall()

        return render_template('search.html',
                                conditions        = conditionList,
                                colors            = colorList,
                                eras              = eraList,
                                sizes             = sizeList,
                                dimensions        = dimensionList,
                                items             = searchResults,
                                selectedCategory  = itemCategory,
                                selectedCondition = itemCondition,
                                selectedColor     = itemColor,
                                selectedEra       = itemEra,
                                selectedChecked   = itemChecked,
                                selectedSize      = itemSize,
                                selectedDimension = itemDimension)

# View Item Route: HTML Template
@app.route('/items/id/<int:oid>', methods=['GET'])
@login_required()
def item_page(oid):
    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Item.get_condition_filters).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Item.get_color_filters).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Item.get_era_filters).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the size filters
        sizeQuery = conn.execute(Item.get_size_filters).fetchall()
        sizeList = []
        for sizeTuple in sizeQuery:
            sizeList.append(sizeTuple[1])

        # Gets the dimension filters
        dimensionQuery = conn.execute(Item.get_dimension_filters).fetchall()
        dimensionList = []
        for dimensionTuple in dimensionQuery:
            dimensionList.append(dimensionTuple[1])

        # Get an item by an OID
        searchQuery = buildSearch(oid, '', '', '', '', '', '', '', '')

        # Get the item
        item = conn.execute(searchQuery).fetchone()

        # Get the item's images
        images = conn.execute(Item.get_images, {
            'OID' : oid,
        }).fetchall()

        # Get the item's colors
        colors = conn.execute(Item.get_colors, {
            'OID' : oid,
        }).fetchall()

        # Get the item's size
        size = conn.execute(Item.get_size, {
            'OID' : oid,
        }).fetchone()
        if size != None:
            size = size[0]

        # Get the item's dimension
        dimension = conn.execute(Item.get_dimension, {
            'OID' : oid,
        }).fetchone()
        if dimension != None:
            dimension = dimension[0]

        # Get the item's borrower, if it has one
        checkedTo = conn.execute(Item.get_borrower, {
            'OID' : oid,
        }).fetchone()

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
                            borrower       = checkedTo[0],
                            item           = item,
                            images         = images,
                            size           = size,
                            dimension      = dimension,
                            itemColors     = itemColors,
                            itemColorArray = itemColorArray,
                            conditions     = conditionList,
                            colors         = colorList,
                            eras           = eraList,
                            sizes          = sizeList,
                            dimensions     = dimensionList)

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
            ('itemSize' not in request.form and \
            'itemDimension' not in request.form):
        flash(u'Required fields do not exist.', 'danger')
        return item_page(oid)

    # Get search bar input
    itemName = request.form['itemName']

    # get filter inputs
    itemDescription = request.form['itemDescription']
    itemCategory    = request.form['itemCategory']
    itemCondition   = request.form['itemCondition']
    itemEra         = request.form['itemEra']
    itemColors      = request.form['itemColors']

    # check optional filters
    if 'itemSize' in request.form:
        itemSize = request.form['itemSize']
    elif 'itemDimension' in request.form:
        itemDimension = request.form['itemDimension']

    with DatabaseConnection() as conn:
        # Begins a transaction
        transaction = conn.begin()
        try:
            # If updating
            if request.form['submit'] == 'Confirm':
                # # Updates the item
                # conn.execute(Item.update)

                # Commits the transaction changes
                transaction.commit()

                flash(u'Item updated.', 'success')
                return redirect(url_for('item_page', oid=oid))
            # If deleting
            elif request.form['submit'] == 'Delete':
                # # Deletes the item
                # conn.execute(Item.delete)

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
            raise

    return redirect(url_for('search_page'))

# Add Item Route: HTML Template
@app.route('/items/new', methods=['GET'])
@login_required()
def additem_page():
    with DatabaseConnection() as conn:
        # Gets the condition filters
        conditionQuery = conn.execute(Item.get_condition_filters).fetchall()
        conditionList = []
        for conditionTuple in conditionQuery:
            conditionList.append(conditionTuple[1])

        # Gets the color filters
        colorQuery = conn.execute(Item.get_color_filters).fetchall()
        colorList = []
        for colorTuple in colorQuery:
            colorList.append(colorTuple[1])

        # Gets the era filters
        eraQuery = conn.execute(Item.get_era_filters).fetchall()
        eraList = []
        for eraTuple in eraQuery:
            eraList.append(eraTuple[1])

        # Gets the size filters
        sizeQuery = conn.execute(Item.get_size_filters).fetchall()
        sizeList = []
        for sizeTuple in sizeQuery:
            sizeList.append(sizeTuple[1])

        # Gets the dimension filters
        dimensionQuery = conn.execute(Item.get_dimension_filters).fetchall()
        dimensionList = []
        for dimensionTuple in dimensionQuery:
            dimensionList.append(dimensionTuple[1])

    return render_template('additem.html',
                            conditions        = conditionList,
                            colors            = colorList,
                            eras              = eraList,
                            sizes             = sizeList,
                            dimensions        = dimensionList)

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
            ('itemSize' not in request.form and \
            'itemDimension' not in request.form):
        flash(u'Required fields do not exist.', 'danger')
        return additem_page()

    # Get search bar input
    itemName = request.form['itemName']

    # get detail inputs
    itemDescription = request.form['itemDescription']
    itemCategory    = request.form['itemCategory']
    itemCondition   = request.form['itemCondition']
    itemEra         = request.form['itemEra']
    itemColors      = request.form['itemColors']

    # check optional filters
    if 'itemSize' in request.form:
        itemSize = request.form['itemSize']
    elif 'itemDimension' in request.form:
        itemDimension = request.form['itemDimension']

    # Checks if required fields are empty
    if itemName == '':
        flash(u'Name field cannot be empty.', 'danger')
        return additem_page()
    if itemCategory == '':
        flash(u'Please select a category.', 'danger')
        return additem_page()
    if itemEra == '':
        flash(u'Please select an era.', 'danger')
        return additem_page()
    if itemColors == '':
        flash(u'Please select a color.', 'danger')
        return additem_page()
    if (itemCategory == 'costume' and itemSize == ''):
        flash(u'Please select a size.', 'danger')
        return additem_page()
    if (itemCategory == 'prop' and itemDimension == ''):
        flash(u'Please select a dimension.', 'danger')
        return additem_page()
    if itemCondition == '':
        flash(u'Please select a condition.', 'danger')
        return additem_page()

    # Handles image file uploading
    if request.files:
        image = request.files['image']
        imageName = save_image(image)

    print(request.files['image'], file=sys.stderr)

    with DatabaseConnection() as conn:
        # Begins a transaction
        transaction = conn.begin()
        try:
            # Parse the inputs into unique IDs
            oid = conn.execute(Item.get_new_oid).fetchone()[0] + 1

            eid = conn.execute(Item.get_new_era, {
                'Era' : itemEra,
            }).fetchone()[0]

            colorNames = itemColors.split(',')
            colorIDs = []
            for colorName in colorNames:
                colorID = conn.execute(Item.get_new_color, {
                    'Color' : colorName,
                }).fetchone()
                colorIDs.append(colorID[0])

            cnid = conn.execute(Item.get_new_condition, {
                'Condition' : itemCondition,
            }).fetchone()[0]

            # Add the item
            conn.execute(Item.insert_into_object, {
                'OID'         : oid,
                'Name'        : itemName,
                'Description' : itemDescription,
                'Type'        : convertCategory(itemCategory),
                'CNID'        : cnid,
                'EID'         : eid,
            })

            for cid in colorIDs:
                conn.execute(Item.insert_into_color, {
                    'OID' : oid,
                    'CID' : cid,
                })

            # Updates tables for the size property
            if 'itemSize' in request.form:
                sid = conn.execute(Item.get_new_size, {
                    'Size' : itemSize,
                }).fetchone()[0]

                conn.execute(Item.insert_into_costume, {
                    'OID' : oid,
                    'SID' : sid,
                })
            # Updates tables for the dimension property
            elif 'itemDimension' in request.form:
                did = conn.execute(Item.get_new_dimension, {
                    'Dimension' : itemDimension,
                }).fetchone()[0]

                conn.execute(Item.insert_into_prop, {
                    'OID' : oid,
                    'DID' : did,
                })

            conn.execute(Item.insert_into_picture, {
                'OID' : oid,
                'ImageBlob' : imageName,
            })

            # Commits the transaction changes
            transaction.commit()
            flash(u'Item added.', 'success')
        except:
            # Rollback and discard transaction changes upon failure
            transaction.rollback()
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
