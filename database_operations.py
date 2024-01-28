import logging


def get_cursor(mysql):
    return mysql.connection.cursor()


def execute_query(mysql, query, params=None):
    cursor = get_cursor(mysql)
    if params:
        logging.info(f"Params are {params}, executing query ....")
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor


def fetch_one(mysql, query, params=None):
    logging.info(f"Executing query {query} with params {params}")
    cursor = execute_query(mysql, query, params)
    result = cursor.fetchone()
    logging.info(f"Result from database {result}")
    cursor.close()
    return result


def fetch_all(mysql, query, params=None):
    logging.info(f"Executing query {query} with params {params}")
    cursor = execute_query(mysql, query, params)
    result = cursor.fetchall()
    cursor.close()
    return result


def insert_data(mysql, query, params=None):
    cursor = execute_query(mysql, query, params)
    mysql.connection.commit()
    cursor.close()






