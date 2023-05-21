from flask import Flask, \
                    render_template, \
                    send_from_directory, \
                    make_response, \
                    request, \
                    session, \
                    redirect
import os
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
app.config['UPLOAD_FOLDER'] = "static/uploads"

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def home():
    if 'user' not in session:
        user = auth.sign_in_anonymous()
        session['anonymous_user'] = user
    return render_template('home.html', page='home')


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
            return redirect('/settings')
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
            return render_template('registration_success.html')
        except:
            return 'Failed to register'
    return render_template('register.html')


@app.route("/delete_account")
def delete_account():
    if 'user' in session:
        try:
            user = session['user']
            auth.delete_user_account(user['idToken'])
        except:
            return 'Failed to delete account'
    return redirect('/settings')


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


@app.route("/search")
def search():
    return render_template("search.html", page="search")


@app.route("/item_added", methods=['POST'])
def item_added():
    if request.method == 'POST':
  
        # Get the list of files from webpage
        files = request.files.getlist("file")
  
        # Iterate for each file in the files List, and Save them
        filenames = []
        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            filenames.append(file.filename)
        return str(filenames) + "<h1>Files Uploaded Successfully.!</h1>"
    return 'not received'


@app.route("/add_item", methods=['POST', 'GET'])
def add_item():
    return render_template("add_item.html", page="add_item")


@app.route("/settings")
def settings():
    if 'user' in session:
        return render_template("settings.html", page="settings", logged_in=True, email=session['user']['email'])
    else:
        return render_template("settings.html", page="settings", logged_in=False)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/settings')


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
