from flask import Flask, redirect, url_for, session, render_template, request, flash
from datetime import timedelta
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from authlib.integrations.flask_client import OAuth
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://127.0.0.1:5000/auth_callback"

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Google CLIENT_ID and CLIENT_SECRET must be set as environment variables.")

flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    },
    scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
)

oauth = OAuth(app)
facebook = oauth.register(
    name='facebook',    
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    authorize_url='https://www.facebook.com/v14.0/dialog/oauth',
    authorize_params=None,
    access_token_url='https://graph.facebook.com/v14.0/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    client_kwargs={'scope': 'email'},
)

# connection = sqlite3.connect("profile.db",)

def create_tables():
    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        username TEXT UNIQUE NOT NULL, 
        email TEXT UNIQUE NOT NULL, 
        name TEXT, 
        friends TEXT, 
        posts BLOB, 
        number INTEGER, 
        dob TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
        sender TEXT NOT NULL, 
        receiver TEXT NOT NULL, 
        text TEXT, 
        blob BLOB,
        FOREIGN KEY (sender) REFERENCES profiles(username),
        FOREIGN KEY (receiver) REFERENCES profiles(username)
    )
    """)
    
    connection.commit()

def insert_profile(name, email, username = 'hiii', number  = None, dob = None):
    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
        INSERT INTO profiles (username, name, email, number, dob, friends)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username, name, email, number, dob, None))
        connection.commit()
        print(f"Profile for {username} added successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error inserting profile: {e}")

def chats_list(username):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

        # SQL query to find the latest message for each unique username
        query = """
        SELECT sender, sender_username, receiver, receiver_username, text
        FROM chats
        WHERE id IN (
            SELECT MAX(id) 
            FROM chats
            WHERE sender_username = ? OR receiver_username = ?
            GROUP BY 
                CASE 
                    WHEN sender_username = ? THEN receiver_username 
                    ELSE sender_username 
                END
        )
        ORDER BY id DESC
        """

        # Execute the query with the username
        cursor.execute(query, (username, username, username))

        # Fetch all matching rows
        rows = cursor.fetchall()

        # Transform rows into a list of dictionaries
        results = []
        for row in rows:
            if row[1] == username:
                results.append({
                    "name": row[2],
                    "username": row[3],
                    "text": row[4],
                })
            else:
                results.append({
                    "name": row[0],
                    "username": row[1],
                    "text": row[4],
                })

        return results
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if connection:
            connection.close()

def chats(username, recipient_username):
    try:
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

        query = """
        SELECT sender, sender_username, text, blob
        FROM chats
        WHERE ((sender_username = ? AND receiver_username = ?) OR (sender_username = ? AND receiver_username = ?))
        ORDER BY id DESC
        """

        cursor.execute(query,(username, recipient_username, recipient_username, username))
        rows = cursor.fetchall()
        chats = []
        for row in rows:
            chats.append({
                "sender": row[0],
                "sender_username" : row[1],
                "text" : row[2],
                "blob" : row[3]

            })
        return chats
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if connection:
            connection.close()

create_tables()

@app.route('/')
def index():
    if(session.get('user') or session.get('email')):
        return redirect(url_for('chats'))
    
    return render_template('SignIn.html')

@app.route('/loginWithGoogle')
def loginWithGoogle():
    try:
        flow.redirect_uri = REDIRECT_URI
        authorization_url, state = flow.authorization_url(prompt='consent')
        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        flash(f"An error occurred while initiating login: {str(e)}")
        return redirect(url_for('index'))

@app.route('/loginWithFacebook')
def loginWithFacebook():
    # Redirect the user to Facebook for authorization
    redirect_uri = url_for('FB_auth_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)

@app.route('/FB_auth_callback')
def FB_auth_callback():
    # Retrieve the access token
    token = facebook.authorize_access_token()

    # Use the token to fetch user information from Facebook
    resp = facebook.get('https://graph.facebook.com/me?fields=id,name,email', token=token)
    user = resp.json()

    # Save the user information in the session
    session['email'] = user.get('email')
    session['name'] = user.get('name')

    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()      
    cursor.execute("SELECT 1 FROM profiles WHERE email = ? LIMIT 1;", (user.get('email'),))
    result = cursor.fetchone()
    if not result:
        insert_profile(session['name'], session['email'], "hiii")
    return redirect(url_for('chats'))

@app.route('/auth_callback')
def callback():
    if 'state' not in session:
        flash("Session state missing. Please try logging in again.")
        return redirect(url_for('index'))
    
    if session['state'] != request.args.get('state'):
        flash("Invalid session state. Please try logging in again.")
        return redirect(url_for('index'))
    
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_obj = google.auth.transport.requests.Request()
        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token, request=request_obj, audience=CLIENT_ID
        )
        session['email'] = id_info.get('email')
        session['name'] = id_info.get('name')
        
        connection = sqlite3.connect("profile.db")
        cursor = connection.cursor()      
        cursor.execute("SELECT 1 FROM profiles WHERE email = ? LIMIT 1;", (id_info.get('email'),))
        result = cursor.fetchone()

        if not result:
            insert_profile(session['name'], session['email'], "hiii")

        
        return redirect(url_for('chats'))
    except Exception as e:
        flash(f"An error occurred during authentication: {str(e)}")
        return redirect(url_for('index'))

@app.route('/dm')
def DM():
    return render_template('DMs.html')

@app.route('/chats')
def chats():
    return render_template('chats.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')
    
@app.route('/settings/edit')
def edit():
    return render_template('EditProfile.html')

@app.route('/search')
def search():
    return render_template('Search.html')

@app.route('/profile')
def profile():
    return render_template('Profilepage.html')

@app.route('/notification')
def notification():
    return render_template('notifications.html')

@app.route('/profileinfo')
def profileinfo():
    return render_template('ProfileInfo.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('ssl.crt', 'ssl.key'))