from sqlalchemy import create_engine
from bunch import Bunch
from time import gmtime, strftime

# Creates a SQLAlchemy engine to execute query statements on the engine's connection
engine = create_engine('mysql+pymysql://test:sombra123@35.185.36.22/UAH_Theater')
# new engine:
#engine = create_engine('postgres://zofcfonftlaxgc:6b740a65d78cfbb48421918f357ddc36b09078c58f18e6f91aec64f12fab0686@ec2-54-225-112-61.compute-1.amazonaws.com:5432/d29sibnn2hc0ib')

# Create a class for managing the database connection as an object
class DatabaseConnection:
    """
    Adds the ability to wrap a database connection.

    ``
    with DatabaseConnection() as conn:
        # do something with conn
    ``
    """

    def __enter__(self):
        # make a database connection and return it
        self.connection = engine.connect()
        return self.connection

    def __exit__(self, type, value, traceback):
        # make sure the database connection gets closed
        self.connection.close()

# Declares some useful constants
TRUE = 1
FALSE = 0

# Creates Bunch contexts for the database schema and queries
User = Bunch()
User.insert          = 'INSERT INTO USER(USERNAME, PASSWORD) VALUES (%(Username)s, %(Password)s)'
User.findby_username = 'SELECT USERNAME, ISADMIN, ISVERIFIED FROM USER WHERE USERNAME = %(Username)s AND ISVERIFIED = 1'
User.check_login     = 'SELECT USERNAME, ISADMIN, ISVERIFIED FROM USER WHERE USERNAME = %(Username)s AND PASSWORD = %(Password)s AND ISVERIFIED = 1'

Item = Bunch()
Item.find_all              = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA LEFT JOIN PICTURE ON OBJECT.OID = PICTURE.OID'
Item.findby_oid            = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA NATURAL JOIN PICTURE WHERE OID = %(OID)s'
#Item.insert
#Item.update
#Item.checkout
#Item.checkin
Item.get_images            = 'SELECT IMAGE FROM PICTURE WHERE OID = %(OID)s'
Item.get_colors            = 'SELECT COLORNAME FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE OID = %(OID)s'
Item.get_size_filters      = 'SELECT SIZENAME FROM SIZE'
Item.get_dimension_filters = 'SELECT DIMENSIONNAME FROM DIMENSION'
Item.get_era_filters       = 'SELECT ERANAME FROM ERA'
Item.get_color_filters     = 'SELECT COLORNAME FROM COLOR'
Item.get_condition_filters = 'SELECT CNDTNNAME FROM CNDTN'

def convertCategory(category):
    if category == 'costume':
        return 'c'
    if category == 'prop':
        return 'p'
    return category

def convertChecked(status):
    if status == 'Checked-In':
        return 1
    if status == 'Checked-Out':
        return 0
    return status

#Any input that isn't being searched on should be null
def buildSearch(name, objecttype, condition, color, era, checkedout, size, dimension):
    query = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA LEFT JOIN PICTURE'
    if name != '' or  \
            objecttype != '' or \
            condition != '' or \
            color != '' or \
            era != '' or \
            checkedout != '' or \
            size != '' or \
            dimension != '':
        query += ' WHERE '

    if name != '':
        query += 'OBJECTNAME = \'' + name + '\''
        if objecttype != '' or \
                condition != '' or \
                color != '' or \
                era != '':
            query += ' AND '

    if objecttype != '':
        query += 'TYPE = \'' + objecttype + '\''
        if condition != '' or \
                color != '' or \
                era != '':
            query += ' AND '

    if condition != '':
        query += 'CNDTNNAME = \'' + condition + '\''
        if color != '' or \
                era != '':
            query += ' AND '

    if color != '':
        query += 'OID IN (SELECT OID FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE COLORNAME = \'' + color + '\')'
        if era != '':
            query += ' AND '

    if era != '':
        query += 'ERANAME = \'' + era + '\''
        if checkedout != '':
            query += ' AND '

    if checkedout != '':
        if (checkedout):
            query += ' CHECKEDOUTTO IS NOT NULL'
        elif (not checkedout):
            query += ' CHECKEDOUTTO IS NULL'
        if size != '' or dimension != '':
            query += ' AND '

    if objecttype == 'c' and size != '':
        query += ' OID IN (SELECT OID FROM COSTUME WHERE SIZE = \'' + size + '\''
    elif objecttype == 'p' and dimension != '':
        query += ' OID IN (SELECT OID FROM PROP WHERE DIMENSION = ' + dimension + ')'

    return query;

#Name, objecttype, condition, and era are required of type String
#colors should be a list of valid colors
#For Costumes, size is required
#For props, dimension is required
def buildCreate(name, description, objecttype, condition, era, colors, dimension, size):
    return 'INSERT INTO OBJECT(OBJECTNAME, TYPE, CNID, EID) VALUES (\'New Object\', \'c\', 0, 0)'
    #query = [];
    #query.add('');
    #query[0] = 'INSERT INTO OBJECT(OBJECTNAME, DESCRIPTION, TYPE, CNID, EID) VALUES (\'' + name + '\', \''+ objecttype
    #for color in colors:

def buildUpdate(name, objecttype, condition, era, checkedout, color, dimension, size):
#similar to search, just not implemented yet
    print(name) #placeholder
