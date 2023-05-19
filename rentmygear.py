from flask import Flask, \
                    render_template, \
                    send_from_directory, \
                    make_response, \
                    request, \
                    session, \
                    redirect
import pyrebase
import yaml


# Read the firebase info
with open("firebase_config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

app = Flask(__name__)
app.secret_key = 'secret'

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


@app.route("/", methods=['POST', 'GET'])
def home():
    if 'user' not in session:
        user = auth.sign_in_anonymous()
        session['anonymous_user'] = user
    return render_template('home.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'user' in session and 'anonymous' not in session:
        return f"Hi, {session['user']}"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user
        except:
            return 'Failed to login'
    return render_template('login.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.create_user_with_email_and_password(email, password)
            session['account_created'] = True
        except:
            return 'Failed to register'
    return render_template('register.html')


@app.route("/user")
def user():
    if 'user' in session:
        return session['user']
    elif 'anonymous_user' in session:
        return session['anonymous_user']
    else:
        return 'Error'


@app.route("/base")
def base():
    return render_template("base.html")


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
