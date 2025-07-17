import json
from jsonschema import validate, ValidationError

brewery_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "brewery_type": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "country": {"type": "string"},
        "website_url": {"type": ["string", "null"]},
    },
    "required": ["id", "name", "brewery_type", "city", "state", "country"],
    "additionalProperties": True
}

def validate_breweries_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        breweries = json.load(f)
    errors = []
    for idx, brewery in enumerate(breweries):
        try:
            validate(instance=brewery, schema=brewery_schema)
        except ValidationError as e:
            errors.append((idx, str(e)))
    if errors:
        print("Erros encontrados:")
        for idx, err in errors:
            print(f"Item {idx}: {err}")
        return False
    else:
        print("JSON válido!")
        return True

if __name__ == "__main__":
    validate_breweries_json('/opt/airflow/data/bronze/breweries_raw.json')