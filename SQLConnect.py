

import psycopg2


def connect():
    # global connection, cursor, cursor2
    connection = psycopg2.connect(
        database="VLearn", user='postgres', password='superpost', host='127.0.0.1', port='5432'
    )
    connection.autocommit = True
    if connection is None:
        print('Connection not established to PostgreSQL.')

    cursor = connection.cursor()
    cursor2 = connection.cursor()
    return connection,cursor

def connect2():
    # global connection, cursor, cursor2
    connection2 = psycopg2.connect(
        database="VLearn", user='postgres', password='superpost', host='127.0.0.1', port='5432'
    )
    connection2.autocommit = True
    if connection2 is None:
        print('Connection not established to PostgreSQL.')

    cursor2 = connection2.cursor()
    return connection2,cursor2