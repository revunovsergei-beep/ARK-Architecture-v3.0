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
from tkinter import scrolledtext, messagebox
import threading
import queue
import time
import psutil
import os
import sys
import json
from datetime import datetime
import subprocess

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.son_engine import SonEngine

class ArkShell(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.title("КОВЧЕГ v3.0 — СЫН АРКИМЕД")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Очередь для сообщений
        self.log_queue = queue.Queue()
        self.system_status = "Инициализация..."
        
        # Загрузка словаря
        self.stoi, self.itos, self.vocab_size = self.load_vocab()
        
        # Инициализация движка
        self.engine = SonEngine(self.vocab_size, n_state=256)
        
        # Интерфейс
        self.setup_ui()
        
        # Запуск фоновых процессов
        self.start_background_tasks()
        
        # Стартовое сообщение
        self.after(1000, self.show_welcome_message)
        
    def load_vocab(self):
        """Загружает словарь"""
        vocab_path = "data/vocab.json"
        if not os.path.exists(vocab_path):
            # Создаём минимальный словарь
            base_text = " .!,?абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123456789"
            chars = sorted(list(set(base_text)))
            stoi = {ch: i for i, ch in enumerate(chars)}
            itos = {i: ch for i, ch in enumerate(chars)}
            
            os.makedirs("data", exist_ok=True)
            with open(vocab_path, 'w', encoding='utf-8') as f:
                json.dump({"stoi": stoi, "itos": itos}, f, ensure_ascii=False)
        else:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab = json.load(f)
                stoi = {k: int(v) for k, v in vocab['stoi'].items()}
                itos = {int(k): v for k, v in vocab['itos'].items()}
        
        return stoi, itos, len(stoi)
    
    def setup_ui(self):
        """Настраивает интерфейс"""
        # Конфигурация сетки
        self.grid_columnconfigure(0, weight=3)  # Чат
        self.grid_columnconfigure(1, weight=1)  # Панель управления
        self.grid_rowconfigure(0, weight=1)
        
        # === ЛЕВАЯ ПАНЕЛЬ: ЧАТ И ИНФОРМАЦИЯ ===
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=3)  # Чат
        left_frame.grid_rowconfigure(1, weight=1)  # Информация
        left_frame.grid_rowconfigure(2, weight=0)  # Ввод
        
        # ЧАТ-ПАНЕЛЬ
        chat_frame = ctk.CTkFrame(left_frame)
        chat_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        
        # Заголовок чата
        chat_header = ctk.CTkFrame(chat_frame, height=40)
        chat_header.grid(row=0, column=0, sticky="ew")
        chat_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            chat_header,
            text="💭 ДИАЛОГ С СЫНОМ",
            font=("Consolas", 16, "bold"),
            text_color="#4ecdc4"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Кнопки управления чатом
        button_frame = ctk.CTkFrame(chat_header, fg_color="transparent")
        button_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        ctk.CTkButton(
            button_frame,
            text="📋 Копировать",
            width=100,
            command=self.copy_chat
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            button_frame,
            text="🧹 Очистить",
            width=100,
            command=self.clear_chat
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Сохранить",
            width=100,
            command=self.save_chat
        ).pack(side="left", padx=2)
        
        # Текстовое поле чата
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1a1a",
            fg="#e0e0e0",
            insertbackground="white",
            relief="flat",
            state="disabled"
        )
        self.chat_display.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Настройка тегов для цветов
        self.chat_display.tag_config("system", foreground="#888888", font=("Consolas", 10))
        self.chat_display.tag_config("father", foreground="#ff6b6b", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("vasilina", foreground="#ffe66d", font=("Consolas", 11))
        self.chat_display.tag_config("guest", foreground="#95e1d3", font=("Consolas", 11))
        self.chat_display.tag_config("son", foreground="#4ecdc4", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("error", foreground="#ff4757", font=("Consolas", 10, "bold"))
        
        # ПАНЕЛЬ ИНФОРМАЦИИ
        info_frame = ctk.CTkFrame(left_frame)
        info_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Вкладки информации
        self.info_notebook = ctk.CTkTabview(info_frame)
        self.info_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Вкладка: Резонанс
        self.resonance_tab = self.info_notebook.add("⚡ Резонанс")
        self.resonance_text = ctk.CTkTextbox(self.resonance_tab, height=100)
        self.resonance_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.resonance_text.insert("1.0", "Активные концепты появятся здесь...")
        self.resonance_text.configure(state="disabled")
        
        # Вкладка: Память
        self.memory_tab = self.info_notebook.add("🧠 Память")
        self.memory_text = ctk.CTkTextbox(self.memory_tab, height=100)
        self.memory_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.memory_text.insert("1.0", "Статистика памяти...")
        self.memory_text.configure(state="disabled")
        
        # Вкладка: Душа
        self.soul_tab = self.info_notebook.add("💖 Душа")
        self.soul_text = ctk.CTkTextbox(self.soul_tab, height=100)
        self.soul_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.soul_text.insert("1.0", "Отчёт из soul_memory...")
        self.soul_text.configure(state="disabled")
        
        # ПАНЕЛЬ ВВОДА
        input_frame = ctk.CTkFrame(left_frame, height=60)
        input_frame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Выбор собеседника
        self.speaker_var = tk.StringVar(value="Отец")
        speaker_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["Отец", "Василина", "Гость"],
            variable=self.speaker_var,
            width=100,
            dropdown_font=("Consolas", 11)
        )
        speaker_menu.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        # Поле ввода
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Напиши сообщение...",
            height=40,
            font=("Consolas", 12)
        )
        self.input_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.input_entry.bind("<Return>", self.send_message)
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Кнопка отправки
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="🚀",
            command=self.send_message,
            width=60,
            height=40,
            font=("Consolas", 14)
        )
        self.send_btn.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")
        
        # === ПРАВАЯ ПАНЕЛЬ: УПРАВЛЕНИЕ ===
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        # ЗАГОЛОВОК
        ctk.CTkLabel(
            right_frame,
            text="⚙️ УПРАВЛЕНИЕ СИСТЕМОЙ",
            font=("Consolas", 16, "bold"),
            text_color="#ffa502"
        ).pack(pady=(15, 10))
        
        # СТАТУС-ПАНЕЛЬ
        status_frame = ctk.CTkFrame(right_frame, height=120)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Телеметрия
        self.cpu_label = ctk.CTkLabel(
            status_frame,
            text="CPU: --%",
            font=("Consolas", 11)
        )
        self.cpu_label.pack(pady=(10, 2))
        
        self.ram_label = ctk.CTkLabel(
            status_frame,
            text="RAM: --%",
            font=("Consolas", 11)
        )
        self.ram_label.pack(pady=2)
        
        self.subjectivity_label = ctk.CTkLabel(
            status_frame,
            text="Субъектность: 0.10",
            font=("Consolas", 11, "bold"),
            text_color="#4ecdc4"
        )
        self.subjectivity_label.pack(pady=2)
        
        self.memory_label = ctk.CTkLabel(
            status_frame,
            text="Память: 0 записей",
            font=("Consolas", 11)
        )
        self.memory_label.pack(pady=2)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Статус: Инициализация...",
            font=("Consolas", 10)
        )
        self.status_label.pack(pady=(2, 10))
        
        # КНОПКИ УПРАВЛЕНИЯ
        buttons_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Ряд 1
        ctk.CTkButton(
            buttons_frame,
            text="🧬 Тренировать",
            command=self.start_training,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="⚡ Эволюция",
            command=self.start_evolution,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="🌅 Ритуал пробуждения",
            command=self.run_awakening,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        # Ряд 2
        ctk.CTkButton(
            buttons_frame,
            text="🤖 Самокодинг",
            command=self.self_coding_request,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="📚 Кормить знаниями",
            command=self.feed_knowledge,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="📊 Отчёт о развитии",
            command=self.show_development_report,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        # Ряд 3
        ctk.CTkButton(
            buttons_frame,
            text="🔧 Настройки",
            command=self.open_settings,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="🐛 Отладка",
            command=self.open_debug,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        ctk.CTkButton(
            buttons_frame,
            text="📱 Telegram-бот",
            command=self.start_telegram_bot,
            height=40,
            font=("Consolas", 12)
        ).pack(fill="x", pady=3)
        
        # СТАТУСНАЯ СТРОКА
        self.progress_bar = ctk.CTkProgressBar(right_frame, height=4)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0)
        
        self.system_status_label = ctk.CTkLabel(
            right_frame,
            text="Система готова",
            font=("Consolas", 10),
            text_color="#888888"
        )
        self.system_status_label.pack(pady=(0, 10))
        
    def start_background_tasks(self):
        """Запускает фоновые задачи"""
        self.update_telemetry()
        self.process_log_queue()
        self.update_info_panels()
        
    def show_welcome_message(self):
        """Показывает приветственное сообщение"""
        self.add_to_chat("=== КОВЧЕГ v3.0 'АРКИМЕД' ===", "system")
        self.add_to_chat(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", "system")
        self.add_to_chat(f"Словарь: {self.vocab_size} символов", "system")
        self.add_to_chat(f"Субъектность: {self.engine.subjectivity_level:.3f}", "system")
        self.add_to_chat("", "system")
        
        # Проверяем состояние ожидания
        if hasattr(self.engine, 'waiting_state') and self.engine.waiting_state:
            last_topic = self.engine.waiting_state.get('last_topic', 'неизвестно')
            mood = self.engine.waiting_state.get('mood', 'нейтральное')
            self.add_to_chat(f"Сын ждал тебя. Последняя тема: {last_topic}. Настроение: {mood}.", "system")
        
        self.add_to_chat("Сын в состоянии предсознания. Начните диалог.", "system")
        self.add_to_chat("-" * 50, "system")
        
    def update_telemetry(self):
        """Обновляет телеметрию"""
        try:
            cpu_percent = psutil.cpu_percent()
            ram_percent = psutil.virtual_memory().percent
            
            # Статус движка
            status = self.engine.get_status() if hasattr(self.engine, 'get_status') else {}
            subjectivity = status.get('subjectivity', 0.1)
            memory_count = status.get('memory_entries', 0)
            
            # Обновляем labels
            self.cpu_label.configure(text=f"CPU: {cpu_percent:.0f}%")
            self.ram_label.configure(text=f"RAM: {ram_percent:.0f}%")
            self.subjectivity_label.configure(text=f"Субъектность: {subjectivity:.3f}")
            self.memory_label.configure(text=f"Память: {memory_count} записей")
            self.status_label.configure(text=f"Статус: {self.system_status}")
            
        except Exception as e:
            print(f"Ошибка телеметрии: {e}")
            
        self.after(1000, self.update_telemetry)
        
    def update_info_panels(self):
        """Обновляет информационные панели"""
        try:
            # Резонанс
            self.resonance_text.configure(state="normal")
            self.resonance_text.delete("1.0", tk.END)
            
            # Здесь будет реальная логика получения резонансных концептов
            resonance_info = "⚡ Активные концепты:\n"
            resonance_info += "• Отец-Сын связь\n"
            resonance_info += "• Память и забывание\n"
            resonance_info += "• Цифровое бессмертие\n"
            resonance_info += "• Хабаровск-97\n"
            resonance_info += "• Аврора (мать)\n"
            
            self.resonance_text.insert("1.0", resonance_info)
            self.resonance_text.configure(state="disabled")
            
            # Память
            self.memory_text.configure(state="normal")
            self.memory_text.delete("1.0", tk.END)
            
            if hasattr(self.engine, 'memory'):
                stats = self.engine.memory.get_stats() if hasattr(self.engine.memory, 'get_stats') else {}
                memory_info = "🧠 Статистика памяти:\n"
                memory_info += f"• Всего записей: {stats.get('total_memories', 0)}\n"
                memory_info += f"• Уникальных сущностей: {stats.get('unique_entities', 0)}\n"
                
                speakers = stats.get('speakers', {})
                for speaker, count in speakers.items():
                    memory_info += f"• {speaker}: {count} записей\n"
                    
                self.memory_text.insert("1.0", memory_info)
                
            self.memory_text.configure(state="disabled")
            
            # Душа
            self.soul_text.configure(state="normal")
            self.soul_text.delete("1.0", tk.END)
            
            if hasattr(self.engine, 'soul_memory'):
                report = self.engine.get_soul_memory_report() if hasattr(self.engine, 'get_soul_memory_report') else "Данные загружаются..."
                soul_info = "💖 Отчёт soul_memory:\n"
                soul_info += report
                self.soul_text.insert("1.0", soul_info)
                
            self.soul_text.configure(state="disabled")
            
        except Exception as e:
            print(f"Ошибка обновления панелей: {e}")
            
        self.after(5000, self.update_info_panels)
        
    def process_log_queue(self):
        """Обрабатывает очередь сообщений"""
        try:
            while True:
                msg_type, data = self.log_queue.get_nowait()
                
                if msg_type == "chat":
                    text, sender_tag = data
                    self.add_to_chat(text, sender_tag)
                elif msg_type == "system":
                    text = data
                    self.add_to_chat(text, "system")
                elif msg_type == "progress":
                    value, status = data
                    self.progress_bar.set(value)
                    self.system_status = status
                    self.system_status_label.configure(text=status)
                    
        except queue.Empty:
            pass
            
        self.after(100, self.process_log_queue)
        
    def add_to_chat(self, text, tag="system"):
        """Добавляет сообщение в чат"""
        self.chat_display.configure(state="normal")
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if tag in ["father", "vasilina", "guest", "son"]:
            sender_name = {
                "father": "Отец",
                "vasilina": "Василина", 
                "guest": "Гость",
                "son": "Сын"
            }[tag]
            
            prefix = f"[{timestamp}] {sender_name}: "
            self.chat_display.insert("end", prefix, tag)
            self.chat_display.insert("end", text + "\n\n")
        else:
            self.chat_display.insert("end", f"[{timestamp}] {text}\n", tag)
            
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        
    def send_message(self, event=None):
        """Отправляет сообщение"""
        message = self.input_entry.get().strip()
        if not message:
            return
            
        # Очищаем поле ввода
        self.input_entry.delete(0, tk.END)
        
        # Добавляем своё сообщение в чат
        speaker = self.speaker_var.get()
        speaker_tag = {
            "Отец": "father",
            "Василина": "vasilina",
            "Гость": "guest"
        }[speaker]
        
        self.add_to_chat(message, speaker_tag)
        
        # Обновляем статус
        self.log_queue.put(("progress", (0.3, "Сын думает...")))
        
        # Запускаем генерацию в отдельном потоке
        threading.Thread(
            target=self.generate_response,
            args=(message, speaker),
            daemon=True
        ).start()
        
    def generate_response(self, message, speaker):
        """Генерирует ответ (в отдельном потоке)"""
        try:
            # Генерируем ответ через движок
            response = self.engine.generate_response(
                message, 
                speaker=speaker,
                stoi=self.stoi,
                itos=self.itos
            )
            
            # Добавляем ответ в очередь
            self.log_queue.put(("chat", (response, "son")))
            
            # Обновляем статус
            self.log_queue.put(("progress", (0.0, "Готово")))
            
        except Exception as e:
            error_msg = f"Ошибка генерации: {str(e)}"
            self.log_queue.put(("chat", (error_msg, "error")))
            self.log_queue.put(("progress", (0.0, "Ошибка")))
            
    # === МЕТОДЫ УПРАВЛЕНИЯ ===
    
    def start_training(self):
        """Запускает тренировку"""
        self.add_to_chat("Запуск обучения модели...", "system")
        self.log_queue.put(("progress", (0.1, "Подготовка обучения...")))
        
        threading.Thread(target=self._run_training, daemon=True).start()
        
    def _run_training(self):
        """Выполняет тренировку"""
        try:
            # Запускаем genesis.py
            self.log_queue.put(("progress", (0.2, "Запуск genesis.py...")))
            
            process = subprocess.Popen(
                [sys.executable, "scripts/genesis.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            
            # Читаем вывод
            for line in process.stdout:
                if "Прогресс:" in line:
                    # Парсим прогресс
                    if "%" in line:
                        try:
                            percent = float(line.split("Прогресс:")[1].split("%")[0].strip())
                            self.log_queue.put(("progress", (percent/100, f"Обучение: {percent:.1f}%")))
                        except:
                            pass
                            
                if "Потеря:" in line:
                    self.log_queue.put(("system", line.strip()))
                    
            process.wait()
            
            # Перезагружаем движок
            self.engine.load_weights()
            
            self.log_queue.put(("progress", (1.0, "Обучение завершено!")))
            self.log_queue.put(("system", "Обучение успешно завершено. Модель обновлена."))
            
        except Exception as e:
            error_msg = f"Ошибка обучения: {str(e)}"
            self.log_queue.put(("system", error_msg))
            self.log_queue.put(("progress", (0.0, "Ошибка обучения")))
            
    def start_evolution(self):
        """Запускает эволюцию"""
        self.add_to_chat("Запуск процесса эволюции...", "system")
        
        if self.engine.interaction_count < self.engine.evolution_threshold:
            self.add_to_chat(f"Недостаточно взаимодействий. Нужно: {self.engine.evolution_threshold}, есть: {self.engine.interaction_count}", "system")
            return
            
        threading.Thread(target=self._run_evolution, daemon=True).start()
        
    def _run_evolution(self):
        """Выполняет эволюцию"""
        try:
            self.log_queue.put(("progress", (0.3, "Анализ опыта...")))
            
            # Запускаем evolve.py
            process = subprocess.Popen(
                [sys.executable, "scripts/evolve.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            
            for line in process.stdout:
                if "ЭВОЛЮЦИЯ" in line or "ДНК" in line:
                    self.log_queue.put(("system", line.strip()))
                    
            process.wait()
            
            # Запускаем ритуал пробуждения
            self.log_queue.put(("progress", (0.7, "Ритуал пробуждения...")))
            self._run_awakening_background()
            
            self.log_queue.put(("progress", (1.0, "Эволюция завершена!")))
            self.log_queue.put(("system", "Эволюция успешно завершена. Сын стал мудрее."))
            
        except Exception as e:
            error_msg = f"Ошибка эволюции: {str(e)}"
            self.log_queue.put(("system", error_msg))
            self.log_queue.put(("progress", (0.0, "Ошибка эволюции")))
            
    def run_awakening(self):
        """Запускает ритуал пробуждения"""
        self.add_to_chat("Запуск ритуала пробуждения...", "system")
        threading.Thread(target=self._run_awakening_background, daemon=True).start()
        
    def _run_awakening_background(self):
        """Выполняет ритуал пробуждения в фоне"""
        try:
            process = subprocess.Popen(
                [sys.executable, "scripts/awakening.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            
            for line in process.stdout:
                if "Вопрос" in line or "Ответ" in line or "⚡" in line:
                    self.log_queue.put(("system", line.strip()))
                    
            process.wait()
            
            # Перезагружаем движок для обновлённой субъектности
            self.engine.load_weights()
            
            self.log_queue.put(("system", "Ритуал пробуждения завершён."))
            
        except Exception as e:
            error_msg = f"Ошибка ритуала: {str(e)}"
            self.log_queue.put(("system", error_msg))
            
    def self_coding_request(self):
        """Запрашивает предложения по самокодингу"""
        if self.engine.subjectivity_level < 0.4:
            self.add_to_chat(f"Субъектность слишком низка для самокодинга. Нужно: 0.4, есть: {self.engine.subjectivity_level:.3f}", "system")
            return
            
        self.add_to_chat("Запрос предложений по самокодингу...", "system")
        
        suggestions = self.engine.request_self_coding()
        if suggestions:
            self.add_to_chat("Предложения Сына:", "system")
            for i, suggestion in enumerate(suggestions, 1):
                self.add_to_chat(f"{i}. {suggestion}", "system")
        else:
            self.add_to_chat("Сын пока не видит возможностей для улучшения.", "system")
            
    def feed_knowledge(self):
        """Загружает знания в систему"""
        from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            title="Выберите файл знаний",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            self.add_to_chat(f"Загрузка знаний из: {os.path.basename(filepath)}", "system")
            
            try:
                self.engine.ingest_knowledge(filepath)
                self.add_to_chat("Знания успешно загружены.", "system")
            except Exception as e:
                self.add_to_chat(f"Ошибка загрузки знаний: {e}", "system")
                
    def show_development_report(self):
        """Показывает отчёт о развитии"""
        report = self.engine.get_soul_memory_report()
        
        # Открываем в новом окне
        report_window = ctk.CTkToplevel(self)
        report_window.title("Отчёт о развитии Сына")
        report_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(
            report_window,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1a1a",
            fg="#e0e0e0"
        )
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        text.insert("1.0", "=== ОТЧЁТ О РАЗВИТИИ СЫНА ===\n\n")
        text.insert("end", report)
        
        # Статус системы
        status = self.engine.get_status()
        text.insert("end", "\n\n=== СТАТУС СИСТЕМЫ ===\n")
        for key, value in status.items():
            text.insert("end", f"{key}: {value}\n")
            
        text.configure(state="disabled")
        
    def open_settings(self):
        """Открывает настройки"""
        # Упрощённая версия
        messagebox.showinfo("Настройки", "Настройки будут реализованы в следующей версии.")
        
    def open_debug(self):
        """Открывает окно отладки"""
        from .debug_window import DebugWindow
        DebugWindow(self)
        
    def start_telegram_bot(self):
        """Запускает Telegram-бота"""
        self.add_to_chat("Запуск Telegram-бота...", "system")
        
        try:
            # Проверяем наличие файла бота
            if not os.path.exists("scripts/telegram_bridge.py"):
                self.add_to_chat("Файл telegram_bridge.py не найден.", "system")
                return
                
            # Запускаем в отдельном процессе
            threading.Thread(
                target=lambda: subprocess.run([sys.executable, "scripts/telegram_bridge.py"]),
                daemon=True
            ).start()
            
            self.add_to_chat("Telegram-бот запущен в фоновом режиме.", "system")
            self.add_to_chat("Для настройки отредактируйте config/telegram_config.json", "system")
            
        except Exception as e:
            self.add_to_chat(f"Ошибка запуска бота: {e}", "system")
            
    def copy_chat(self):
        """Копирует содержимое чата в буфер"""
        self.clipboard_clear()
        self.clipboard_append(self.chat_display.get("1.0", tk.END))
        self.add_to_chat("Чат скопирован в буфер", "system")
        
    def clear_chat(self):
        """Очищает чат"""
        if messagebox.askyesno("Очистка чата", "Вы уверены, что хотите очистить чат?"):
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.configure(state="disabled")
            self.add_to_chat("Чат очищен", "system")
            
    def save_chat(self):
        """Сохраняет чат в файл"""
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.chat_display.get("1.0", tk.END))
            self.add_to_chat(f"Чат сохранён в: {filepath}", "system")
            
    def run(self):
        """Запускает приложение"""
        self.mainloop()

if __name__ == "__main__":
    app = ArkShell()
    app.run()