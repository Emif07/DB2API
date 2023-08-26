import os

def path_exists(path: str) -> bool:
    return os.path.exists(path)

def create_project_folder(project_name: str) -> None:
    project_path = os.path.join("projects", project_name)
    os.makedirs(project_path, exist_ok=True)


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    with open(file_path, 'w') as file:
        file.write(content)

def append_to_file(file_path: str, content: str) -> None:
    with open(file_path, 'a') as file:
        file.write(content)
