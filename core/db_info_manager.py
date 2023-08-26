from typing import Dict
from utils.encryption_utils import decrypt_password, encrypt_password, load_key
from utils.file_manager import write_file, read_file, path_exists

DB_CONFIG_FILENAME = "db_config.txt"

def get_db_config_path(project_name: str) -> str:
    """
    Returns the path to the db_config file for a given project.

    Args:
    - project_name (str): The name of the user's project.

    Returns:
    - str: The path to the db_config file.
    """
    return f"projects/{project_name}/{DB_CONFIG_FILENAME}"

def save_db_info(project_name: str, db_info: Dict[str, str]) -> None:
    """
    Saves the database connection information to a file.

    Args:
    - project_name (str): The name of the user's project.
    - db_info (Dict[str, str]): A dictionary containing database connection information.
    """
    key = load_key()
    encrypted_password = encrypt_password(db_info["password"], key)
    db_info["password"] = encrypted_password

    content = '\n'.join([f"{key}={value}" for key, value in db_info.items()])
    write_file(get_db_config_path(project_name), content)

def load_db_info(project_name: str) -> Dict[str, str]:
    """
    Loads the database connection information from a file.

    Args:
    - project_name (str): The name of the user's project.

    Returns:
    - Dict[str, str]: A dictionary containing database connection information.
    """
    if not path_exists(get_db_config_path(project_name)):
        raise FileNotFoundError(f"Database configuration for project {project_name} not found!")

    content = read_file(get_db_config_path(project_name))
    lines = content.strip().split('\n')
    db_info = {}

    for line in lines:
        key, value = line.split('=')
        db_info[key] = value

    key = load_key()
    decrypted_password = decrypt_password(db_info["password"], key)
    db_info["password"] = decrypted_password
    
    return db_info
