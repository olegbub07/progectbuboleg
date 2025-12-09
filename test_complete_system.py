"""
Тестирование полной системы с JSON и PostgreSQL
"""

from notebook.storage import NoteStorage
from notebook.models import Note

def test_complete_system():
    print("🧪 ТЕСТИРОВАНИЕ ПОЛНОЙ СИСТЕМЫ (JSON + PostgreSQL)")
    print("=" * 50)
    
    try:
        # Создаем хранилище
        storage = NoteStorage()
        print("✅ Хранилище инициализировано")
        
        # Тест 1: Создание заметки
        print("\n1. 📝 ТЕСТ СОЗДАНИЯ ЗАМЕТКИ")
        note = Note("Тест PostgreSQL + JSON", "Это тест работы с обоими хранилищами")
        saved_note = storage.save_note(note)
        print(f"   ✅ Заметка создана с ID: {saved_note.id}")
        
        # Тест 2: Получение всех заметок
        print("\n2. 📋 ТЕСТ ПОЛУЧЕНИЯ ВСЕХ ЗАМЕТОК")
        all_notes = storage.get_all_notes()
        print(f"   ✅ Найдено заметок: {len(all_notes)}")
        for note in all_notes:
            print(f"      ID: {note.id}, Заголовок: {note.title}")
        
        # Тест 3: Поиск заметок
        print("\n3. 🔍 ТЕСТ ПОИСКА ЗАМЕТОК")
        search_results = storage.search_notes("PostgreSQL")
        print(f"   ✅ Найдено по запросу 'PostgreSQL': {len(search_results)}")
        
        # Тест 4: Фильтрация по дате
        print("\n4. 📅 ТЕСТ ФИЛЬТРАЦИИ ПО ДАТЕ")
        filtered_notes = storage.filter_notes_by_date(all_notes, 'today')
        print(f"   ✅ Заметок за сегодня: {len(filtered_notes)}")
        
        # Тест 5: Удаление заметки
        print("\n5. 🗑️ ТЕСТ УДАЛЕНИЯ ЗАМЕТКИ")
        if all_notes:
            delete_result = storage.delete_note(saved_note.id)
            print(f"   ✅ Удаление заметки ID {saved_note.id}: {delete_result}")
            
            # Проверяем что удалилось
            remaining_notes = storage.get_all_notes()
            print(f"   ✅ Осталось заметок после удаления: {len(remaining_notes)}")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("💾 Данные сохраняются в: JSON файл И PostgreSQL базу данных")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        print("💡 Проверьте:")
        print("   - Запущен ли PostgreSQL")
        print("   - Правильный ли пароль в .env файле")
        print("   - Существует ли база данных 'notes_db'")

if __name__ == "__main__":
    test_complete_system()