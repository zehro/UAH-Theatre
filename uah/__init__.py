from flask import Flask
from binascii import unhexlify

app = Flask(__name__, static_url_path='/static')
app.secret_key = unhexlify('554148205468656174726520496E76656E746F72793A20536563726574204B657921')

import uah.views
