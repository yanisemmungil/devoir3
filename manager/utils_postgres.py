try: 
    from psycopg2 import connect
    from psycopg2.errors import DuplicateTable, DatabaseError
except:
    pass

def connect_to_db_server(user, password, 
    database, host="db", port="5432"):
    """ Connect to database server with provided environment variables """
    try:
        connection = connect(
                user=user,
                password=password,
                database=database,
                host=host,
                port=port)
        cursor = connection.cursor()
        print("Successfully connected to Postgres Server\n")
        return connection
    except Exception as e:
        print(f"could not connect to the postgres {e}\n")
        return None

def create_new_table(connection):
    """ Create a new table in the default db"""

    query = """ CREATE TABLE persons ( 
                    id SERIAL, 
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    PRIMARY KEY (id)
                    ) """
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        print("Created table successfully\n")
    except DuplicateTable as e:
        print("The table already exist, skipping.\n")
        connection.rollback()
    except (Exception, DatabaseError) as e:
        print(e)
        connection.rollback()

def csv_to_table(connection, table, data_path):
    """ Load csv file (without header) to postgres table when formats match """
    try:
        cursor = connection.cursor()
        with open(data_path, 'r') as f:
            header = f.readline().rstrip("\n").split(',')
            cursor.copy_from(f, table, sep=",", 
                columns=header)
        connection.commit()
        print("Added the CSV successfully !")
    except (Exception, DatabaseError) as error:
        print(error)
        connection.rollback()

### for testing ###
def table_to_csv(connection, table, output_file):
    """ Retrieve data from the Postgres table and store it in CSV """
    import csv
    try:
        cursor = connection.cursor()
        cursor.execute(f"select * from {table} limit 0 ;")
        id_col, *colnames = [desc[0] for desc in cursor.description]
        cursor.execute(f"select * from {table} ;")
        records_without_id = []
        for id_, *rest in cursor.fetchall():
            records_without_id.append(rest)
        with open(output_file, 'w') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            writer.writerow(colnames)
            writer.writerows(records_without_id)
    except (Exception, DatabaseError) as error:
        print(error)

def csv_to_tuples(file_path):
    """ Read csv file and return list of tuples """
    import csv
    with open(file_path, 'r') as f:
        data=[tuple(line) for line in csv.reader(f)]
    return data

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    import platform    # For getting the operating system name
    import subprocess  # For executing a shell command
    
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0