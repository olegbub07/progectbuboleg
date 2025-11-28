"""
Модуль для работы с базой данных PostgreSQL.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Класс для работы с базой данных PostgreSQL."""
    
    def __init__(self):
        """Инициализирует подключение к базе данных."""
        self.connection = None
        self._init_db()
    
    def get_connection(self):
        """Возвращает подключение к базе данных."""
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
        return self.connection
    
    def _init_db(self):
        """Инициализирует базу данных и создает таблицы, если их нет."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Создаем таблицу для заметок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("✅ Таблица 'notes' создана или уже существует")
        except Exception as e:
            print(f"❌ Ошибка при создании таблицы: {e}")
        finally:
            cursor.close()
    
    def close_connection(self):
        """Закрывает подключение к базе данных."""
        if self.connection and not self.connection.closed:
            self.connection.close()

# Тестовое подключение и создание таблицы
if __name__ == "__main__":
    try:
        db = Database()
        print("✅ Модуль database.py работает корректно!")
        db.close_connection()
    except Exception as e:
        print(f"❌ Ошибка: {e}")