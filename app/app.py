import os
from flask import Flask, request
from flask_jwt_extended import JWTManager, jwt_required
from flask_mysqldb import MySQL

import secrets
import logging
from user_operations import create_user, get_user_from_database, get_user_dict
from auth import check_password, get_data_from_jwt
from errors import get_message

import link_operations as link_operations

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
logging.basicConfig(level=logging.DEBUG)

# MYSLQ configuration
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'db')

mysql = MySQL(app)
jwt = JWTManager(app)


###### USER API ######


@app.route('/users', methods=['POST'])
def register_user():
    data = request.get_json()
    result = create_user(data, mysql)
    return result


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')

    user_from_database = get_user_from_database(data, mysql)
    app.logger.info(f"User logged in {user_from_database}")

    if user_from_database:
        user_dict = get_user_dict(user_from_database)
        hashed_password = user_dict['password']
        return check_password(hashed_password, password, user_dict)
    else:
        return get_message('Invalid credentials', 400)


###### LINK API ######

@app.route('/links', methods=['POST'])
@jwt_required()
def create_link():
    current_username = get_data_from_jwt(app, 'username')
    if current_username:
        links = link_operations.get_links_from_database(mysql, current_username)
        app.logger.info(f"User has {len(links)}")

        if len(links) >= 10 and get_data_from_jwt(app, 'subscription_type') == 'free':
            return get_message({'error': 'You can not have more thant 10 subscriptions with free subscription type'},
                               403)
        data = request.json
        return link_operations.create_link_for_api(mysql, data, current_username)

    return get_message({'error': 'User does not exist'}, 400)


@app.route('/links', methods=['GET'])
@jwt_required()
def get_links():
    current_username = get_data_from_jwt(app, 'username')

    if current_username:
        links = link_operations.get_links_for_api(mysql, current_username)
        return links

    return get_message({'error': 'User does not exist'}, 400)


@app.route('/links/<int:link_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_link(link_id):
    current_username = get_data_from_jwt(app, 'username')
    if current_username:
        if request.method == 'GET':
            link_result = link_operations.get_link_for_api(mysql, current_username, link_id)
            return link_result

        elif request.method == 'PUT':
            data = request.json
            result = link_operations.update_link_for_api(mysql, current_username, data, link_id)
            return result

        elif request.method == 'DELETE':
            result = link_operations.delete_link_for_api(mysql, current_username, link_id)
            return result
    else:
        get_message({'error': 'User does not exist'}, 404)


def handler(event, context):

    http_method = event['http_method']
    path = event['path']
    body = event.get('body', None)

    with app.request_context(path, method=http_method, data=body):
        if path == '/users' and http_method == 'POST':
            return register_user()
        elif path == '/users/login' and http_method == 'POST':
            return login()
        elif path == '/links' and http_method == 'POST':
            return create_link()
        elif path == '/link' and http_method == 'GET':
            return get_link()
        elif path.startswith('/links') and http_method in ['GET', 'PUT', 'DELETE']:
            link_id = int(path.split('/')[-1])
            return get_link(link_id)
        else:
            return {"statusCode": 400, "body": "Not Found"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
