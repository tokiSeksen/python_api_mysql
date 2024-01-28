import logging

from database_operations import fetch_one, get_cursor, insert_data
from flask_bcrypt import generate_password_hash
from errors import get_message


class User:
    def __init__(self, id, username, password, subscription_type, created_at):
        self.id = id
        self.username = username
        self.password = password
        self.subscription_type = subscription_type
        self.created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None


def create_user(data, mysql):
    username = data.get('username')
    password = data.get('password')
    subscription_type = data.get('subscription_type')

    cursor = get_cursor(mysql)

    try:
        result_from_database = get_user_from_database(data, mysql)
    except Exception as e:
        return get_message(f'Error querying database {e}', 500)

    if result_from_database:
        cursor.close()
        return get_message({'message': 'Username already exists'}, 400)
    query_create_user = "INSERT INTO users (username, password, subscription_type) VALUES (%s, %s, %s)"

    hashed_password = generate_password_hash(password)

    try:
        insert_data(mysql, query_create_user, (username, hashed_password, subscription_type))
    except Exception as e:
        return get_message(f'Error querying database {e}', 500)

    return get_message( {'message': 'User registered successfully'}, 200)


def get_user_from_database(data, mysql):
    username = data.get('username')
    query_get_user = f"SELECT * FROM users WHERE username = '{username}'"

    logging.info(f"In get_user_from_database executing {query_get_user}")

    return fetch_one(mysql, query_get_user)


def get_user_dict(user_from_database):
    user_instance = User(*user_from_database)
    result_dict = user_instance.__dict__

    return result_dict


