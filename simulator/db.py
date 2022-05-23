import psycopg2
params = {
    "host"      : "database-1.cpwa86v6hjzb.ap-northeast-2.rds.amazonaws.com",
    "database"  : "postgres",
    "user"      : "postgres",
    "password"  : "hunter2022"
}


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return conn





