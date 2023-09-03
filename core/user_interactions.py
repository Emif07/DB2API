from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm

def get_project_name() -> dict:
    project_name = input("Enter your project name: ")
    return project_name

def get_db_details() -> dict:
    db_name = prompt("Enter database name: ", default="poker_tournaments")
    db_user = prompt("Enter database user: ", default="ufuktogay")
    db_password = prompt("Enter database password: ", default="1234")
    db_host = prompt("Enter database host: ", default="localhost")
    db_port = prompt("Enter database port: ", default="5432")
    if not db_host:
        db_host = "localhost"
    if not db_port:
        db_port = "5432"
    return {
        "db_name": db_name,
        "db_username": db_user,
        "db_password": db_password,
        "db_host": db_host,
        "db_port": db_port
    }

def get_generation_options() -> dict:
    generate_models = confirm("Do you want to generate models?", default=True)
    generate_controllers = confirm("Do you want to generate controllers?", default=True)
    generate_repositories = confirm("Do you want to generate repositories?", default=False)
    generate_services = confirm("Do you want to generate services?", default=True)
    
    return {
        "generate_models": generate_models,
        "generate_controllers": generate_controllers,
        "generate_repositories": generate_repositories,
        "generate_services": generate_services
    }
