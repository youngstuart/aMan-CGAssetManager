import mysql.connector
import json
import os

class DatabaseHandler:
    def __init__(self, database_file):
        self.config = self.get_config(database_file)
        self.conn = None
        self.cur = None

    def get_config(self, database_file: str) -> dict:
        """Looks for environment variable AMAN and searches for aMan.conf file containing the following lines:
        DATABASE=<database name>
        HOST=<ip or hostname of mysql server>
        USER=<mysql username>
        PASSWORD=<password>
        PORT=<msql server port>

        NOTE: Variable names are case sensitive

        Returns:
            dict: {
            database: str,
            host: str,
            user: str,
            password: str,
            port: str
            }
            - or NONE if error
        """
        config = {}

        with open(database_file, "r") as configFile:
            for line in configFile:
                var, value = [n.strip(' "\'\t\r\n') for n in line.split("=")]
                if var == "database":
                    config["database"] = value
                if var == "host":
                    config["host"] = value
                if var == "user":
                    config["user"] = value
                if var == "password":
                    config["password"] = value
                if var == "port":
                    config["port"] = value

        for var in ["database", "host", "user", "password", "port"]:
            if not var in config:
                print(f"Config Error: Variable {var} not found")
                return None
            if not config[var]:
                print(f"Config Error: Value for variable {var} is None")
                return None
            
        return config
    
    
    def __enter__(self):
        # context manager for opening connection
        self.conn = mysql.connector.connect(**self.config)
        self.cur = self.conn.cursor(buffered=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # context manager for closing connection
        self.close_connection()

    def execute_query(self, query, params=None):
        try:
            if params is None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, params)
            self.conn.commit()
            return 0
        except mysql.connector.IntegrityError as e:
            return e.errno
        
    def fetch_data(self, query, params=None):
        if params is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, params)
        return self.cur.fetchall()
    
    def get_last_insert_id(self):
        self.cur.execute("SELECT LAST_INSERT_ID()")
        return self.cur.fetchone()[0]

    def close_connection(self):
        self.cur.close()
        self.conn.close()

