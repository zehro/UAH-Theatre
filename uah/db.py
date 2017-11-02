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

# Declares some useful functions
def convertCategory(category):
    if category == 'costume':
        return 'c'
    if category == 'prop':
        return 'p'
    return category

def convertChecked(status):
    if status == 'checked-in':
        return False
    if status == 'checked-out':
        return True
    return status

# Any input that isn't being searched on should be null
def buildSearch(oid, name, objecttype, condition, color, era, checkedout, size, dimension):
    query = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA NATURAL JOIN PICTURE WHERE OBJORDER = 1'

    if oid != '' or \
            name != '' or \
            objecttype != '' or \
            condition != '' or \
            color != '' or \
            era != '' or \
            checkedout != '' or \
            size != '' or \
            dimension != '':
        query += ' AND '

        if oid != '':
            query += 'OID = ' + str(oid)
            if name != '' or \
                    objecttype != '' or \
                    condition != '' or \
                    color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if name != '':
            query += 'OBJECTNAME = \'' + name + '\''
            if objecttype != '' or \
                    condition != '' or \
                    color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if objecttype != '':
            query += 'TYPE = \'' + objecttype + '\''
            if condition != '' or \
                    color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if condition != '':
            query += 'CNDTNNAME = \'' + condition + '\''
            if color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if color != '':
            query += 'OID IN (SELECT OID FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE COLORNAME = \'' + color + '\')'
            if era != '' or \
                    checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if era != '':
            query += 'ERANAME = \'' + era + '\''
            if checkedout != '' or \
                    size != '' or \
                    dimension != '':
                query += ' AND '

        if checkedout != '':
            if (checkedout):
                query += 'CHECKEDOUTTO IS NOT NULL'
            elif (not checkedout):
                query += 'CHECKEDOUTTO IS NULL'
            if size != '' or dimension != '':
                query += ' AND '

        if objecttype == 'c' and size != '':
            query += 'OID IN (SELECT OID FROM COSTUME NATURAL JOIN SIZE WHERE SIZENAME = \'' + size + '\')'
        elif objecttype == 'p' and dimension != '':
            query += 'OID IN (SELECT OID FROM PROP NATURAL JOIN DIMENSION WHERE DIMENSIONNAME = \'' + dimension + '\')'

    return query;

# Declares some useful constants
TRUE = 1
FALSE = 0

# Creates Bunch contexts for the database schema and queries
User = Bunch()
User.insert          = 'INSERT INTO USER(USERNAME, PASSWORD) VALUES (%(Username)s, %(Password)s)'

User.find_all        = 'SELECT * FROM USER'
User.toggle_status   = 'UPDATE USER SET ISVERIFIED = IF(ISVERIFIED=1, 0, 1) WHERE UID = %(UID)s'
User.delete_one      = 'DELETE FROM USER WHERE UID = %(UID)s'

User.findby_username = 'SELECT UID, USERNAME, ISADMIN, ISVERIFIED FROM USER WHERE USERNAME = %(Username)s AND ISVERIFIED = 1'
User.check_login     = 'SELECT UID, USERNAME, ISADMIN, ISVERIFIED FROM USER WHERE USERNAME = %(Username)s AND PASSWORD = %(Password)s AND ISVERIFIED = 1'



Item = Bunch()
Item.get_new_oid           = 'SELECT MAX(OID) AS OID FROM OBJECT'
Item.get_new_condition     = 'SELECT CNID FROM CNDTN WHERE CNDTNNAME = %(Condition)s'
Item.get_new_era           = 'SELECT EID FROM ERA WHERE ERANAME = %(Era)s'
Item.get_new_color         = 'SELECT CID FROM COLOR WHERE COLORNAME = %(Color)s'
Item.get_new_size          = 'SELECT SID FROM SIZE WHERE SIZENAME = %(Size)s'
Item.get_new_dimension     = 'SELECT DID FROM DIMENSION WHERE DIMENSIONNAME = %(Dimension)s'

Item.insert_into_object    = 'INSERT INTO OBJECT(OID, OBJECTNAME, DESCRIPTION, TYPE, CNID, EID) VALUES (%(OID)s, %(Name)s, %(Description)s, %(Type)s, %(CNID)s, %(EID)s)'
Item.insert_into_color     = 'INSERT INTO OBJECTCOLOR(OID, CID) VALUES (%(OID)s, %(CID)s)'
Item.insert_into_costume   = 'INSERT INTO COSTUME(OID, SID) VALUES (%(OID)s, %(SID)s)'
Item.insert_into_prop      = 'INSERT INTO PROP(OID, DID) VALUES (%(OID)s, %(DID)s)'
Item.insert_into_picture   = 'INSERT INTO PICTURE(OID, IMAGE) VALUES (%(OID)s, %(ImageBlob)s)'
# Item.update                = ''

Item.get_borrower          = 'SELECT USERNAME FROM USER WHERE UID IN (SELECT CHECKEDOUTTO FROM OBJECT WHERE OID = %(OID)s)'
Item.checkout              = 'UPDATE OBJECT SET CHECKEDOUTTO = %(UID)s WHERE OID = %(OID)s'
Item.checkin               = 'UPDATE OBJECT SET CHECKEDOUTTO = NULL WHERE OID = %(OID)s'

Item.find_all              = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA NATURAL JOIN PICTURE'
Item.findby_oid            = 'SELECT * FROM OBJECT NATURAL JOIN CNDTN NATURAL JOIN ERA NATURAL JOIN PICTURE WHERE OID = %(OID)s'

Item.get_images            = 'SELECT IMAGE FROM PICTURE WHERE OID = %(OID)s'
Item.get_colors            = 'SELECT COLORNAME FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE OID = %(OID)s'
Item.get_size              = 'SELECT SIZENAME FROM COSTUME NATURAL JOIN SIZE WHERE OID = %(OID)s'
Item.get_dimension         = 'SELECT DIMENSIONNAME FROM PROP NATURAL JOIN DIMENSION WHERE OID = %(OID)s'

Item.get_size_filters      = 'SELECT SID, SIZENAME FROM SIZE ORDER BY SID'
Item.get_dimension_filters = 'SELECT DID, DIMENSIONNAME FROM DIMENSION ORDER BY DID'
Item.get_era_filters       = 'SELECT EID, ERANAME FROM ERA ORDER BY EID'
Item.get_color_filters     = 'SELECT CID, COLORNAME FROM COLOR ORDER BY CID'
Item.get_condition_filters = 'SELECT CNID, CNDTNNAME FROM CNDTN ORDER BY CNID'
