from flask import Flask, redirect, url_for, session, render_template, request, flash, jsonify
from datetime import timedelta
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import os
import glob
import uuid
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "https://127.0.0.1:5000/auth_callback"
UPLOAD_FOLDER = 'static/images/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def create_tables():
    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        profile_pic TEXT,
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
        sender_username TEXT NOT NULL, 
        receiver_username TEXT NOT NULL, 
        text TEXT, 
        blob BLOB,
        FOREIGN KEY (sender) REFERENCES profiles(username),
        FOREIGN KEY (receiver) REFERENCES profiles(username)
    )
    """)
    
    connection.commit()

def chats_list(username):
    try:
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

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

        cursor.execute(query, (username, username, username))

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

def get_chats(username, recipient_username):
    try:
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

        query = """
        SELECT sender, sender_username, text, blob
        FROM chats
        WHERE ((sender_username = ? AND receiver_username = ?) OR (sender_username = ? AND receiver_username = ?))
        ORDER BY id DESC
        """
        cursor.execute(query, (username, recipient_username, recipient_username, username))
        rows = cursor.fetchall()
        chats = [{"sender": row[0], "sender_username": row[1], "text": row[2], "blob": row[3]} for row in rows]
        return chats
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if connection:
            connection.close()

@socketio.on('fetch_chats')
def fetch_chats(data):
    my_username = data['my_username']
    receiver_username = data['receiver_username']
    chats = get_chats(my_username, receiver_username)
    emit('update_chats', {'chats': chats}, broadcast=True)

def insert_chat(sender, sender_username, receiver, receiver_username, text):
    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO chats (sender, sender_username, receiver, receiver_username, text) VALUES (?, ?, ?, ?, ?)", 
                   (sender, sender_username, receiver, receiver_username, text))
    connection.commit()
    connection.close()

# SocketIO event to handle the message submission
@socketio.on('send_message')
def handle_message(data):
    sender = data['my_name']
    sender_username = data['my_username']
    receiver = data['name']
    receiver_username = data['username']
    text = data['text']
    
    insert_chat(sender, sender_username, receiver, receiver_username, text)
    
    # Broadcast the message to all connected clients
    emit('receive_message', {'sender_username': sender, 'receiver': receiver, 'text': text}, broadcast=True)

def get_posts(username):
    files = [os.path.basename(file) for file in glob.glob(f"static/images/uploads/posts/{username}-*") if os.path.isfile(file)]
    return files

@app.route('/addProfile', methods=['POST'])
def add_profile():
    if request.method == 'POST':
        username = request.form['username']
        number = request.form['number']
        dob = request.form['dob']
        name = session['name']
        email = session['email']
        session['username'] = username
        if session.get('pfp') == None:
            session['pfp'] = 'pfp.jpg'
        else:
            directory = os.path.dirname(session['pfp'])
            new_file_path = os.path.join(directory, session['username'] + '.jpg')
            os.rename(session['pfp'], new_file_path)
            session['pfp'] = session['username'] + '.jpg'

        connection = sqlite3.connect("profile.db")
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO profiles (profile_pic, username, name, email, number, dob, friends)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session['pfp'], username, name, email, number, dob, None))
            connection.commit()
            insertion_sort()
            return  redirect(url_for('chats'))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting profile: {e}")

def insertion_sort():
    # Connect to the SQLite database
    connection = sqlite3.connect('profile.db')
    cursor = conn.cursor()

    # Fetch all records from the profiles table
    cursor.execute("SELECT * FROM profiles")
    profiles = cursor.fetchall()

    # Insertion sort implementation based on the username field
    for i in range(1, len(profiles)):
        key = profiles[i]
        j = i - 1
        while j >= 0 and profiles[j][1] > key[1]:  # Compare usernames (index 1)
            profiles[j + 1] = profiles[j]
            j -= 1
        profiles[j + 1] = key

    # Clear the profiles table
    cursor.execute("DELETE FROM profiles")

    # Insert sorted records back into the table
    cursor.executemany(
        "INSERT INTO profiles (profile_pic, username, name, email, number, dob, friends) VALUES (?, ?, ?, ?, ?, ?, ?)",
        profiles,
    )

    # Commit changes and close the connection
    connection.commit()
    connection.close()

def get_profile(username):
    try:
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

        query = """
        SELECT profile_pic, name, username
        FROM profiles
        WHERE username = ?
        """

        cursor.execute(query, username)
        rows = cursor.fetchone()
        if rows == None:
            print("No profile found")
        return rows
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if connection:
            connection.close()

def search_profile(username):
    try:
        connection = sqlite3.connect('profile.db')
        cursor = connection.cursor()

        query = """
        SELECT profile_pic, name, username
        FROM profiles
        WHERE (username LIKE ? OR name LIKE ?)
        AND username != ?
        """

        cursor.execute(query,('%' + username + '%', '%' + username + '%', session['username']))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if connection:
            connection.close()

@app.route('/search', methods=['POST'])
def search():
    username = request.json.get('username', '')
    results = search_profile(username)
    # Format results for response
    profiles = [
        {"profile_pic": row[0], "name": row[1], "username": row[2]} for row in results
    ]
    return jsonify(profiles)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request'}), 400

    file = request.files['file']
    current_page = request.form.get('currentPage', '')
    if current_page == '/profileinfo':
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            session['pfp'] = filepath
            file.save(filepath)
            return jsonify({'success': True, 'message': 'File uploaded successfully!'})
    else:
        if file and allowed_file(file.filename):
            filename = session['username'] + "-" + secure_filename(file.filename)
            filepath = os.path.join("static/images/uploads/posts", filename)
            file.save(filepath)
            return jsonify({'success': True, 'message': 'File uploaded successfully!'})

    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

@app.route('/insert_chat', methods=['POST'])
def insert_chats():
    if request.method == 'POST':
        text = request.form['message']
        connection = sqlite3.connect("profile.db")
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO chats (sender, sender_username, receiver, receiver_username, text, blob)
            """, (session["name"], session["email"], receiver, receiver_username, text, blob))
            connection.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error inserting chat: {e}")

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
    token = facebook.authorize_access_token()

    resp = facebook.get('https://graph.facebook.com/me?fields=id,name,email', token=token)
    user = resp.json()

    session['email'] = user.get('email')
    session['name'] = user.get('name')

    connection = sqlite3.connect("profile.db")
    cursor = connection.cursor()      
    cursor.execute("SELECT profile_pic, username FROM profiles WHERE email = ?", (user.get('email'),))
    result = cursor.fetchone()
    if not result:
        return redirect(url_for('profileinfo'))
    else:
        session['pfp'] = result[0]
        session['username'] = result[1]
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
        cursor.execute("SELECT profile_pic, username FROM profiles WHERE email = ?", (id_info.get('email'),))
        result = cursor.fetchone()

        if not result:
            return redirect(url_for('profileinfo'))

        else:
            session['pfp'] = result[0]
            session['username'] = result[1]
            return redirect(url_for('chats'))

    except Exception as e:
        flash(f"An error occurred during authentication: {str(e)}")
        return redirect(url_for('index'))