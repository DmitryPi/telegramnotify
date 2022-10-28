import logging
import sqlite3

from .utils import handle_error, load_config


class Database:
    def __init__(self):
        self.config = load_config()
        self.sql_create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                uid integer PRIMARY KEY,
                username text NOT NULL,
                first_name text NOT NULL,
                full_name text NOT NULL,
                phone_num int NOT NULL,
                role text NOT NULL,
                created text NOT NULL,
                updated text NOT NULL
            );"""

    def create_connection(self, db_file="db.sqlite3"):
        """Connect to db/Create `db.sqlite3` in root folder if not exist"""
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            logging.info("Connected to db\n")
        except Exception as e:
            handle_error(e)
        return conn

    def create_table(self, conn, sql=""):
        """Create project table from `self.sql_create_project_table`
        Optional `sql` kwarg if you want to create new table
        """
        try:
            sql = sql if sql else self.sql_create_project_table
            cur = conn.cursor()
            cur.execute(sql)
            return True
        except Exception as e:
            handle_error(e)

    def insert_object(self, conn, table: str, fields: tuple, values: tuple):
        try:
            cur = conn.cursor()
            cur.execute(f"INSERT OR IGNORE INTO {table} {fields} VALUES {values}")
            conn.commit()
        except Exception as e:
            handle_error(e)

    def update_object(self, conn, table: str, column: str, field: str, values: tuple):
        """Update table object, filtered by field value
        update_object(db_conn, db_table, 'test_text', 'test_bool', ('changed', 1)
        - Objects with test_bool=True will have test_text=changed"""
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE {table} SET {column}=? WHERE {field}=?", values)
            conn.commit()
        except Exception as e:
            handle_error(e)

    def delete_object(self, conn, table: str, field: str, value):
        """Delete table object"""
        try:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table} WHERE {field}={value}")
            conn.commit()
        except Exception as e:
            handle_error(e)

    def get_objects_all(self, conn, table: str) -> list:
        """Return queryset of table objects"""
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            return cur.fetchall()
        except Exception as e:
            handle_error(e)

    def get_objects_filter_by_value(self, conn, table: str, column: str, value) -> list:
        """Filter db table by column value"""
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table} WHERE {column}=?", (value,))
            return cur.fetchall()
        except Exception as e:
            handle_error(e)

    def get_objects_field_values(self, conn, table: str, column: str) -> list:
        """Select column values from table"""
        try:
            conn.row_factory = lambda cursor, row: row[0]
            cur = conn.cursor()
            cur.execute(f"SELECT {column} FROM {table}")
            return cur.fetchall()
        except Exception as e:
            handle_error(e)
