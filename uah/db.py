from sqlalchemy import create_engine
from bunch import Bunch
from time import gmtime, strftime

# Creates a SQLAlchemy engine to execute query statements on the engine's connection
engine = create_engine('postgres://zofcfonftlaxgc:6b740a65d78cfbb48421918f357ddc36b09078c58f18e6f91aec64f12fab0686@ec2-54-225-112-61.compute-1.amazonaws.com:5432/d29sibnn2hc0ib')
#TODO: remove mysqlengine below
#engine = create_engine('mysql+pymysql://test:sombra123@35.185.36.22/UAH_Theater')

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
    category = category.capitalize()
    if category == 'Costume':
        return 'c'
    if category == 'Prop':
        return 'p'
    return category

def convertChecked(status):
    if status == 'checked-in':
        return False
    if status == 'checked-out':
        return True
    return status

# Creates Bunch contexts for the database schema and queries
User = Bunch()
User.find_all        = 'SELECT * FROM ACCOUNT'
User.findby_username = 'SELECT UID, USERNAME, ISADMIN, ISVERIFIED FROM ACCOUNT WHERE USERNAME = %(USERNAME)s AND ISVERIFIED = true'
User.check_login     = 'SELECT UID, USERNAME, ISADMIN, ISVERIFIED FROM ACCOUNT WHERE USERNAME = %(USERNAME)s AND PASSWORD = %(PASSWORD)s AND ISVERIFIED = true'
User.insert          = 'INSERT INTO ACCOUNT(USERNAME, PASSWORD, FIRSTNAME, LASTNAME) VALUES (%(USERNAME)s, %(PASSWORD)s, %(FIRSTNAME)s, %(LASTNAME)s)'
User.toggle_status   = 'UPDATE ACCOUNT SET ISVERIFIED = IF(ISVERIFIED=true, false, true) WHERE UID = %(UID)s'
User.delete          = 'DELETE FROM ACCOUNT WHERE UID = %(UID)s'

Item = Bunch()
Item.select_all          = '''SELECT OID,
                                     OBJECTNAME,
                                     DESCRIPTION,
                                     TYPE,
                                     SIZE,
                                     CNDTNNAME,
                                     ERANAME,
                                     CHECKEDOUTTO,
                                     IMAGE
                                FROM OBJECT
                                NATURAL LEFT OUTER JOIN CNDTN
                                NATURAL LEFT OUTER JOIN ERA
                                NATURAL LEFT OUTER JOIN (
                                    SELECT * FROM PICTURE WHERE OBJORDER = 1)
                                    AS PICTURES'''
Item.order               = ' ORDER BY OBJECTNAME'
Item.find_all            = Item.select_all + Item.order
Item.findby_oid          = Item.select_all + ' WHERE OID = %(OID)s'
Item.get_images          = 'SELECT IMAGE FROM PICTURE WHERE OID = %(OID)s'
Item.get_colors          = 'SELECT COLORNAME FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE OID = %(OID)s'
Item.get_borrower        = 'SELECT USERNAME FROM ACCOUNT WHERE UID IN (SELECT CHECKEDOUTTO FROM OBJECT WHERE OID = %(OID)s)'
Item.get_next_oid        = 'SELECT MAX(OID) FROM OBJECT'
Item.get_picture_count   = 'SELECT MAX(OBJORDER) AS OBJORDER FROM PICTURE WHERE OID = %(OID)s'
Item.insert              = 'INSERT INTO OBJECT(OBJECTNAME, DESCRIPTION, TYPE, SIZE, CNID, EID) VALUES (%(OBJECTNAME)s, %(DESCRIPTION)s, %(TYPE)s, %(SIZE)s, %(CNID)s, %(EID)s)'
Item.insert_into_color   = 'INSERT INTO OBJECTCOLOR(OID, CID) VALUES (%(OID)s, %(CID)s)'
Item.insert_into_picture = 'INSERT INTO PICTURE(OID, IMAGE, OBJORDER) VALUES (%(OID)s, %(IMAGE)s, %(OBJORDER)s)'
Item.update              = 'UPDATE OBJECT SET OBJECTNAME = %(OBJECTNAME)s, DESCRIPTION = %(DESCRIPTION)s, TYPE = %(TYPE)s, SIZE = %(SIZE)s, CNID = %(CNID)s, EID = %(EID)s WHERE OID = %(OID)s'
Item.checkout            = 'UPDATE OBJECT SET CHECKEDOUTTO = %(UID)s WHERE OID = %(OID)s'
Item.checkin             = 'UPDATE OBJECT SET CHECKEDOUTTO = NULL WHERE OID = %(OID)s'
# #Delete a PICTURE:
# DELETE FROM PICTURE WHERE OID = oid AND OBJORDER = order;
# or
# DELETE FROM PICTURE WHERE IMAGE = 'image';
Item.delete              = 'DELETE FROM OBJECT WHERE OID = %(OID)s'
Item.delete_colors       = 'DELETE FROM OBJECTCOLOR WHERE OID = %(OID)s'

Condition = Bunch()
Condition.find_all     = 'SELECT * FROM CNDTN ORDER BY CNID'
Condition.find_by_name = 'SELECT * FROM CNDTN WHERE CNDTNNAME = %(CNDTNNAME)s'

Era = Bunch()
Era.find_all     = 'SELECT * FROM ERA ORDER BY ERANAME'
Era.find_by_name = 'SELECT * FROM ERA WHERE ERANAME = %(ERANAME)s'
Era.add          = 'INSERT INTO ERA(ERANAME) VALUES (%(ERANAME)s)'
Era.update       = 'UPDATE ERA SET ERANAME = %(NEWERANAME)s WHERE EID = %(EID)s'
Era.delete       = 'DELETE FROM ERA WHERE EID = %(EID)s'

Color = Bunch()
Color.find_all     = 'SELECT * FROM COLOR ORDER BY COLORNAME'
Color.find_by_name = 'SELECT * FROM COLOR WHERE COLORNAME = %(COLORNAME)s'
Color.add          = 'INSERT INTO COLOR(COLORNAME) VALUES (%(COLORNAME)s)'
Color.update       = 'UPDATE COLOR SET COLORNAME = %(NEWCOLORNAME)s WHERE CID = %(CID)s'
Color.delete       = 'DELETE FROM COLOR WHERE CID = %(CID)s'

# Any input that isn't being searched on should be null
def buildSearch(name, objecttype, condition, color, era, checkedout, size):
    query = Item.select_all

    if name != '' or \
            objecttype != '' or \
            condition != '' or \
            color != '' or \
            era != '' or \
            checkedout != '' or \
            size != '':
        query += ' WHERE '

        if name != '':
            query += 'OBJECTNAME = \'' + name + '\''
            if objecttype != '' or \
                    condition != '' or \
                    color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '':
                query += ' AND '

        if objecttype != '':
            query += 'TYPE = \'' + objecttype + '\''
            if condition != '' or \
                    color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '':
                query += ' AND '

        if condition != '':
            query += 'CNDTNNAME = \'' + condition + '\''
            if color != '' or \
                    era != '' or \
                    checkedout != '' or \
                    size != '':
                query += ' AND '

        if color != '':
            query += 'OID IN (SELECT OID FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE COLORNAME = \'' + color + '\')'
            if era != '' or \
                    checkedout != '' or \
                    size != '':
                query += ' AND '

        if era != '':
            query += 'ERANAME = \'' + era + '\''
            if checkedout != '' or \
                    size != '':
                query += ' AND '

        if checkedout != '':
            if (checkedout):
                query += 'CHECKEDOUTTO IS NOT NULL'
            elif (not checkedout):
                query += 'CHECKEDOUTTO IS NULL'
            if size != '':
                query += ' AND '

        if size != '':
            query += 'SIZE = \'' + size + '\''

    return query + Item.order;
