import logging

from flask_bcrypt import generate_password_hash, check_password_hash
from flask import jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, decode_token, get_jwt


def check_password(hashed_password, password, user_dict):
    if check_password_hash(hashed_password, password):
        logging.info(f"hashed_password {hashed_password}, password {password}")
        access_token = create_access_token(identity=user_dict['id'],
                                           additional_claims={'username': user_dict['username'],
                                                              'subscription_type': user_dict['subscription_type']})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid credentials'), 401


def get_data_from_jwt(app, user_data):
    claims = get_jwt()
    app.logger.info(f"this is claims {claims}")
    data = claims[user_data]
    app.logger.info(f"Retrieving data from claims {data}")
    return data