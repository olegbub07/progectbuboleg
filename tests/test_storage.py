"""
Тесты для модуля storage с PostgreSQL.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebook.storage import NoteStorage
from notebook.models import Note

class TestNoteStoragePostgreSQL(unittest.TestCase):
    """Тесты для класса NoteStorage с PostgreSQL (с использованием моков)."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем мок для базы данных
        self.mock_db = MagicMock()
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Настраиваем моки
        self.mock_db.get_connection.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        
        # Патчим Database в NoteStorage
        self.db_patcher = patch('notebook.storage.Database')
        self.mock_database_class = self.db_patcher.start()
        self.mock_database_instance = MagicMock()
        self.mock_database_class.return_value = self.mock_database_instance
        self.mock_database_instance.get_connection.return_value = self.mock_connection
        
        self.storage = NoteStorage()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        self.db_patcher.stop()
    
    def test_save_note(self):
        """Тест сохранения заметки."""
        # Arrange
        note = Note("Тест", "Тестовое содержание")
        self.mock_cursor.fetchone.return_value = (1,)
        
        # Act
        saved_note = self.storage.save_note(note)
        
        # Assert
        self.assertIsNotNone(saved_note.id)
        self.mock_cursor.execute.assert_called()
    
    def test_get_all_notes(self):
        """Тест получения всех заметок."""
        # Arrange
        mock_rows = [
            (1, 'Заметка 1', 'Содержание 1', '2024-01-01T10:00:00'),
            (2, 'Заметка 2', 'Содержание 2', '2024-01-02T10:00:00')
        ]
        self.mock_cursor.fetchall.return_value = mock_rows
        
        # Act
        notes = self.storage.get_all_notes()
        
        # Assert
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].title, 'Заметка 1')
        self.assertEqual(notes[1].title, 'Заметка 2')
    
    def test_delete_note(self):
        """Тест удаления заметки."""
        # Arrange
        self.mock_cursor.rowcount = 1
        
        # Act
        result = self.storage.delete_note(1)
        
        # Assert
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_with("DELETE FROM notes WHERE id = %s", (1,))
    
    def test_delete_nonexistent_note(self):
        """Тест удаления несуществующей заметки."""
        # Arrange
        self.mock_cursor.rowcount = 0
        
        # Act
        result = self.storage.delete_note(999)
        
        # Assert
        self.assertFalse(result)
    
    def test_search_notes(self):
        """Тест поиска заметок."""
        # Arrange
        mock_rows = [
            (1, 'Python программирование', 'Изучаем Python', '2024-01-01T10:00:00')
        ]
        self.mock_cursor.fetchall.return_value = mock_rows
        
        # Act
        results = self.storage.search_notes("Python")
        
        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Python программирование')
        self.mock_cursor.execute.assert_called_with(
            "SELECT id, title, content, created_at FROM notes WHERE title ILIKE %s OR content ILIKE %s ORDER BY created_at DESC",
            ('%Python%', '%Python%')
        )

if __name__ == '__main__':
    unittest.main()