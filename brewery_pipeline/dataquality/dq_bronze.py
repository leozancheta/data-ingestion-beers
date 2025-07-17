import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_brewery_basic(brewery, idx):
    """Validação básica sem dependências externas"""
    errors = []
    
    # Verificar se é um dicionário
    if not isinstance(brewery, dict):
        errors.append(f"Item {idx}: Deve ser um objeto JSON")
        return errors
    
    # Campos obrigatórios
    required_fields = ["id", "name", "brewery_type", "city", "state", "country"]
    
    for field in required_fields:
        if field not in brewery:
            errors.append(f"Item {idx}: Campo obrigatório '{field}' não encontrado")
        elif not isinstance(brewery[field], str) or not brewery[field].strip():
            errors.append(f"Item {idx}: Campo '{field}' deve ser uma string não vazia")
    
    # Verificar tipos específicos
    if "website_url" in brewery and brewery["website_url"] is not None:
        if not isinstance(brewery["website_url"], str):
            errors.append(f"Item {idx}: Campo 'website_url' deve ser string ou null")
    
    return errors

def validate_breweries_json(json_path):
    """Validação de dados de cervejarias com fallback sem jsonschema"""
    try:
        # Tentar usar jsonschema se disponível
        from jsonschema import validate, ValidationError
        return validate_with_jsonschema(json_path)
    except ImportError:
        logger.warning("jsonschema não disponível, usando validação básica")
        return validate_with_basic_validation(json_path)

def validate_with_jsonschema(json_path):
    """Validação usando jsonschema"""
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
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            breweries = json.load(f)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {json_path}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        return False
    
    errors = []
    for idx, brewery in enumerate(breweries):
        try:
            validate(instance=brewery, schema=brewery_schema)
        except ValidationError as e:
            errors.append((idx, str(e)))
    
    if errors:
        logger.error("Erros encontrados na validação:")
        for idx, err in errors:
            logger.error(f"Item {idx}: {err}")
        return False
    else:
        logger.info("JSON válido com jsonschema!")
        return True

def validate_with_basic_validation(json_path):
    """Validação básica sem dependências externas"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            breweries = json.load(f)
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {json_path}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao fazer parse do JSON: {e}")
        return False
    
    all_errors = []
    for idx, brewery in enumerate(breweries):
        errors = validate_brewery_basic(brewery, idx)
        all_errors.extend(errors)
    
    if all_errors:
        logger.error("Erros encontrados na validação:")
        for error in all_errors:
            logger.error(error)
        return False
    else:
        logger.info(f"JSON válido! Validados {len(breweries)} registros com validação básica")
        return True

if __name__ == "__main__":
    validate_breweries_json('/opt/airflow/data/bronze/breweries_raw.json')