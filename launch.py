"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

#!/usr/bin/env python3
"""
LAUNCH.PY - единая точка входа для Ковчега
Запуск: python launch.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python():
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8+")
        sys.exit(1)

def check_imports():
    required = ['torch', 'customtkinter', 'psutil', 'numpy']
    missing = []
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
    return missing

def setup_dirs():
    dirs = ['data', 'data/logs', 'knowledge', 'backups', 'config']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

def create_default_configs():
    # system_config.json
    sys_conf = Path("config/system_config.json")
    if not sys_conf.exists():
        default = {
            "system": {"name": "Ковчег", "version": "3.0"},
            "model": {"n_state": 256, "temperature": 0.7},
            "paths": {"dna": "data/dna.txt", "weights": "data/son_weights.pth"}
        }
        sys_conf.write_text(json.dumps(default, indent=2, ensure_ascii=False))

    # dna.txt
    dna = Path("data/dna.txt")
    if not dna.exists():
        dna.write_text("=== ДНК ===\nПривет.\n", encoding='utf-8')

def run_training():
    weights = Path("data/son_weights.pth")
    if not weights.exists():
        print("🧬 Весов нет. Запускаю обучение...")
        result = subprocess.run([sys.executable, "scripts/genesis.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Обучение завершено")
        else:
            print(f"❌ Ошибка обучения:\n{result.stderr[:500]}")
            sys.exit(1)

def main():
    print("🚀 ЗАПУСК КОВЧЕГ-АРХИМЕД")
    print("=" * 40)
    
    # 1. Проверки
    check_python()
    missing = check_imports()
    if missing:
        print(f"❌ Не хватает: {', '.join(missing)}")
        print(f"   Установи: pip install {' '.join(missing)}")
        sys.exit(1)
    
    # 2. Настройка
    setup_dirs()
    create_default_configs()
    
    # 3. Обучение (если нужно)
    run_training()
    
    # 4. Запуск интерфейса
    print("🖥️  Запуск интерфейса...")
    os.chdir(Path(__file__).parent)  # Переходим в папку ARK
    subprocess.run([sys.executable, "shell/ark_shell.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)