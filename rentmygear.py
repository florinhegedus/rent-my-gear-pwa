from flask import Flask, \
                    render_template, \
                    send_from_directory, \
                    make_response, \
                    request
import sys


app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        return f"username: {username}, password={password}"
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template("about.html")


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
