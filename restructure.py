import shutil
import os

structure = {
    "bots": ["bot_template.py.j2", "generated_bot.py"],
    "docs/architecture": ["class_diagram.puml", "sequence_diagram.puml"],
    "docs/templates": ["docs_templates.markdown"],
    "docs": ["getting_started.markdown", "index.markdown", "user_experience_report.markdown"],
    "src/egtgbt": ["cli.py", "generate.py", "target_bot_code.py"],
    "src/utils": ["utils_validation.py"],
    "data": ["bot_users.db"],
    "config": ["config_business_card.json"]
}

for dest, files in structure.items():
    os.makedirs(dest, exist_ok=True)
    for file in files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(dest, file))