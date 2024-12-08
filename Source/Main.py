from flask import Flask, redirect, url_for, session, render_template, request, flash
from datetime import timedelta
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from authlib.integrations.flask_client import OAuth
import os
import sqlite3

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

app.secret_key = os.urandom(24)

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
print(os.getenv('FACEBOOK_CLIENT_ID'))
os.getenv('FACEBOOK_CLIENT_SECRET')


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
        
        # Connect to the database
        conn = sqlite3.connect("profile.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM profiles WHERE email = ? LIMIT 1;", (session['email'],))

        # Check if the email exists
        result = cursor.fetchone()

        if not result:
            cursor.execute("INSERT INTO profiles (email, username) VALUES (?, ?);", (session['email'], session['name']))
            conn.commit()
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
    
@app.route('/search')
def search():
    return render_template('Search.html')

@app.route('/edit')
def edit():
    return render_template('EditProfile.html')

@app.route('/addpost')
def addPost():
    return "This is the Add Post page (placeholder)."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('ssl.crt', 'ssl.key'))