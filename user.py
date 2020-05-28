from werkzeug.security import check_password_hash
from app import app, lm

class User():

    def __init__(self, username):
        self.username = username
        self.email = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"username": username})
        self.role = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"username": username})
        self.name = app.config['REGISTEREDUSERS_COLLECTION'].find_one({"username": username})

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
