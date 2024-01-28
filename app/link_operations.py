from database_operations import fetch_one, insert_data, fetch_all
from errors import get_message
import logging
from flask import jsonify


class Link:
    def __init__(self, id, username, destination_url, title, created_at):
        self.id = id
        self.username = username
        self.destination_url = destination_url
        self.title = title
        self.created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None


def get_links_from_database(mysql, current_username):
    query = f"SELECT * FROM links WHERE username = '{current_username}'"
    links_from_db = fetch_all(mysql, query)

    return links_from_db


def get_link_from_database(mysql, link_id):
    query = f"SELECT * FROM links WHERE id = '{link_id}'"
    link_from_db = fetch_one(mysql, query)

    return link_from_db


def create_link_for_api(mysql, data, current_username):
    query = "INSERT INTO links (username, destination_url, title) VALUES (%s, %s, %s)"
    destination_url = data.get('destination_url')
    title = data.get('title')
    try:
        insert_data(mysql, query, (current_username, destination_url, title))
    except Exception as e:
        return get_message(f'Error querying database {e}', 500)

    return get_message({'message': 'Link created successfully'}, 201)


def get_links_for_api(mysql, current_username):
    links = get_links_from_database(mysql, current_username)
    links_list = []
    for link in links:
        result_dict = get_dict_for_link_instance(link)
        links_list.append(result_dict)

    logging.info(f"this is links_list {links_list}")

    result = jsonify(links_list)
    logging.info(f"These are the links {result}")
    return result, 200


def get_link_for_api(mysql, current_username, link_id):
    link_from_db = get_link_from_database(mysql, link_id)

    if link_from_db:
        result_dict = get_dict_for_link_instance(link_from_db)

        if result_dict['username'] == current_username:
            link_result_json = jsonify(result_dict).get_json()
            return link_result_json, 200
        else:
            return get_message({'error': 'You can not access this link'}, 403)
    else:
        return get_message({'error': 'Link does not exist'}, 404)


def update_link_for_api(mysql, current_username, data, link_id):
    destination_url = data['destination_url'],
    title = data.get('title', None)

    link_from_db = get_link_from_database(mysql, link_id)

    if link_from_db:
        result_dict = get_dict_for_link_instance(link_from_db)
        if result_dict['username'] == current_username:
            query = "UPDATE links SET destination_url = %s, title = %s WHERE id = %s"
            insert_data(mysql, query, (destination_url, title, link_id))
            return get_message({'message': 'Link updated successfully'}, 200)
        else:
            return get_message({'error': 'You can not update this link'}, 403)
    return get_message({'error': 'Link does not exist'}, 404)


def delete_link_for_api(mysql, current_username, link_id):
    link_from_db = get_link_from_database(mysql, link_id)
    if link_from_db:
        result_dict = get_dict_for_link_instance(link_from_db)
        if result_dict['username'] == current_username:
            query = f"DELETE FROM links WHERE id = '{link_id}'"
            insert_data(mysql, query)
            return get_message({'message': 'Link deleted successfully'}, 200)
        else:
            return get_message({'error': 'You can not delete this link'}, 403)
    return get_message({'error': 'Link does not exist'}, 404)


def get_dict_for_link_instance(link_from_db):
    link_instance = Link(*link_from_db)
    result_dict = link_instance.__dict__

    return result_dict


