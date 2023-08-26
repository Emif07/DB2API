from typing import Dict
from core import DatabaseConnector
from utils import write_file, render_template

def generate_model_for_table(db_info: Dict[str, str], table_name: str):
    # Initialize the database connector
    connector = DatabaseConnector(db_info)

    # Fetch table details: column names and data types
    column_query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = %s
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
    """
    foreign_keys = connector.execute_query(fk_query, (table_name,))

    # Convert result to a suitable context for the template
    context = {
        "table_name": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys
    }

    # Render the model using the template and context
    rendered_content = render_template("models/default_model.j2", context)

    # Define where to save the generated model
    file_path = f"projects/{db_info['dbname']}/models/{table_name}.py"

    # Save the generated content
    write_file(file_path, rendered_content)

    connector.close()
