import os
from typing import Dict, List
from utils import write_file, render_template
import logging
import subprocess
import re
from jinja2 import Template

# ============================
# Helper Functions
# ============================

def basic_context(table_name: str) -> Dict:
    return {
        "table_name": table_name,
        "table_name_lower": table_name.lower()
    }

def file_path_for(project_name: str, table_name: str, category: str, extension='py') -> str:
    category_path_mapping = {
        "model": "models",
        "controller": "controllers",
        "repository": "repositories",
        "service": "services"
    }
    path_category = category_path_mapping.get(category, category)
    return f"projects/{project_name}/app/{path_category}/{table_name}_{category}.{extension}"

def template_name_for(category: str, template_type: str = "default") -> str:
    category_path_mapping = {
        "model": "app/models",
        "controller": "app/controllers",
        "repository": "app/repositories",
        "service": "app/services"
    }
    path_category = category_path_mapping.get(category, category)
    return f"{path_category}/{template_type}_{category}.j2"

def render_and_save(category: str, table_name: str, project_name: str, context: Dict, template_type: str = "default", enum_types: List[str] = None):
    template_name = template_name_for(category, template_type)
    path = file_path_for(project_name, table_name, category)

    # Include enums in the context
    if enum_types:
        context['enums'] = enum_types

    rendered_content = render_template(template_name, context)
    write_file(path, rendered_content)
    logging.debug(f"{category.capitalize()} for table {table_name} saved at {path}")

def update_init_file(project_name: str, directory_name: str, item_name: str, import_pattern: str):
    """
    Updates the __init__.py file in the given directory with an import based on the provided pattern.
    """
    # Convert table_name (like tournament_rankings) to ClassName (like TournamentRankings)
    class_name = ''.join(word.capitalize() for word in item_name.split('_'))
    
    init_path = f"projects/{project_name}/app/{directory_name}/__init__.py"
    if directory_name == "controllers":
        new_import = import_pattern.format(item_name, item_name)
    else:
        new_import = import_pattern.format(item_name.lower(), class_name)

    # If the file doesn't exist, create it
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write(f"# Auto-generated __init__.py for {directory_name}\n")

    # Read the existing content
    with open(init_path, 'r') as f:
        content = f.readlines()

    # If the new import already exists, no need to update
    if new_import + "\n" in content:
        logging.debug(f"{class_name} is already present in __init__.py of {directory_name}.")
        return

    # Remove existing __all__ declaration
    content = [line for line in content if not line.startswith("__all__")]

    # Append the new import
    content.append(new_import + "\n")

    # Extracting existing names
    item_names = [line.split()[3] for line in content if line.startswith("from .") and line.split()[3] not in ["'", ","]]

    # Ensure no duplicates
    item_names = list(set(item_names))

    # Add the updated __all__ declaration
    all_declaration = "__all__ = [" + ", ".join([f"'{name}'" for name in item_names]) + "]"
    content.append(all_declaration + "\n")

    # Write the updated content back to __init__.py
    with open(init_path, 'w') as f:
        f.writelines(content)

    logging.debug(f"Updated __init__.py for {class_name} in {directory_name} at {init_path}")

def snake_case(s):
    """Convert CamelCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

# ============================
# Model Generation
# ============================
def split_classes_to_files(project_name: str, filename):
    # Determine the directory of the provided file
    directory = os.path.dirname(filename)
    
    # Read the input file
    with open(filename, 'r') as f:
        content = f.read()

    # Split content based on class definition
    classes = re.split(r'(?=class [A-Za-z_][A-Za-z0-9_]*\()', content)
    
    # Common headers (imports and other initializations)
    headers = classes[0]
    
    # Transform the headers
    headers = transform_model_content(headers)
    
    # Iterate over each class content and create separate files
    for cls in classes[1:]:
        # Extract class name
        class_name = re.search(r'class ([A-Za-z_][A-Za-z0-9_]*)\(', cls).group(1)
        file_name = f"{snake_case(class_name)}_model.py"

        # Transform the class content
        cls = transform_model_content(cls)

        # Create new file with class name in the same directory
        new_file_path = os.path.join(directory, file_name)
        with open(new_file_path, 'w') as f:
            f.write(headers + "\n\n")
            f.write(cls)

        update_init_file(project_name, "models", snake_case(class_name).capitalize(), "from .{}_model import {}")        

    rename_relationships_in_model(new_file_path)

def transform_model_content(content):
    # Remove the SQLAlchemy instantiation first
    content = content.replace("db = SQLAlchemy()", "")
    
    # Remove the utf-8 coding line
    content = content.replace("# coding: utf-8", "")
    
    # Replace the import and ensure newline separation
    content = content.replace("from flask_sqlalchemy import SQLAlchemy", 
                              "from ..database.extensions import db\nfrom app.models.model_mixins import ModelToDictMixin\n\n")
    
    # Add the mixin to the class definition using regex (ensure newline separation before the class definition)
    content = re.sub(r'class ([A-Za-z_][A-Za-z0-9_]*)\(db.Model\):', r'\nclass \1(db.Model, ModelToDictMixin):', content)
    
    return content.strip()

def generate_model_for_database(db_info: Dict[str, str], project_name: str):
    logging.info(f"Generating model for table {db_info['db_name']} in project {project_name}")
    
    # Construct the database URL from the db_info dictionary
    database_url = f"postgresql://{db_info['db_username']}:{db_info['db_password']}@{db_info['db_host']}:{db_info['db_port']}/{db_info['db_name']}"

    # Use the file_path_for function to get the path for the model
    output_file = f"projects/{project_name}/app/models/all_tables.txt"

    dir_path = os.path.dirname(output_file)
    os.makedirs(dir_path, exist_ok=True)

    # Construct the command
    command = [
        "flask-sqlacodegen",
        database_url,
        "--outfile", output_file,
        "--flask",
        "--nobackrefs",
        "--noinflect"
    ]

    # Run the command
    subprocess.run(command, check=True)
    split_classes_to_files(project_name, output_file)

def rename_relationships_in_model(model_file):
    with open(model_file, 'r') as f:
        content = f.readlines()

    # A pattern to match the db.relationship lines
    pattern = re.compile(r'(\w+) = db\.relationship\(')
    
    new_content = []
    for line in content:
        match = pattern.search(line)
        if match:
            # Extract the variable name before the relationship
            var_name = match.group(1)

            # If the variable name is generic (like user1, parent1, etc.), rename it
            if var_name.endswith("1"):
                # Extract the associated field name from the primaryjoin clause
                field_name_match = re.search(r'primaryjoin=\'\w+\.(\w+) ==', line)
                if field_name_match:
                    field_name = field_name_match.group(1)
                    new_name = f"{field_name}_relation"
                    line = line.replace(var_name, new_name)
        new_content.append(line)

    # Write the updated content back to the model file
    with open(model_file, 'w') as f:
        f.writelines(new_content)

# ============================
# Controller Generation
# ============================

def generate_controller_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating controller for table {table_name} in project {project_name} using {template_type} template")
    
    context = basic_context(table_name)
    render_and_save("controller", table_name, project_name, context, template_type)
    # Update the __init__.py file
    update_init_file(project_name, "controllers", table_name, "from .{}_controller import {}_bp")

# ============================
# Repository Generation
# ============================

def generate_repository_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating repository for table {table_name} in project {project_name} using {template_type} template")

    context = basic_context(table_name)
    render_and_save("repository", table_name, project_name, context, template_type)
    # Update the __init__.py file with the new repository
    update_init_file(project_name, "repositories", table_name.capitalize(), "from .{}_repository import {}Repository")

# ============================
# Service Generation
# ============================

def generate_service_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating service for table {table_name} in project {project_name} using {template_type} template")

    context = basic_context(table_name)
    render_and_save("service", table_name, project_name, context, template_type)
    # Update the __init__.py file
    update_init_file(project_name, "services", table_name.capitalize(), "from .{}_service import {}Service")

# ============================
# API Structure Generation
# ============================

def generate_api_structure_for_table(db_info: Dict[str, str], table_name: str, project_name: str):
    logging.info(f"Generating API structure for table {table_name} in project {project_name}")

    # Generate controller for the table
    generate_controller_for_table(table_name, project_name)

    # Generate repository for the table
    generate_repository_for_table(table_name, project_name)

    # Generate services for the table
    generate_service_for_table(table_name, project_name)

# ============================
# run.py Generation
# ============================

def create_run_py(project_name):
    controllers_path = os.path.join("projects", project_name, "app", "controllers")
    
    # List all blueprint files
    blueprint_files = [f[:-3] for f in os.listdir(controllers_path) if f.endswith('.py') and f != '__init__.py']
    
    # Extract the base name from filenames and construct import and registration statements
    imports, registrations = generate_blueprint_statements(blueprint_files)
    
    # Load the Jinja2 template
    with open("templates/run_py.j2", "r") as template_file:
        template_content = template_file.read()

    template = Template(template_content)

    # Render the template with the imports and registrations
    run_content = template.render(imports=imports, registrations=registrations)
    run_py_path = os.path.join("projects", project_name, "run.py")
    
    # Write the rendered content to run.py
    with open(run_py_path, "w") as run_file:
        run_file.write(run_content)

    logging.info("run.py has been generated.")

def generate_blueprint_statements(filenames):
    # Extract the base name from filenames and construct import and registration statements
    imports = []
    registrations = []
    
    for filename in filenames:
        # Extract blueprint name from the filename
        blueprint_name = filename.split('_controller')[0]
        
        # Construct import statement
        import_statement = f"from app.controllers.{filename} import {blueprint_name}_bp"
        imports.append(import_statement)
        
        # Construct registration statement
        registration_statement = f"app.register_blueprint({blueprint_name}_bp, url_prefix='/{blueprint_name}')"
        registrations.append(registration_statement)
    
    return imports, registrations

def create_database_extensions(project_name):
    path = os.path.join("projects", project_name, "app", "database", "extensions.py")
    
    # Check if file already exists
    if os.path.exists(path):
        logging.info(f"'extensions.py' already exists. Skipping creation.")
        return
    
    # Ensure the directory exists
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    content = """\
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
"""
    with open(path, 'w') as f:
        f.write(content)
    
    logging.info(f"'extensions.py' has been created successfully!")
