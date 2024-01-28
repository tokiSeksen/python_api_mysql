import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token, get_jwt
from flask_mysqldb import MySQL
from flask_bcrypt import generate_password_hash, check_password_hash
import secrets
import logging
from user_operations import create_user, get_user_from_database, get_user_dict
from auth import check_password, get_data_from_jwt
from errors import get_message
from link_operations import get_links_from_database, create_link_for_api, get_links_for_api, \
    get_link_for_api, update_link_for_api, delete_link_for_api

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
logging.basicConfig(level=logging.DEBUG)

# Configuration for MySQL
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'db')

mysql = MySQL(app)
jwt = JWTManager(app)


###########################################################
# USER API#
###########################################################

@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    result = create_user(data, mysql)
    return result


# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')
    app.logger.info(f"In login ...")

    user_from_database = get_user_from_database(data, mysql)
    app.logger.info(f"In login user_from_database {user_from_database}")

    if user_from_database:
        user_dict = get_user_dict(user_from_database)
        hashed_password = user_dict['password']
        return check_password(hashed_password, password, user_dict)
    else:
        return get_message('Invalid credentials', 400)


###########################################################
# LINK API#
###########################################################

class Link:
    def __init__(self, id, username, destination_url, title, created_at):
        self.id = id
        self.username = username
        self.destination_url = destination_url
        self.title = title
        self.created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None


@app.route('/links', methods=['POST'])
@jwt_required()
def create_link():
    current_username = get_data_from_jwt(app, 'username')
    if current_username:
        links = get_links_from_database(mysql, current_username)
        app.logger.info(f"User has {len(links)}")

        if len(links) >= 10 and get_data_from_jwt(app, 'subscription_type') == 'free':
            return get_message({'error': 'You can not have more thant 10 subscriptions with free subscription type'},
                               403)
        data = request.json
        return create_link_for_api(mysql, data, current_username)

    return get_message({'error': 'User does not exist'}, 400)


@app.route('/links', methods=['GET'])
@jwt_required()
def get_links():
    current_username = get_data_from_jwt(app, 'username')

    if current_username:
        links = get_links_for_api(mysql, current_username)
        return links

    return get_message({'error': 'User does not exist'}, 400)


@app.route('/links/<int:link_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_link(link_id):
    current_username = get_data_from_jwt(app, 'username')
    if current_username:
        if request.method == 'GET':
            link_result = get_link_for_api(mysql, current_username, link_id)
            return link_result

        elif request.method == 'PUT':
            data = request.json
            result = update_link_for_api(mysql, current_username, data, link_id)
            return result

        elif request.method == 'DELETE':
            result = delete_link_for_api(mysql, current_username, link_id)
            return result
    else:
        get_message({'error': 'User does not exist'}, 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
