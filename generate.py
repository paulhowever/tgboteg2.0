import json
import os
import logging
from jinja2 import Environment, FileSystemLoader
from utils.utils_validation import validate_config, validate_block_schema
import sys


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def generate(config, output_file, config_id=None):
    is_valid, error = validate_config(config)
    if not is_valid:
        raise ValueError(error)
    
    is_valid, error = validate_block_schema(config)
    if not is_valid:
        raise ValueError(error)
    
    logging.debug(f"Generating bot with config: {json.dumps(config, indent=2, ensure_ascii=False)}")
    
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template('bot_template.py.j2')
    output_code = template.render(config=config, config_id=config_id or os.path.basename(output_file).split('.')[0].split('_')[-1])
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.write(output_code)
