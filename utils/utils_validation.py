import json
from jsonschema import validate, ValidationError

def validate_config(config):
    required_fields = {'bot_name', 'handlers'}
    handler_required_fields = {'command', 'text'}
    
    if not all(field in config for field in required_fields):
        return False, "Отсутствуют обязательные поля: bot_name, handlers"
    
    for handler in config.get('handlers', []):
        if not all(field in handler for field in handler_required_fields):
            return False, f"Обработчик {handler.get('command', 'unknown')} не содержит обязательных полей: command, text"
        
        if handler.get('reply_markup') and 'inline_keyboard' in handler['reply_markup']:
            for row in handler['reply_markup']['inline_keyboard']:
                for button in row:
                    if not ('text' in button and ('url' in button or 'callback_data' in button)):
                        return False, f"Кнопка в {handler['command']} не содержит text или url/callback_data"
                    if 'url' in button and not button['url'].startswith(('http://', 'https://', 'tel:')):
                        return False, f"Недопустимый URL в кнопке: {button['url']}"
                    if 'callback_data' in button and 'response' not in button:
                        return False, f"Кнопка с callback_data в {handler['command']} не содержит response"
    
    return True, ""

from jsonschema import validate, ValidationError
import json
import os

def validate_block_schema(config):
    schema_path = os.path.join(os.path.dirname(__file__), 'block_schema.json')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    try:
        validate(instance=config, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, f"Ошибка валидации схемы: {e.message}"

def validate_bot_token(token):
    if not token or not isinstance(token, str):
        return False, "Токен не указан или не является строкой"
    if not token.count(":") == 1 or not token.split(":")[0].isdigit():
        return False, "Некорректный формат токена"
    return True, ""