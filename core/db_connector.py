import psycopg2
from typing import List, Tuple, Dict

class DatabaseConnector:
    def __init__(self, db_info: Dict[str, str]):
        self.connection = self._connect_to_db(db_info)
        self.cursor = self.connection.cursor()

    def _connect_to_db(self, db_info: Dict[str, str]):
        """
        Establishes a connection to the PostgreSQL database.

        Args:
        - db_info (Dict[str, str]): Dictionary containing database connection details.

        Returns:
        - Connection object.
        """
        return psycopg2.connect(
            host=db_info["host"],
            port=db_info["port"],
            user=db_info["username"],
            password=db_info["password"],
            dbname=db_info["dbname"]
        )

    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Executes a SQL query on the database.

        Args:
        - query (str): The SQL query to execute.
        - params (Tuple): Parameters for the query if it's a parametrized query.

        Returns:
        - List[Tuple]: Result of the query.
        """
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        """
        Closes the cursor and the connection to the database.
        """
        self.cursor.close()
        self.connection.close()
