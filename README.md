# reqcraft

A terminal-first HTTP client and API test runner. Define your API requests in YAML, run them from the terminal, and assert on responses — no GUI required.

## Installation

```bash
pip install reqcraft
```

## Quick start

Create a collection file:

```yaml
name: My API
version: "1.0"
variables:
  base_url: "https://jsonplaceholder.typicode.com"

requests:
  - id: get-post
    name: Get a post
    method: GET
    url: "{{ base_url }}/posts/1"
    assertions:
      - type: status
        expected: 200
      - type: json
        path: "id"
        op: equals
        expected: 1
```

Run it:

```bash
reqcraft run my-api.yaml
```

## Collection format

### Top-level fields

| Field | Description |
|-------|-------------|
| `name` | Collection name |
| `version` | Collection version (default: `"1.0"`) |
| `variables` | Default variables available to all requests |
| `requests` | List of requests to run |

### Request fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (used for `depends_on`) |
| `name` | Display name |
| `method` | HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) |
| `url` | URL — supports `{{ variable }}` substitution |
| `headers` | Key/value headers — values support `{{ variable }}` substitution |
| `params` | Query parameters |
| `body` | Request body (`json`, `form`, or `raw`) |
| `depends_on` | List of request IDs that must run first |
| `assertions` | List of assertions to evaluate against the response |
| `extract` | List of values to extract from the response for use in later requests |

### Assertions

```yaml
assertions:
  - type: status
    expected: 200

  - type: json
    path: "data.token"   # JMESPath
    op: exists

  - type: header
    name: content-type
    op: equals
    expected: "application/json"

  - type: response_time
    op: less_than
    expected: 500        # milliseconds

  - type: body_size
    op: greater_than
    expected: 0
```

Available operators: `equals`, `not_equals`, `contains`, `exists`, `not_exists`, `matches`, `greater_than`, `less_than`

### Extracting values for request chaining

```yaml
requests:
  - id: login
    method: POST
    url: "{{ base_url }}/auth/login"
    body:
      json:
        username: "alice"
        password: "secret"
    extract:
      - name: auth_token
        source: body
        path: "data.token"

  - id: get-profile
    depends_on: [login]
    method: GET
    url: "{{ base_url }}/users/me"
    headers:
      Authorization: "Bearer {{ auth_token }}"
```

Extract sources: `body` (JMESPath), `header`, `status`

## CLI reference

```bash
# Run a collection
reqcraft run <collection.yaml>

# Run with an environment file
reqcraft run <collection.yaml> --env production.yaml

# Override a variable
reqcraft run <collection.yaml> --var base_url=https://staging.example.com

# Multiple overrides
reqcraft run <collection.yaml> --var base_url=https://staging.example.com --var timeout=60
```

## Environment files

```yaml
name: production
variables:
  base_url: "https://api.example.com"
  api_key: "your-api-key"
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | All assertions passed |
| `1` | One or more assertions failed |
| `2` | Collection or environment validation error |
| `3` | Network or HTTP error |
