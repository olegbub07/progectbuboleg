import psycopg2
from dotenv import load_dotenv
import os

print("🔍 Проверка подключения к PostgreSQL...")

# Загружаем настройки из .env файла
load_dotenv()

print("📁 Загружаем настройки из .env файла...")
print(f"   Хост: {os.getenv('DB_HOST')}")
print(f"   Порт: {os.getenv('DB_PORT')}")
print(f"   База: {os.getenv('DB_NAME')}")
print(f"   Пользователь: {os.getenv('DB_USER')}")
print(f"   Пароль: {'*' * len(os.getenv('DB_PASSWORD', ''))}")

try:
    print("🔌 Пытаемся подключиться к базе данных...")
    
    # Подключаемся к PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'), 
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    print("✅ Подключение к PostgreSQL УСПЕШНО!")
    
    # Создаем курсор для выполнения SQL команд
    cursor = conn.cursor()
    
    # Проверяем версию PostgreSQL
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"📊 Версия PostgreSQL: {version[0]}")
    
    # Проверяем есть ли таблица notes
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'notes'
        );
    """)
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✅ Таблица 'notes' существует!")
    else:
        print("❌ Таблица 'notes' не существует (будет создана позже)")
    
    # Закрываем соединение
    cursor.close()
    conn.close()
    print("🔒 Соединение закрыто")
    
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    print("💡 Проверьте:")
    print("   - Запущен ли PostgreSQL (в меню должно быть 'Stop Server')")
    print("   - Правильный ли пароль в файле .env")
    print("   - Существует ли база данных 'notes_db'")

print("🎯 Проверка завершена!")