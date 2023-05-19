import pyrebase
import yaml


with open("firebase_config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = 'test@gmail.com'
password = '123456'

# user = auth.create_user_with_email_and_password(email, password)
# print(user)

user = auth.sign_in_with_email_and_password(email, password)

# info = auth.get_account_info(user['idToken'])
# print(info)

# auth.send_email_verification(user['idToken'])

# auth.send_password_reset_email(email)

# Get a reference to the database service
db = firebase.database()
data1 = {"name": "geaca"}
data2 = {"name": "buti"}
results = db.child("items").push(data1)
results = db.child("items").push(data2)

results = db.child("items").get().val()
print(results)
