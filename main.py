from utils.file_manager import create_project_folder, write_file, read_file
from core.db_info_manager import save_db_info, load_db_info
import os

def main():
    # Step 1: Ask for project name
    project_name = input("Enter the name of your project: ")

    # Step 2: Check if project folder already exists
    project_path = os.path.join("projects", project_name)
    config_path = os.path.join(project_path, "db_config.json")

    if os.path.exists(project_path):
        print(f"Project '{project_name}' already exists.")
        
        # Step 3: Check for existing configuration
        if os.path.exists(config_path):
            print("Loading existing database configuration...")
            db_info = load_db_info(project_name)
        else:
            db_info = get_db_info_from_user()
            save_db_info(project_name, db_info)
    else:
        print(f"Creating project '{project_name}'...")
        create_project_folder(project_name)
        db_info = get_db_info_from_user()
        save_db_info(project_name, db_info)

    print("Database configuration is set!")
    # From here, you can continue with other functionalities like connecting to the DB, generating models, etc.

def get_db_info_from_user():
    """Prompt the user for database connection details."""
    print("Please provide database connection details:")
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

if __name__ == "__main__":
    main()
