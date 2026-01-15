"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

import shutil
from datetime import datetime
import os

def create_backup():
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    backup_dir = f"backups/ark_backup_{date_str}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Копируем важные данные
    shutil.copytree("data", f"{backup_dir}/data", dirs_exist_ok=True)
    shutil.copytree("config", f"{backup_dir}/config", dirs_exist_ok=True)
    
    print(f"✅ Бэкап создан: {backup_dir}")
    return backup_dir

if __name__ == "__main__":
    create_backup()