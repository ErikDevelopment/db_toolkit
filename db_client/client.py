import sqlite3
import mariadb
import psycopg2
from typing import List, Tuple, Any
import csv
import hashlib


class DatabaseClient:
    def __init__(self, db_type: str, host: str = '', port: int = 0, database: str = '', user: str = '',
                 password: str = ''):
        self.db_type = db_type
        self.conn = None
        self.cursor = None

        if db_type == 'sqlite':
            self.conn = sqlite3.connect(database)
            self.cursor = self.conn.cursor()
        elif db_type == 'mariadb':
            self.conn = mariadb.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
        elif db_type == 'postgresql':
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
        else:
            raise ValueError("Unsupported database type. Supported types are 'sqlite', 'mariadb', and 'postgresql'.")

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]):
        columns_str = ", ".join([f"{col} {dtype}" for col, dtype in columns])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name: str, columns: List[str], values: Tuple):
        placeholders = ", ".join(["%s" for _ in values])
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def batch_insert(self, table_name: str, columns: List[str], values_list: List[Tuple]):
        placeholders = ", ".join(["%s" for _ in columns])
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        self.cursor.executemany(query, values_list)
        self.conn.commit()

    def remove(self, table_name: str, condition: str, condition_value: Tuple):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, condition_value)
        self.conn.commit()

    def update(self, table_name: str, updates: str, condition: str, values: Tuple):
        query = f"UPDATE {table_name} SET {updates} WHERE {condition}"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch(self, table_name: str, columns: List[str], condition: str = "", condition_value: Tuple = ()):
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query, condition_value)
        return self.cursor.fetchall()

    def add_value(self, table_name: str, column: str, amount: int, condition: str, condition_value: Tuple):
        query = f"UPDATE {table_name} SET {column} = {column} + %s WHERE {condition}"
        self.cursor.execute(query, (amount,) + condition_value)
        self.conn.commit()

    def subtract_value(self, table_name: str, column: str, amount: int, condition: str, condition_value: Tuple):
        query = f"UPDATE {table_name} SET {column} = {column} - %s WHERE {condition}"
        self.cursor.execute(query, (amount,) + condition_value)
        self.conn.commit()

    def is_field_empty(self, table_name: str, column: str, condition: str, condition_value: Tuple) -> bool:
        query = f"SELECT {column} FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, condition_value)
        result = self.cursor.fetchone()
        return result is None or result[0] is None or result[0] == ''

    def begin_transaction(self):
        self.conn.autocommit = False

    def commit_transaction(self):
        self.conn.commit()

    def rollback_transaction(self):
        self.conn.rollback()

    def drop_table(self, table_name: str):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(query)
        self.conn.commit()

    def clear_table(self, table_name: str):
        query = f"DELETE FROM {table_name}"
        self.cursor.execute(query)
        self.conn.commit()

    def create_index(self, index_name: str, table_name: str, columns: List[str]):
        columns_str = ", ".join(columns)
        query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def drop_index(self, index_name: str):
        query = f"DROP INDEX IF EXISTS {index_name}"
        self.cursor.execute(query)
        self.conn.commit()

    def alter_table_add_column(self, table_name: str, column: str, dtype: str):
        query = f"ALTER TABLE {table_name} ADD COLUMN {column} {dtype}"
        self.cursor.execute(query)
        self.conn.commit()

    def table_exists(self, table_name: str) -> bool:
        query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s"
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchone()[0] > 0

    def column_exists(self, table_name: str, column_name: str) -> bool:
        query = "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = %s AND column_name = %s"
        self.cursor.execute(query, (table_name, column_name))
        return self.cursor.fetchone()[0] > 0

    def list_tables(self) -> List[str]:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def list_columns(self, table_name: str) -> List[str]:
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
        self.cursor.execute(query, (table_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def count_rows(self, table_name: str, condition: str = "", condition_value: Tuple = ()) -> int:
        query = f"SELECT COUNT(*) FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query, condition_value)
        return self.cursor.fetchone()[0]

    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple[Any]]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def backup_database(self, backup_path: str):
        with open(backup_path, 'wb') as f:
            for chunk in self.conn.iterdump():
                f.write(f"{chunk}\n".encode())

    def restore_database(self, backup_path: str):
        with open(backup_path, 'r') as f:
            sql = f.read()
        self.cursor.executescript(sql)
        self.conn.commit()

    def export_to_csv(self, table_name: str, csv_path: str):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]

        with open(csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(columns)
            csv_writer.writerows(rows)

    def import_from_csv(self, table_name: str, csv_path: str):
        with open(csv_path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            columns = next(csv_reader)
            rows = [tuple(row) for row in csv_reader]

        placeholders = ", ".join(["%s" for _ in columns])
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        self.cursor.executemany(query, rows)
        self.conn.commit()

    def create_user(self, table_name: str, username: str, password: str, role: str):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.insert(table_name, ["username", "password", "role"], (username, password_hash, role))

    def delete_user(self, table_name: str, username: str):
        self.remove(table_name, "username = %s", (username,))

    def set_password(self, table_name: str, username: str, new_password: str):
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        self.update(table_name, "password = %s", "username = %s", (new_password_hash, username))

    def verify_password(self, table_name: str, username: str, password: str) -> bool:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = f"SELECT password FROM {table_name} WHERE username = %s"
        self.cursor.execute(query, (username,))
        stored_password_hash = self.cursor.fetchone()
        return stored_password_hash is not None and stored_password_hash[0] == password_hash

    def grant_permission(self, table_name: str, username: str, permission: str):
        self.insert(table_name, ["username", "permission"], (username, permission))

    def revoke_permission(self, table_name: str, username: str, permission: str):
        self.remove(table_name, "username = %s AND permission = %s", (username, permission))

    def get_permissions(self, table_name: str, username: str) -> List[str]:
        result = self.fetch(table_name, ["permission"], "username = %s", (username,))
        return [row[0] for row in result]

    def log_action(self, table_name: str, action: str, details: str):
        self.insert(table_name, ["action", "details"], (action, details))

    def get_audit_log(self, table_name: str) -> List[Tuple[str, str]]:
        return self.fetch(table_name, ["action", "details"])

    def create_roles(self, table_name: str):
        roles = [
            ("admin", "Administrator with full access"),
            ("user", "Regular user with limited access"),
            ("remote", "Remote user with specific permissions"),
            ("localhost", "Local user with specific permissions")
        ]
        self.batch_insert(table_name, ["role", "description"], roles)

    def __del__(self):
        if self.conn:
            self.conn.close()



