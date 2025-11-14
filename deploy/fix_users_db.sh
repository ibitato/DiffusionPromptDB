#!/bin/bash
# Fix users database path configuration

cd /var/www/diffusionprompt/src/api

# Create backup
cp config.py config.py.backup

# Add users_db_path configuration
python3 << 'PYTHON'
# Read config.py
with open("config.py", "r") as f:
    content = f.read()

# Add users_db_path configuration after catalog_db_path
if "users_db_path" not in content:
    new_line = '    users_db_path: str = "../data/users.db"\n'
    content = content.replace(
        '    catalog_db_path: str = "database/prompts_catalog.db"',
        '    catalog_db_path: str = "database/prompts_catalog.db"\n' + new_line
    )
    
    # Write back
    with open("config.py", "w") as f:
        f.write(content)
    
    print("✅ users_db_path agregado a config.py")
else:
    print("⚠️ users_db_path ya existe en config.py")
PYTHON

# Restart API
systemctl restart diffusionprompt-api
sleep 3
systemctl status diffusionprompt-api --no-pager

echo ""
echo "✅ Configuración actualizada y servicio reiniciado"
