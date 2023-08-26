from typing import Dict
from core import DatabaseConnector
from utils import write_file, render_template
from utils.file_manager import write_file

def generate_model_for_table(db_info: Dict[str, str], table_name: str, project_name: str):
    # Initialize the database connector
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

    context = {
        "table_name": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "repr_string": repr_string
    }
    # Render the model using the template and context
    rendered_content = render_template("models/default_model.j2", context)

    # Define where to save the generated model
    file_path = f"projects/{project_name}/models/{table_name}.py"

    # Save the generated content
    write_file(file_path, rendered_content)
