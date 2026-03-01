import jmespath
import httpx
from reqcraft.models.collection import Extract

def extract_values(response: httpx.Response, extracts: list[Extract]) -> dict[str, str]:
    extracted_values: dict[str, str] = {}
    for extract in extracts:
        if extract.source == "body":
            extracted_values[extract.name] = str(jmespath.search(extract.path, response.json()) or "")
        elif extract.source == "header":
            extracted_values[extract.name] = response.headers.get(extract.path, "")
        elif extract.source == "status":
            extracted_values[extract.name] = str(response.status_code)

    return extracted_values
