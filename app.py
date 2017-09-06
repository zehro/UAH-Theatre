# Imports
from flask import Flask, render_template, request, redirect, url_for, session, g
from sqlalchemy import create_engine
from time import gmtime, strftime

# Flask Settings
app = Flask(__name__)
app.debug = True


engine = create_engine('mysql+pymysql://test:sombra123@35.185.36.22/UAH_Theater')
connection = engine.connect()
result = connection.execute("select * from AUDITACTION")
# for row in result:
#     print("Audit Action:", row['Name'])
# connection.close()


# API Routes
@app.route('/')
def index_page():
    return redirect('/login')

@app.route('/logout')
def logout():
    return redirect(url_for('index_page'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('home_page'))

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    result = connection.execute("INSERT INTO AUDIT(ACTION, TIME, USER) VALUES (1, %s ,1)", (strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    return redirect(url_for('login_page'))

@app.route('/home', methods=['GET'])
def home_page():
    return render_template('home.html')

# Main Program
if __name__ == '__main__':
    app.run()
