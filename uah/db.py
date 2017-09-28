from sqlalchemy import create_engine
from bunch import Bunch
from time import gmtime, strftime

# Creates a SQLAlchemy engine to execute query statements on the engine's connection
engine = create_engine('mysql+pymysql://test:sombra123@35.185.36.22/UAH_Theater')

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
User.findby_username = 'SELECT USERNAME, ISADMIN FROM USER WHERE USERNAME = %(Username)s AND ISVERIFIED = 1'
User.check_login     = 'SELECT USERNAME, ISADMIN FROM USER WHERE USERNAME = %(Username)s AND PASSWORD = %(Password)s AND ISVERIFIED = 1'

Item = Bunch()
Item.get_era_filters       = 'SELECT ERANAME FROM ERA'
Item.get_color_filters     = 'SELECT COLORNAME FROM COLOR'
Item.get_condition_filters = 'SELECT CNDTNNAME FROM CNDTN'
Item.get_images            = 'SELECT IMAGE FROM PICTURE WHERE OID = %(OID)s'
Item.get_colors            = 'SELECT COLORNAME FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE OID = %(OID)s'




#Any input that isn't being searched on should be null
def buildSearch(name, objecttype, condition, era, checkedout, color, dimension, size):
    query = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA WHERE';
    if (name != null):
        query += ' OBJECTNAME = %' + str(name) + '% AND '
    if (objecttype != null):
        query += ' TYPE = \'' + str(type) + '\''
    if (condition != null):
        query += ' CNDTNNAME = ' + str(condition) + ' AND '
    if (era != null):
        query += ' ERANAME = ' + str(era) + ' AND '
    if (checkedout != null):
        if (checkedout):
            query += ' CHECKEDOUTTO IS NOT NULL AND '
        elif (not checkedout):
            query += ' CHECKEDOUTTO IS NULL AND '
    if (color != null):
        query += ' OID IN (SELECT OID FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE COLORNAME = ' + str(color) + ') AND '
    if (objecttype == 'p' and dimension != null):
        query += ' OID IN (SELECT OID FROM PROP WHERE DIMENSION = ' + str(dimension) + ') AND '
    if (objecttype == 'c' and size != null):
        query += ' OID IN (SELECT OID FROM COSTUME WHERE SIZE = \'' + str(size) + '\' AND '
    return query[:-5];

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
    print name #placeholder
