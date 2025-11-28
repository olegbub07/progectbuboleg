"""
Модуль для работы с хранилищем заметок.

Отвечает за сохранение, чтение, удаление и поиск заметок в JSON-файле и базе данных PostgreSQL.
"""

import json
import os
import psycopg2
from datetime import datetime, date, timedelta
from typing import List
from .models import Note
from .database import Database

class NoteStorage:
    """Класс для работы с файлом заметок в формате JSON и базой данных PostgreSQL.
    
    Attributes:
        filename (str): Имя файла для хранения заметок.
    """
    
    def __init__(self, filename: str = "notes.json"):
        """Инициализирует хранилище заметок.
        
        Args:
            filename (str, optional): Имя файла для хранения. По умолчанию "notes.json".
        """
        self.filename = filename
        self.db = Database()
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Создает файл для хранения заметок, если он не существует."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
            print(f"📁 Создан новый файл для заметок: {self.filename}")
    
    def _read_notes(self) -> List[dict]:
        """Читает все заметки из файла.
        
        Returns:
            List[dict]: Список словарей с данными заметок.
            
        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если файл поврежден.
        """
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_notes(self, notes_data: List[dict]):
        """Записывает заметки в файл.
        
        Args:
            notes_data (List[dict]): Список словарей с данными заметок.
            
        Raises:
            IOError: Если произошла ошибка записи в файл.
        """
        with open(self.filename, 'w') as f:
            json.dump(notes_data, f, indent=2)
    
    def get_all_notes(self) -> List[Note]:
        """Получает все заметки в виде объектов Note.
        
        Returns:
            List[Note]: Список объектов заметок.
        """
        # Получаем заметки из базы данных
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            
            notes = []
            for row in rows:
                note = Note.from_db_row(row)
                notes.append(note)
            
            return notes
        except Exception as e:
            print(f"Ошибка при получении заметок из БД: {e}")
            # Если ошибка с БД, возвращаем заметки из JSON файла
            notes_data = self._read_notes()
            return [Note.from_dict(note_data) for note_data in notes_data]
        finally:
            cursor.close()
    
    def save_note(self, note: Note) -> Note:
        """Сохраняет заметку в файл и базу данных.
        
        Если у заметки нет ID, ей присваивается новый уникальный ID
        и она добавляется в хранилище.
        
        Args:
            note (Note): Объект заметки для сохранения.
            
        Returns:
            Note: Сохранённая заметка с присвоенным ID.
            
        Raises:
            IOError: Если произошла ошибка записи в файл.
        """
        # Сохраняем в базу данных
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if note.id is None:
                # Вставка новой заметки
                cursor.execute(
                    "INSERT INTO notes (title, content, created_at) VALUES (%s, %s, %s) RETURNING id",
                    (note.title, note.content, note.created_at)
                )
                note.id = cursor.fetchone()[0]
            else:
                # Обновление существующей заметки
                cursor.execute(
                    "UPDATE notes SET title = %s, content = %s WHERE id = %s",
                    (note.title, note.content, note.id)
                )
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при сохранении заметки в БД: {e}")
        
        finally:
            cursor.close()
        
        # Также сохраняем в JSON файл для обратной совместимости
        notes_data = self._read_notes()
        
        if note.id is None:
            if notes_data:
                note.id = max([n['id'] for n in notes_data]) + 1
            else:
                note.id = 1
            notes_data.append(note.to_dict())
        else:
            # Обновляем существующую заметку в JSON
            for i, note_data in enumerate(notes_data):
                if note_data['id'] == note.id:
                    notes_data[i] = note.to_dict()
                    break
            else:
                notes_data.append(note.to_dict())
        
        self._write_notes(notes_data)
        return note
    
    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID.
        
        Args:
            note_id (int): ID заметки для удаления.
            
        Returns:
            bool: True если удаление успешно, False если заметка не найдена.
        """
        # Удаляем из базы данных
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        db_deleted = False
        try:
            cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            conn.commit()
            db_deleted = cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при удалении заметки из БД: {e}")
        finally:
            cursor.close()
        
        # Удаляем из JSON файла
        notes_data = self._read_notes()
        initial_length = len(notes_data)
        
        notes_data = [note for note in notes_data if note['id'] != note_id]
        
        json_deleted = len(notes_data) < initial_length
        if json_deleted:
            self._write_notes(notes_data)
        
        return db_deleted or json_deleted
    
    def search_notes(self, query: str) -> List[Note]:
        """Ищет заметки по тексту в заголовке или содержании.
        
        Args:
            query (str): Текст для поиска.
            
        Returns:
            List[Note]: Список найденных заметок.
        """
        # Ищем в базе данных
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, title, content, created_at FROM notes WHERE title ILIKE %s OR content ILIKE %s ORDER BY created_at DESC",
                (f'%{query}%', f'%{query}%')
            )
            rows = cursor.fetchall()
            
            notes = []
            for row in rows:
                note = Note.from_db_row(row)
                notes.append(note)
            
            return notes
        except Exception as e:
            print(f"Ошибка при поиске заметок в БД: {e}")
            # Если ошибка с БД, ищем в JSON файле
            notes = self.get_all_notes()
            query = query.lower()
            
            return [
                note for note in notes 
                if query in note.title.lower() or query in note.content.lower()
            ]
        finally:
            cursor.close()
    
    def filter_notes_by_date(self, notes: List[Note], date_filter: str) -> List[Note]:
        """Фильтрует заметки по дате создания.
        
        Args:
            notes (List[Note]): Список заметок для фильтрации.
            date_filter (str): Фильтр даты (today, week, month, ГГГГ-ММ-ДД, ГГГГ-ММ, ГГГГ).
            
        Returns:
            List[Note]: Отфильтрованный список заметок.
        """
        today = datetime.now().date()
        filtered_notes = []
        
        for note in notes:
            try:
                note_date = datetime.fromisoformat(note.created_at).date()
                
                if date_filter == 'today':
                    if note_date == today:
                        filtered_notes.append(note)
                elif date_filter == 'week':
                    week_ago = today - timedelta(days=7)
                    if note_date >= week_ago:
                        filtered_notes.append(note)
                elif date_filter == 'month':
                    month_ago = today - timedelta(days=30)
                    if note_date >= month_ago:
                        filtered_notes.append(note)
                elif len(date_filter) == 10:  # ГГГГ-ММ-ДД
                    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                    if note_date == filter_date:
                        filtered_notes.append(note)
                elif len(date_filter) == 7:  # ГГГГ-ММ
                    filter_year, filter_month = map(int, date_filter.split('-'))
                    if note_date.year == filter_year and note_date.month == filter_month:
                        filtered_notes.append(note)
                elif len(date_filter) == 4:  # ГГГГ
                    filter_year = int(date_filter)
                    if note_date.year == filter_year:
                        filtered_notes.append(note)
                        
            except (ValueError, AttributeError):
                continue
        
        return filtered_notes