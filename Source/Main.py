from flask import Flask, render_template

app=Flask(__name__) 

@app.route('/DM')
def DM():
    return render_template('DMs.html')

@app.route('/chats')
def chats():
    return render_template('chats.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)