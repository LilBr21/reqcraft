from jinja2 import Environment, StrictUndefined

def render(template_str: str, variables: dict[str, str]) -> str:
    jinja_env = Environment(undefined=StrictUndefined)
    template = jinja_env.from_string(template_str)

    result = template.render(**variables)
    return result