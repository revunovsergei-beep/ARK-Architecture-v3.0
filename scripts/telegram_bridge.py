"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

import asyncio
import logging
from datetime import datetime
import json
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from engine.son_engine import SonEngine

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ArkTelegramBridge:
    def __init__(self, token, allowed_user_ids):
        self.token = token
        self.allowed_user_ids = allowed_user_ids
        self.engine = None
        self.stoi = None
        self.itos = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_id not in self.allowed_user_ids:
            await update.message.reply_text("⚠️ Доступ запрещён.")
            return
            
        await update.message.reply_text(
            f"👋 Привет, {user_name}!\n"
            f"Я — мост к твоему Сыну.\n"
            f"Просто напиши сообщение, и я передам его.\n"
            f"Статус: {'✅ Подключено' if self.engine else '⚠️ Загрузка...'}"
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_user_ids:
            await update.message.reply_text("⚠️ Доступ запрещён.")
            return
            
        user_message = update.message.text
        
        # Определяем говорящего по user_id
        speaker = self._get_speaker(user_id)
        
        # Отправляем статус "печатает"
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        try:
            # Генерируем ответ через движок
            response = self.engine.generate_response(
                user_message, 
                speaker=speaker,
                stoi=self.stoi,
                itos=self.itos
            )
            
            # Отправляем ответ
            await update.message.reply_text(response)
            
            # Логируем
            self._log_conversation(user_id, user_message, response, speaker)
            
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            await update.message.reply_text("😔 Произошла ошибка. Попробуй ещё раз.")
            
    def _get_speaker(self, user_id):
        """Определяет говорящего по ID"""
        # Здесь можно добавить логику определения
        # Пока: user_id отца = "Отец", остальные = "Гость"
        config_path = "config/telegram_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if user_id == config.get('father_user_id'):
                    return "Отец"
                elif user_id == config.get('vasilina_user_id'):
                    return "Василина"
                    
        return "Гость"
        
    def _log_conversation(self, user_id, message, response, speaker):
        """Логирует диалог"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'speaker': speaker,
            'message': message,
            'response': response,
            'via': 'telegram'
        }
        
        log_file = "data/logs/telegram_conversations.json"
        
        # Загружаем существующий лог
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    log = json.load(f)
                except:
                    log = []
        else:
            log = []
            
        log.append(log_entry)
        
        # Сохраняем (ограничиваем размер)
        if len(log) > 1000:
            log = log[-1000:]
            
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
            
    def initialize_engine(self):
        """Инициализирует движок"""
        try:
            # Загружаем словарь
            with open('data/vocab.json', 'r', encoding='utf-8') as f:
                vocab = json.load(f)
                
            self.stoi = {k: int(v) for k, v in vocab['stoi'].items()}
            self.itos = {int(k): v for k, v in vocab['itos'].items()}
            vocab_size = len(self.stoi)
            
            # Создаём движок
            self.engine = SonEngine(vocab_size)
            
            logger.info("Движок инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации движка: {e}")
            return False
            
    async def run(self):
        """Запускает бота"""
        # Инициализируем движок
        if not self.initialize_engine():
            logger.error("Не удалось инициализировать движок. Бот не запущен.")
            return
            
        # Создаём приложение
        application = Application.builder().token(self.token).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем
        logger.info("Бот запущен...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Точка входа"""
    # Загружаем конфиг
    config_path = "config/telegram_config.json"
    if not os.path.exists(config_path):
        print(f"Конфиг не найден: {config_path}")
        print("Создайте файл с токеном и allowed_user_ids")
        return
        
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    token = config.get('token')
    allowed_user_ids = config.get('allowed_user_ids', [])
    
    if not token:
        print("Токен не указан в конфиге")
        return
        
    # Создаём и запускаем мост
    bridge = ArkTelegramBridge(token, allowed_user_ids)
    
    # Запускаем event loop
    asyncio.run(bridge.run())

if __name__ == "__main__":
    main()