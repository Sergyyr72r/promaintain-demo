import os

# 1. Создаем папку .streamlit (скрытую)
os.makedirs(".streamlit", exist_ok=True)

# 2. Создаем файл конфигурации с принудительной светлой темой
config_content = """
[theme]
base="light"
primaryColor="#003366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#333333"
font="sans serif"
"""

with open(".streamlit/config.toml", "w") as f:
    f.write(config_content)

print("✅ Успешно! Тема настроена. Теперь перезапустите streamlit run app.py")