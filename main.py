from utils.file_manager import create_project_folder
from core.db_info_manager import save_db_info, load_db_info
import psycopg2
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

def prompt_for_project_name():
    while True:
        
        project_name = input("Please enter the project name: ").strip()
        project_path = os.path.join("projects", project_name)
        if os.path.exists(project_path):
            logging.info(f"A project with the name '{project_name}' already exists. Proceeding with this project.")
            return project_name, False
        else:
            logging.info(f"Project name '{project_name}' is available.")
            return project_name, True

def validate_db_connection(db_info):
    try:
        conn = psycopg2.connect(
            host=db_info['host'],
            port=db_info['port'],
            user=db_info['username'],
            password=db_info['password'],
            dbname=db_info['dbname']
        )
        conn.close()
        logging.info("Successfully connected to the database.")
        return True
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
        return False

def get_db_info_from_user():
    logging.info("Please provide database connection details:")
    host = input("Host: ")
    port = input("Port: ")
    username = input("Username: ")
    password = input("Password: ")
    dbname = input("Database name: ")

    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "dbname": dbname
    }

def main():
    project_name, is_new_project = prompt_for_project_name()
    project_path = os.path.join("projects", project_name)
    config_path = os.path.join(project_path, "db_config.json")

    if is_new_project:
        logging.info(f"Creating project '{project_name}'...")
        create_project_folder(project_name)
        db_info = get_db_info_from_user()
        if validate_db_connection(db_info):
            save_db_info(project_name, db_info)
        else:
            logging.warning("Failed to connect with the provided database configuration.")
    else:
        logging.info(f"Using existing project '{project_name}'...")
        if os.path.exists(config_path):
            logging.info("Loading existing database configuration...")
            db_info = load_db_info(project_name)
            if not validate_db_connection(db_info):
                logging.warning("Failed to connect with existing database configuration.")
                db_info = get_db_info_from_user()
                if validate_db_connection(db_info):
                    save_db_info(project_name, db_info)
        else:
            db_info = get_db_info_from_user()
            if validate_db_connection(db_info):
                save_db_info(project_name, db_info)
            else:
                logging.warning("Failed to connect with the provided database configuration.")

    logging.info("Database configuration is set!")
    # Step 3: Connect to the database and fetch metadata (tables, columns, primary keys, and foreign keys).
    # Step 4: Create directories like models, repositories, services, controllers, etc. (Refer to the generic_structure.json)
    # Step 5: Prompt user to for a table name to generate files. Validate the entered table name if exists. 

if __name__ == "__main__":
    main()
