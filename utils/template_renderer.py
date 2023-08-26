from typing import Dict
from jinja2 import Environment, FileSystemLoader
from .custom_filters import map_sqlalchemy_type

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
    env.filters["map_sqlalchemy_type"] = map_sqlalchemy_type

    # Add the mapping function directly to the context
    context['map_sqlalchemy_type'] = map_sqlalchemy_type

    # Load the specified template
    template = env.get_template(template_path)
    
    # Render the template with the provided context
    return template.render(context)
