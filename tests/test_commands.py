# tests/test_commands.py
import unittest
import sys
import os
from unittest.mock import Mock, patch
import io
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebook.commands import NoteCommands
from notebook.models import Note

class TestNoteCommands(unittest.TestCase):
    
    def setUp(self):
        self.mock_storage = Mock()
        self.commands = NoteCommands(self.mock_storage)
    
    def test_add_note_success(self):
        note = Note("Тест", "Текст")
        note.id = 1
        self.mock_storage.save_note.return_value = note
        
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.add_note("Тест", "Текст")
            output = fake_out.getvalue()
            self.assertIn("Заметка добавлена", output)
    
    def test_add_note_empty_title(self):
        with self.assertRaises(ValueError):
            self.commands.add_note("", "Текст")
    
    def test_add_note_empty_content(self):
        with self.assertRaises(ValueError):
            self.commands.add_note("Заголовок", "")
    
    def test_list_notes_empty(self):
        self.mock_storage.get_all_notes.return_value = []
        
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.list_notes()
            output = fake_out.getvalue()
            self.assertIn("Заметок пока нет", output)
    
    def test_list_notes_with_data(self):
        note = Note("Тест", "Текст")
        note.id = 1
        self.mock_storage.get_all_notes.return_value = [note]
        
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.list_notes()
            output = fake_out.getvalue()
            self.assertIn("Тест", output)
    
    def test_search_notes_empty(self):
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.search_notes("")
            output = fake_out.getvalue()
            self.assertIn("Введите текст", output)
    
    def test_delete_note_success(self):
        self.mock_storage.delete_note.return_value = True
        
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.delete_note(1)
            output = fake_out.getvalue()
            self.assertIn("удалена", output)
    
    def test_delete_note_not_found(self):
        self.mock_storage.delete_note.return_value = False
        
        with patch('sys.stdout', new_callable=io.StringIO) as fake_out:
            self.commands.delete_note(999)
            output = fake_out.getvalue()
            self.assertIn("не найдена", output)

if __name__ == '__main__':
    unittest.main()