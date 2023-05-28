from flask import Flask, \
                    render_template, \
                    send_from_directory, \
                    make_response, \
                    request, \
                    session, \
                    redirect
import os
from pathlib import Path
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
db = firebase.database()
storage = firebase.storage()


@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def home():
    if 'user' not in session:
        user = auth.sign_in_anonymous()
        session['anonymous_user'] = user
    items = db.child("items").get().val()

    # Check if the dict is None to avoid errors in jinja
    if items is None:
        items = {}

    return render_template('home.html', page='home', items=items)


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
    return render_template('login.html', page="settings")


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
    return render_template('register.html', page="settings")


@app.route("/delete_account")
def delete_account():
    if 'user' in session:
        try:
            user = session['user']
            auth.delete_user_account(user['idToken'])

            # Delete the items of the user
            items = db.child("items").get().val()
            for key, item in items.items():
                if item['user'] == user['email']:
                    db.child("items").child(key).remove()

            # Remove user from the current session
            session.pop('user', None)

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
    

@app.route("/item_details/<key>")
def item_details(key):
    item = db.child("items").child(key).get().val()

    can_delete = False
    if 'user' in session:
        user = session['user']

        if item['user'] == user['email']:
            can_delete = True

    return render_template("item_details.html", page="home", item=item, can_delete=can_delete)


@app.route("/user_items")
def user_items():
    user = session['user']
    items = db.child("items").get().val()
    to_drop = []
    
    # Check if the dict is None to avoid errors in jinja
    if items is not None:
        for key, item in items.items():
            if item['user'] != user['email']:
                to_drop.append(key)

        for key in to_drop:
            items.pop(key)
    else:
        items = {}

    return render_template('user_items.html', page='settings', items=items)


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        category = request.form['category']
        try:
            items = db.child("items").get().val()
            to_drop = []
    
            # Check if the dict is None to avoid errors in jinja
            if items is not None:
                for key, item in items.items():
                    title_filter = search_query in str(item['title']).lower()
                    description_filter = search_query in str(item['description']).lower()
                    category_filter = category == item['category'] or category == 'any'
                    keep_condition = (title_filter or description_filter) and category_filter

                    if not keep_condition:
                        to_drop.append(key)

                for key in to_drop:
                    items.pop(key)
            else:
                items = {}
            return render_template('search_items.html', page='search', items=items)
        except:
            return 'Failed to search items'
    return render_template('search.html', page="search")


@app.route("/item_added", methods=['POST'])
def item_added():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
  
        # Get the list of files from webpage
        files = request.files.getlist("file")

        # Get user and create upload directory
        user = session['user']
        user_dirpath = Path(os.path.join(app.config['UPLOAD_FOLDER'], user['email'], title))
        user_dirpath.mkdir(parents=True, exist_ok=True)
  
        # Iterate for each file in the files List, and Save them
        urls = []
        for file in files:
            save_path = os.path.join(str(user_dirpath), file.filename)
            file.save(save_path)
            storage.child(save_path).put(save_path, user['idToken'])
            url = storage.child(save_path).get_url(user["idToken"])
            urls.append(url)

        item = {
            'title': title,
            'description': description,
            'price': price,
            'category': category,
            'user': user['email'],
            'images': urls
        }

        db.child("items").push(item)

        return redirect('/item_upload_success')
    return 'not received'


@app.route("/item_upload_success")
def item_upload_success():
    return render_template("item_upload_success.html")


@app.route("/add_item", methods=['POST', 'GET'])
def add_item():
    if 'user' in session:
        return render_template("add_item.html", page="add_item")
    else:
        return render_template("login_needed.html", page="add_item")


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
