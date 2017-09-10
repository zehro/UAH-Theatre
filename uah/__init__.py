from flask import Flask
from binascii import unhexlify

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'some_secret' #should hexlify a key

import uah.views
