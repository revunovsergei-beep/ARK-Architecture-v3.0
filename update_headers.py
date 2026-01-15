import os
import glob

header = '''"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""\n\n'''

# Получаем все .py файлы
for py_file in glob.glob("**/*.py", recursive=True):
    try:
        # Читаем текущее содержание
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, нет ли уже заголовка
        if "ARK ARCHITECTURE v3.0" not in content:
            # Записываем заголовок + оригинальное содержание
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(header + content)
            print(f"✓ Обновлён: {py_file}")
        else:
            print(f"⏭️ Уже обновлён: {py_file}")
            
    except Exception as e:
        print(f"✗ Ошибка с {py_file}: {e}")

print("\n✅ Все файлы обновлены!")