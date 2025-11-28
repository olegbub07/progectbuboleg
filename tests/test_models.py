# tests/test_models.py
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebook.models import Note

class TestNote(unittest.TestCase):
    
    def test_note_creation(self):
        note = Note("Заголовок", "Текст")
        self.assertEqual(note.title, "Заголовок")
        self.assertEqual(note.content, "Текст")
        self.assertIsNone(note.id)
    
    def test_to_dict(self):
        note = Note("Заголовок", "Текст")
        note.id = 1
        data = note.to_dict()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], "Заголовок")
    
    def test_from_dict(self):
        data = {'id': 1, 'title': 'Тест', 'content': 'Текст', 'created_at': '2024-01-01'}
        note = Note.from_dict(data)
        self.assertEqual(note.id, 1)
        self.assertEqual(note.title, 'Тест')

if __name__ == '__main__':
    unittest.main()