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
    profile = get_profile((recipient_username,))
    return render_template('DMs.html', page='dm', name = profile[1], pfp = profile[0], username = recipient_username, my_username = session['username'], my_name = session['name'])

@app.route('/chats')
def chats():
    users = chats_list(session['username'])
    profile = get_profile((session['username'],))
    return render_template('chats.html', page='home', users=users, pfp=profile[0])

@app.route('/settings')
def settings():
    return render_template('settings.html', page='set')
    
@app.route('/edit')
def edit():
    return render_template('EditProfile.html', page='edit')

@app.route('/myprofile')
def myprofile():
    posts = get_posts(session['username'])
    return render_template('my-pfp.html', page='settings', name = session['name'], pfp = session['pfp'], posts = posts, num_of_posts = len(posts))

@app.route('/profile')
def profile():
    username = request.args.get('username')
    if username == session['username']:
        return redirect(url_for('myprofile'))
    else:
        profile = get_profile((username,))
        posts = get_posts(session['username'])
        return render_template('Profilepage.html', page = 'settings', name = profile[1], pfp = profile[0], posts = posts, num_of_posts = len(posts), username = username)

@app.route('/notification')
def notification():
    return render_template('notifications.html', page = 'notif')

@app.route('/profileinfo')
def profileinfo():
    return render_template('ProfileInfo.html', page = 'profileinfo')

# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True, ssl_context = ('ssl.crt', 'ssl.key'))