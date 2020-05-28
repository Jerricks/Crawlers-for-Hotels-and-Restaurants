#!/usr/bin/python
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def main():
    # Connect to the DB
    collection1 = MongoClient('127.0.0.1',27017)["proDB"]["registeredUsers"]
    #  collection1 = MongoClient('35.154.116.6', 27017)["proDB"]["registeredUsers"]

    # Ask for data to store
    user = "cradmin"
    password = "cradmin"

    pass_hash = generate_password_hash(password, method='pbkdf2:sha256')

    # Insert the user in the DB
    try:
        collection1.insert({"_id": user, "username": user, "password": pass_hash, "role": "adminCrawler", "status": "true"})
        print("User created.")
    except DuplicateKeyError:
        print("User already present in DB.")


if __name__ == '__main__':
    main()