from functions import *

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

create_tables()

@app.route('/')
def index():
    if(session.get('user') or session.get('email')):
        return redirect(url_for('chats'))
    
    return render_template('SignIn.html')

@app.route('/dm')
def DM():
    recipient_username = request.args.get('username')
    chats = get_chats(session['username'], recipient_username)
    return render_template('DMs.html', page='dm')

@app.route('/chats')
def chats():
    users = chats_list(session['username'])
    return render_template('chats.html', page='home', users=users)

@app.route('/settings')
def settings():
    return render_template('settings.html', page='set')
    
@app.route('/settings/edit')
def edit():
    return render_template('EditProfile.html', page='edit')

@app.route('/search')
def search():
    return render_template('Search.html', page='search')

@app.route('/profile')
def profile():
    return render_template('Profilepage.html', page='settings', name = session['name'], pfp = session['pfp'])

@app.route('/notification')
def notification():
    return render_template('notifications.html', page='notif')

@app.route('/profileinfo')
def profileinfo():
    return render_template('ProfileInfo.html', page='profileinfo')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('ssl.crt', 'ssl.key'))