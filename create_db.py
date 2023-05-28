import pyrebase
import yaml
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, db
from pathlib import Path
import os


def delete_all_users():
    # Iterate through all users. This will still retrieve users in batches,
    # buffering no more than 1000 users in memory at a time.
    for user in auth.list_users().iterate_all():
        auth.delete_user(user.uid)


def create_users():
    for i in range(10):
        # create user ids from 000 to 100
        user_id = f'{i:03d}'

        # initialize personal details
        email = 'user' + user_id + '@gmail.com'
        phone_number = '+15555550' + user_id
        display_name = 'John ' + user_id 
        auth.create_user(
                    email=email,
                    email_verified=False,
                    phone_number=phone_number,
                    password='123456',
                    display_name=display_name,
                    disabled=False)

    

def reset_database_content():
    with open("firebase_config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    firebase = pyrebase.initialize_app(config)

    db = firebase.database()
    db.child("items").remove()

    for i in range(10):
        user_id = f'{i:03d}'
        email = 'user' + user_id + '@gmail.com'
        title = 'skis for rent ' + user_id
        description = 'These are very good skis' + user_id
        price = 100 + i
        category = 'ski'

        user_dirpath = Path(os.path.join('static/uploads', email, title))
        user_dirpath.mkdir(parents=True, exist_ok=True)

        save_path = os.path.join(str(user_dirpath), file)
        item = {
                'title': title,
                'description': description,
                'price': price,
                'category': category,
                'user': email,
                'images': urls
            }
        db.child("items").push(item)
        


def main():
    cred = credentials.Certificate("rent-my-gear-firebase-adminsdk-chvwl-c28c1be607.json")
    firebase_admin.initialize_app(cred, 
                                  {"databaseURL": "https://rent-my-gear-default-rtdb.europe-west1.firebasedatabase.app/"})

    delete_all_users()  
    create_users()  

    # reset_database_content()


if __name__ == '__main__':
    main()
