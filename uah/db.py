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

def String buildSearch(name, type, condition, era, checkedout, color, dimension, size):
	query = 'SELECT OID FROM OBJECT WHERE';
	if (name != null):
		query += ' NAME = %' + str(name) + '% AND '
	if (type != null):
		query += ' TYPE = \'' + str(type) + '\''
	if (condition != null):
		query += ' OID IN (SELECT OID FROM OBJECT NATURAL JOIN CNDTN WHERE CNDTNNAME = ' + str(condition) + ') AND '
	if (era != null):
		query += ' OID IN (SELECT OID FROM OBJECT NATURAL JOIN ERA WHERE ERANAME = ' + str(era) + ') AND '
	if (checkedout != null):
		if (checkedout):
			query += ' CHECKEDOUTTO IS NOT NULL AND '
		else if (!checkedout):
			query += ' CHECKEDOUTTO IS NULL AND '
	if (color != null):
		query += ' OID IN (SELECT OID FROM OBJECTCOLOR NATURAL JOIN COLOR WHERE COLORNAME = ' + str(color) + ') AND '
	if (type == 'p' && dimension != null):
		query += ' OID IN (SELECT OID FROM PROP WHERE DIMENSION = ' + str(dimension) + ') AND '
	if (type == 'c' && size != null):
		query += ' OID IN (SELECT OID FROM COSTUME WHERE SIZE = \'' + str(size) + '\' AND '
	return query[:-5];
