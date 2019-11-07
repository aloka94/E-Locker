from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key="secret"

# Database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'userlogin'


mysql = MySQL(app)


@app.route('/userlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Checking if account exists in database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Query using string concatenation. This makes the app SQL Injection Vulnerable
        #cursor.execute("SELECT * FROM users WHERE username = '%s' """ % username +"AND password = '%s' """ %password)
        
        # Parameterized query which prevents SQL Injection
        x = 'SELECT * FROM users WHERE username = %s AND password = %s'
        insert_values = (username, password)
        cursor.execute(x, insert_values)

        # Fetch existing record
        user = cursor.fetchone()
        if user:
            # Create session for logged in user
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            # Redirect to homepage
            return redirect(url_for('home'))
        else:
            # No existing account/ incorrect username/password
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)


@app.route('/userlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/userlogin/profile')
def profile():
    # Checking if any user is currently loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        userDetails = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', userDetails=userDetails)
    return redirect(url_for('login'))

@app.route('/userlogin/logout')
def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)