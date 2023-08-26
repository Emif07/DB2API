from typing import Dict
import json
from utils.encryption_utils import decrypt_password, encrypt_password, load_key
from utils.file_manager import write_file, read_file, path_exists

DB_CONFIG_FILENAME = "db_config.json"


def get_db_config_path(project_name: str) -> str:
    return f"projects/{project_name}/{DB_CONFIG_FILENAME}"


def save_db_info(project_name: str, db_info: Dict[str, str]) -> None:
    key = load_key()
    encrypted_password = encrypt_password(db_info["password"], key)
    db_info["password"] = encrypted_password
    write_file(get_db_config_path(project_name), json.dumps(db_info))


def load_db_info(project_name: str) -> Dict[str, str]:
    if not path_exists(get_db_config_path(project_name)):
        raise FileNotFoundError(
            f"Database configuration for project {project_name} not found!"
        )

    content = read_file(get_db_config_path(project_name))
    db_info = json.loads(content)

    key = load_key()
    decrypted_password = decrypt_password(db_info["password"], key)
    db_info["password"] = decrypted_password

    return db_info
