from typing import Dict
from jinja2 import Environment, FileSystemLoader
from .custom_filters import sql_to_python

def render_template(template_path: str, context: Dict[str, object]) -> str:
    """
    Renders a Jinja2 template with the provided context.

    Args:
    - template_path (str): Path to the template relative to the templates directory.
    - context (Dict[str, object]): Data to be used when rendering the template.

    Returns:
    - str: Rendered template content.
    """
    # Set up the environment with the templates directory
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters["sql_to_python"] = sql_to_python

    # Load the specified template
    template = env.get_template(template_path)
    
    # Render the template with the provided context
    return template.render(context)
