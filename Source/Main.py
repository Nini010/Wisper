from flask import Flask, render_template

app=Flask(__name__) 

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

@app.route('/signin')
def signin():
    return render_template('SignIn.html')

@app.route('/addpost')
def addPost():
    return "This is the Add Post page (placeholder)."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)