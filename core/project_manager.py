import os
import logging
import shutil
import psycopg2
from core.db_connector import DatabaseConnector
from core.db_info_manager import get_db_config_path, save_db_info
from core.structure_generator import create_run_py, generate_api_structure_for_table, generate_model_for_database

logging.basicConfig(level=logging.INFO)

class ProjectManager:

    def __init__(self):
        self.db_info = {}
        self.generation_options = {}
        self.template_path = "templates"

    def run(self):
        self.setup_project()
        self.configure_database()
        self.setup_project_structure()
        generate_model_for_database(self.db_info, self.project_name)
        self.create_csr()
        create_run_py(self.project_name)

    def setup_project(self):
        """Setup the project based on user input."""
        from core.user_interactions import get_project_name
        self.project_name = get_project_name()
        self.project_path = os.path.join("projects", self.project_name )
        self.config_path = get_db_config_path(self.project_name)

        # Check if project already exists
        self.is_new_project = not os.path.exists(self.project_path)
        self.db_checked = False

    def configure_database(self):
        """Configure the database based on user input. Keep prompting until validation is successful."""
        from core import load_db_info
        if not self.is_new_project and os.path.exists(self.config_path):
            logging.info("Loading existing database configuration...")
            self.db_info = load_db_info(self.project_name)
        
        self.prompt_until_successful_connection()

    def prompt_until_successful_connection(self):
        from core.user_interactions import get_db_details
        """Keep prompting the user for db info until a successful connection is made."""
        while not self.db_checked:
            if not self.db_info:
                self.db_info = get_db_details()
                self.db_checked = False

            if not self.db_checked:
                if self.validate_db_connection():
                    save_db_info(self.project_name , self.db_info)
                    break
                else:
                    self.db_info = ""

    def validate_db_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.db_info["db_host"],
                port=self.db_info["db_port"],
                user=self.db_info["db_username"],
                password=self.db_info["db_password"],
                dbname=self.db_info["db_name"],
            )
            conn.close()
            logging.info("Successfully connected to the database.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            return False

    def setup_project_structure(self):
        self.check_and_create_project_folder()
        save_db_info(self.project_name , self.db_info)
        template_structure = self.load_template_structure()
        self.create_missing_directories(template_structure)
        self.copy_template_files()
        self.create_config_file()

    def generate_structure(self):
        """Generate the project structure based on user preferences."""
        from core.user_interactions import get_generation_options
        self.generation_options = get_generation_options()
        # ... logic to generate the required components ...

    def check_and_create_project_folder(self):
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)
            logging.info(f"Project directory '{self.project_path}' created.")

    def load_template_structure(self) -> dict:
        structure = {}
        for root, dirs, _ in os.walk(self.template_path):
            relative_root = os.path.relpath(root, self.template_path)
            structure[relative_root] = dirs
        return structure

    def create_missing_directories(self, template_structure: dict):
        for relative_root, dirs in template_structure.items():
            for directory in dirs:
                full_path = os.path.join(self.project_path, relative_root, directory)
                if not os.path.exists(full_path):
                    os.makedirs(full_path)
                    logging.info(f"Created missing directory: {full_path}")


    def copy_template_files(self):
        for root, _, files in os.walk(self.template_path):
            relative_root = os.path.relpath(root, self.template_path)
            target_dir = os.path.join(self.project_path, relative_root)
            for file in files:
                if file.endswith(".py"):
                    shutil.copy2(os.path.join(root, file), target_dir)
                    logging.info(f"Copied {file} to {target_dir}")

    def create_config_file(self):
        config_content = """
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://{username}:{password}@{host}:{port}/{dbname}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
        """.format(
            username=self.db_info["db_username"],
            password=self.db_info["db_password"],
            host=self.db_info["db_host"],
            port=self.db_info["db_port"],
            dbname=self.db_info["db_name"]
        )
        
        config_path = os.path.join(self.project_path, "app", "config.py")
        with open(config_path, "w") as config_file:
            config_file.write(config_content)
        logging.info(f"Created config.py inside {self.project_path}/app/")

    def create_csr(self): # Creates controllers, services and repositories
        connector = DatabaseConnector(self.db_info)

        tables_query = (
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        )
        available_tables = [row[0] for row in connector.execute_query(tables_query)]

        for table_name in available_tables:
            generate_api_structure_for_table(self.db_info, table_name, self.project_name)
