from flask import jsonify


def get_message(message, http_code):
    return jsonify(message), http_code
