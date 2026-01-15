"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

import customtkinter as ctk
import tkinter as tk

class DebugWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("🐛 Окно отладки")
        self.geometry("800x600")
        
        # Делаем окно поверх других
        self.attributes('-topmost', True)
        
        # Текстовое поле для логов
        self.text_area = tk.Text(
            self,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Очистить",
            command=self.clear_logs
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Копировать",
            command=self.copy_logs
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Экспорт",
            command=self.export_logs
        ).pack(side="left", padx=5)
        
        # Загружаем начальные логи
        self.load_initial_logs()
        
    def load_initial_logs(self):
        """Загружает существующие логи"""
        self.text_area.insert("1.0", "=== ЛОГИ СИСТЕМЫ ===\n\n")
        # Здесь будет загрузка из файла
        
    def clear_logs(self):
        """Очищает логи"""
        self.text_area.delete("1.0", tk.END)
        
    def copy_logs(self):
        """Копирует логи в буфер"""
        self.clipboard_clear()
        self.clipboard_append(self.text_area.get("1.0", tk.END))
        
    def export_logs(self):
        """Экспортирует логи в файл"""
        # Будет реализовано позже
        pass