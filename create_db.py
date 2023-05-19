import pyrebase
import yaml
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, db


def delete_all_users():
    # Iterate through all users. This will still retrieve users in batches,
    # buffering no more than 1000 users in memory at a time.
    for user in auth.list_users().iterate_all():
        auth.delete_user(user.uid)


def create_users():
    auth.create_user(
                email='user1@gmail.com',
                email_verified=False,
                phone_number='+15555550100',
                password='secretPassword',
                display_name='John Unu',
                disabled=False)
    auth.create_user(
                email='user2@gmail.com',
                email_verified=False,
                phone_number='+15555550101',
                password='secretPassword',
                display_name='John Doi',
                disabled=False)
    auth.create_user(
                email='user3@gmail.com',
                email_verified=False,
                phone_number='+15555550102',
                password='secretPassword',
                display_name='John Trei',
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

    to_push_list = [{"category": "winter sports", "user": "user1@gmail.com", "price": "100", "title": "skis to rent 177cm", "description": "skis in best condition for tall people"},
                    {"category": "bikes", "user": "user1@gmail.com", "price": "200", "title": "mtb 56cm", "description": "mtb to rent"}]
    
    for item in to_push_list:
        db.child("items").push(item)
    
    results = db.child("items").get().val()
    print(results)


def main():
    cred = credentials.Certificate("rent-my-gear-firebase-adminsdk-chvwl-c28c1be607.json")
    firebase_admin.initialize_app(cred, 
                                  {"databaseURL": "https://rent-my-gear-default-rtdb.europe-west1.firebasedatabase.app/"})

    delete_all_users()  
    create_users()  

    reset_database_content()


if __name__ == '__main__':
    main()
