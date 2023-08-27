from typing import Dict
from core import DatabaseConnector
from utils import write_file, render_template
import logging

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
    return f"projects/{project_name}/{path_category}/{table_name}_{category}.{extension}"

def template_name_for(category: str, template_type: str = "default") -> str:
    category_path_mapping = {
        "model": "models",
        "controller": "controllers",
        "repository": "repositories",
        "service": "services"
    }
    path_category = category_path_mapping.get(category, category)
    return f"{path_category}/{template_type}_{category}.j2"

def render_and_save(category: str, table_name: str, project_name: str, context: Dict, template_type: str = "default"):
    template_name = template_name_for(category, template_type)
    path = file_path_for(project_name, table_name, category)
    rendered_content = render_template(template_name, context)
    write_file(path, rendered_content)
    logging.debug(f"{category.capitalize()} for table {table_name} saved at {path}")

# ============================
# Model Generation
# ============================

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

    connector.close()

    # Convert result to a suitable context for the template
    repr_string = ", ".join([f"{column}={{self.{column}}}" for column, _, _, _ in columns])

    context = basic_context(table_name)
    context.update({
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "repr_string": repr_string
    })

    render_and_save("model", table_name, project_name, context, template_type)

# ============================
# Controller Generation
# ============================

def generate_controller_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating controller for table {table_name} in project {project_name} using {template_type} template")
    
    context = basic_context(table_name)
    render_and_save("controller", table_name, project_name, context, template_type)

# ============================
# Repository Generation
# ============================

def generate_repository_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating repository for table {table_name} in project {project_name} using {template_type} template")

    context = basic_context(table_name)
    render_and_save("repository", table_name, project_name, context, template_type)

# ============================
# Service Generation
# ============================

def generate_service_for_table(table_name: str, project_name: str, template_type: str = "default"):
    logging.debug(f"Generating service for table {table_name} in project {project_name} using {template_type} template")

    context = basic_context(table_name)
    render_and_save("service", table_name, project_name, context, template_type)

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
