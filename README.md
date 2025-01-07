### README for DatabaseClient

## Overview

The goal of this project was to create a Python library called `DatabaseClient.py`, which simplifies interactions with various relational databases (e.g., SQLite, MariaDB, PostgreSQL). This project was designed to provide deeper insights into the topic of databases and enhance expertise in this area.

## Supported Databases

- **SQLite**
- **MariaDB**
- **PostgreSQL**

## Features

- **Database Connection**: Establish connections with SQLite, MariaDB, or PostgreSQL databases.
- **Table Management**: Create, drop, and alter tables.
- **Data Insertion**: Insert single or multiple rows into tables.
- **Data Retrieval**: Fetch data from tables with optional conditions.
- **Data Modification**: Update or delete rows based on conditions.
- **Transaction Management**: Support for beginning, committing, and rolling back transactions.
- **Index Management**: Create and drop indexes on tables.
- **User Management**: Create, delete, and manage users and their permissions.
- **Backup and Restore**: Backup the entire database or restore from a backup file.
- **CSV Export/Import**: Export table data to CSV files and import data from CSV files.
- **Audit Logging**: Log actions performed within the database.

## Installation

```bash
pip install mariadb psycopg2
```

Make sure to install the appropriate drivers for the databases you plan to use:
- For **SQLite**, no additional installation is required as it is included with Python.
- For **MariaDB**, install `mariadb` using `pip`.
- For **PostgreSQL**, install `psycopg2` using `pip`.

## Usage

### 1. Creating a DatabaseClient Instance

```python
from database_client import DatabaseClient

# SQLite example
db = DatabaseClient(db_type='sqlite', database='example.db')

# MariaDB example
db = DatabaseClient(
    db_type='mariadb',
    host='localhost',
    port=3306,
    database='example',
    user='root',
    password='password'
)

# PostgreSQL example
db = DatabaseClient(
    db_type='postgresql',
    host='localhost',
    port=5432,
    database='example',
    user='postgres',
    password='password'
)
```

### 2. Creating a Table

```python
db.create_table(
    "users",
    [
        ("id", "INT PRIMARY KEY AUTO_INCREMENT"),
        ("username", "VARCHAR(255)"),
        ("password", "VARCHAR(255)"),
        ("role", "VARCHAR(50)")
    ]
)
```

### 3. Inserting Data

```python
db.insert(
    "users",
    ["username", "password", "role"],
    ("john_doe", "hashed_password", "admin")
)
```

### 4. Fetching Data

```python
users = db.fetch(
    "users",
    ["id", "username", "role"],
    "role = %s",
    ("admin",)
)
```

### 5. Managing Users and Permissions

```python
# Creating a new user
db.create_user("users", "alice", "securepassword", "user")

# Setting a new password
db.set_password("users", "alice", "new_secure_password")

# Verifying password
is_valid = db.verify_password("users", "alice", "new_secure_password")

# Granting permissions
db.grant_permission("permissions", "alice", "read")

# Revoking permissions
db.revoke_permission("permissions", "alice", "write")

# Fetching user permissions
permissions = db.get_permissions("permissions", "alice")
```

### 6. Backup and Restore

```python
# Backup the database
db.backup_database("backup.sql")

# Restore the database
db.restore_database("backup.sql")
```

### 7. CSV Export and Import

```python
# Export table to CSV
db.export_to_csv("users", "users.csv")

# Import data from CSV
db.import_from_csv("users", "users.csv")
```

### 8. Logging Actions

```python
# Log an action
db.log_action("audit_log", "INSERT", "Inserted a new user into users table")

# Retrieve audit log
logs = db.get_audit_log("audit_log")
```

## Example

```python
if __name__ == "__main__":
    # Create an instance of the DatabaseClient
    db = DatabaseClient(db_type='mariadb', host='localhost', port=3306, database='example', user='root', password='password')
    
    # Create tables
    db.create_table("users", [("id", "INT AUTO_INCREMENT PRIMARY KEY"), ("username", "VARCHAR(255)"), ("password", "VARCHAR(255)"), ("role", "VARCHAR(255)")])
    db.create_table("roles", [("role", "VARCHAR(255) PRIMARY KEY"), ("description", "TEXT")])
    db.create_table("permissions", [("id", "INT AUTO_INCREMENT PRIMARY KEY"), ("username", "VARCHAR(255)"), ("permission", "VARCHAR(255)")])
    
    # Manage roles
    db.create_roles("roles")
    
    # Manage users
    db.create_user("users", "alice", "securepassword", "admin")
    db.set_password("users", "alice", "newsecurepassword")
    print(db.verify_password("users", "alice", "newsecurepassword"))
    db.delete_user("users", "alice")
    
    # Manage permissions
    db.create_user("users", "bob", "securepassword", "user")
    db.grant_permission("permissions", "bob", "read")
    db.revoke_permission("permissions", "bob", "write")
    print(db.get_permissions("permissions", "bob"))
    
    # Logging
    db.create_table("audit_log", [("id", "INT AUTO_INCREMENT PRIMARY KEY"), ("action", "VARCHAR(255)"), ("details", "TEXT")])
    db.log_action("audit_log", "INSERT", "Inserted a new record in users table")
    print(db.get_audit_log("audit_log"))
    
    # Export/Import data
    db.create_table("data_table", [("id", "INT AUTO_INCREMENT PRIMARY KEY"), ("name", "VARCHAR(255)"), ("value", "INT")])
    db.batch_insert("data_table", ["name", "value"], [("item1", 10), ("item2", 20)])
    db.export_to_csv("data_table", "data_table.csv")
    db.clear_table("data_table")
    db.import_from_csv("data_table", "data_table.csv")
    
    print(db.fetch("data_table", ["id", "name", "value"]))
```

## License

This project is licensed under the MIT License.

---

This README file provides comprehensive instructions on how to use the `DatabaseClient` class for managing relational databases. It covers basic usage, advanced features, and includes example code for common tasks.
