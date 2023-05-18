from flask import Flask, \
                    render_template, \
                    send_from_directory, \
                    make_response, \
                    request, \
                    session, \
                    redirect
import pyrebase

config = {
    "apiKey": "AIzaSyCaqYs040k4sD_NrjkCSx2IztVyomfufm8",
    "authDomain": "rent-my-gear.firebaseapp.com",
    "projectId": "rent-my-gear",
    "storageBucket": "rent-my-gear.appspot.com",
    "messagingSenderId": "892030622526",
    "appId": "1:892030622526:web:df3b160d8cac60843caa6f",
    "measurementId": "G-N85D9ZV8WX",
    "databaseURL": ""
}

app = Flask(__name__)

app.secret_key = 'secret'

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template('home.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'user' in session:
        return f"Hi, {session['user']}"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(username, password)
            session['user'] = username
        except:
            return 'Failed to login'
    return render_template('login.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if 'account_created' in session:
        return "Account created."
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            auth.create_user_with_email_and_password(username, password)
            session['account_created'] = True
        except:
            return 'Failed to register'
    return render_template('register.html')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/')


@app.route('/manifest.json')
def manifest():
    return send_from_directory(".", "manifest.json")


@app.route('/images/logo192.png')
def logo192():
    return send_from_directory("images", "logo192.png")


@app.route('/images/logo512.png')
def logo512():
    return send_from_directory("images", "logo512.png")


@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=9999)
