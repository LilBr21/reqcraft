import base64
from reqcraft.core.renderer import render
from reqcraft.models.collection import Auth, AuthType

def resolve_auth(auth: Auth, variables: dict[str, str]):
    if auth is None:
        return {}
    if auth.type == AuthType.BEARER:
        rendered_token = render(auth.token, variables)
        return {
            "Authorization": f"Bearer {rendered_token}",
        }
    elif auth.type == AuthType.API_KEY:
        rendered_header = render(auth.header, variables)
        rendered_value = render(auth.value, variables)
        return {
            rendered_header: rendered_value,
        }
    elif auth.type == AuthType.BASIC:
        rendered_username = render(auth.username, variables)
        rendered_password = render(auth.password, variables)
        credentials = f"{rendered_username}:{rendered_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}"
        }
    else:
        raise ValueError(f"Unknown auth type: {auth.type}")
