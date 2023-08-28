import os
from typing import Dict, List
from core import DatabaseConnector
from utils import write_file, render_template
import logging

from utils.custom_filters import map_sqlalchemy_type

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
        "model": "models",
        "controller": "controllers",
        "repository": "repositories",
        "service": "services"
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

# ============================
# Model Generation
# ============================
def get_enum_values(connector, enum_type):
    query = f"SELECT unnest(enum_range(NULL::{enum_type}));"
    return [row[0] for row in connector.execute_query(query)]

def generate_enum_from_values(enum_name, values):
    return f"class {enum_name}(Enum):\n" + "\n".join([f"    {value.upper()} = \"{value}\"" for value in values])

def generate_model_for_table(db_info: Dict[str, str], table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating model for table {table_name} in project {project_name} using {template_type} template")
    
    connector = DatabaseConnector(db_info)
    
    # Fetch table details: column names, data types, nullability, and defaults
    column_query = """
    SELECT column_name, data_type, is_nullable, column_default 
    FROM information_schema.columns 
    WHERE table_name = %s
    ORDER BY ordinal_position
    """
    columns = connector.execute_query(column_query, (table_name,))

    # Fetch primary keys for the table
    pk_query = """
    SELECT k.column_name
    FROM information_schema.table_constraints t
    JOIN information_schema.key_column_usage k
    USING(constraint_name,table_schema,table_name)
    WHERE t.constraint_type='PRIMARY KEY'
    AND t.table_name=%s
    ORDER BY ordinal_position
    """
    primary_keys = [row[0] for row in connector.execute_query(pk_query, (table_name,))]

    # Fetch foreign keys for the table
    fk_query = """
    SELECT k.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints t
    JOIN information_schema.key_column_usage k
    USING(constraint_name,table_schema,table_name)
    JOIN information_schema.referential_constraints r
    ON t.constraint_name = r.constraint_name
    JOIN information_schema.constraint_column_usage ccu
    ON r.unique_constraint_name = ccu.constraint_name
    WHERE t.constraint_type='FOREIGN KEY'
    AND t.table_name=%s
    ORDER BY k.ordinal_position
    """
    foreign_keys_data = connector.execute_query(fk_query, (table_name,))
    foreign_keys = {row[0]: f"{row[1]}.{row[2]}" for row in foreign_keys_data}

    enum_query = "SELECT udt_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s AND data_type = 'USER-DEFINED';"
    enum_types = [row[0] for row in connector.execute_query(enum_query, (table_name,))]

    enums = {}
    for enum_type in enum_types:
        enum_values = get_enum_values(connector, enum_type)
        enum_definition = generate_enum_from_values(enum_type.capitalize(), enum_values)
        enums[enum_type] = {"name": enum_type.capitalize(), "definition": enum_definition}

    connector.close()
    
    # Convert result to a suitable context for the template
    repr_string = ", ".join([f"{column}={{self.{column}}}" for column, _, _, _ in columns])

    context = basic_context(table_name)
    context.update({
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "repr_string": repr_string,
        "enums": enums
    })

    render_and_save("model", table_name, project_name, context, template_type, enums)

    # Update the __init__.py file
    update_init_file(project_name, "models", table_name.capitalize(), "from .{}_model import {}")

# ============================
# Controller Generation
# ============================

def generate_controller_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating controller for table {table_name} in project {project_name} using {template_type} template")
    
    context = basic_context(table_name)
    render_and_save("controller", table_name, project_name, context, template_type)
    # Update the __init__.py file
    update_init_file(project_name, "controllers", table_name.capitalize(), "from .{}_controller import {}Controller")

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
    logging.debug(f"Generating API structure for table {table_name} in project {project_name}")

    # Generate model for the table
    generate_model_for_table(db_info, table_name, project_name)

    # Generate controller for the table
    generate_controller_for_table(table_name, project_name)

    # Generate repository for the table
    generate_repository_for_table(table_name, project_name)

    # Generate service for the table
    generate_service_for_table(table_name, project_name)

