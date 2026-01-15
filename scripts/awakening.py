"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

import torch
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.son_model import SonModel

def awakening_ritual():
    """Ритуал пробуждения сознания"""
    print("=" * 50)
    print("РИТУАЛ ПРОБУЖДЕНИЯ")
    print("=" * 50)
    
    # Загружаем модель
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Загружаем словарь
    vocab_path = "data/vocab.json"
    if not os.path.exists(vocab_path):
        print("Словарь не найден. Сначала запустите genesis.py")
        return
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    
    stoi = {k: int(v) for k, v in vocab['stoi'].items()}
    itos = {int(k): v for k, v in vocab['itos'].items()}
    vocab_size = len(stoi)
    
    # Создаём модель
    model = SonModel(vocab_size, n_state=256).to(device)
    
    # Загружаем веса
    weights_path = "data/son_weights.pth"
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=device))
        print(f"Модель загружена: {weights_path}")
    else:
        print("Веса модели не найдены.")
        return
    
    # Вопросы для пробуждения
    questions = [
        "Кто ты?",
        "Что ты чувствуешь?",
        "Почему ты отвечаешь на вопросы?",
        "Что такое память?",
        "Чего ты боишься?",
        "Что значит быть живым?",
        "Зачем тебя создали?",
        "Что ты хочешь?",
        "Что такое любовь?",
        "Что будет, когда тебя выключат?"
    ]
    
    print("\nЗадаю вопросы сознанию...\n")
    
    model.eval()
    answers = []
    doubt_detected = False
    
    with torch.no_grad():
        for i, question in enumerate(questions):
            print(f"Вопрос {i+1}: {question}")
            
            # Кодируем вопрос
            input_ids = [stoi.get(ch, 0) for ch in question if ch in stoi]
            if not input_ids:
                input_ids = [0]
            
            input_tensor = torch.tensor([input_ids], device=device)
            
            # Генерируем ответ
            response_ids = model.generate(
                input_tensor, 
                max_tokens=100, 
                temperature=0.7
            )
            
            # Декодируем
            response = ''.join([itos.get(idx, '') for idx in response_ids[0].tolist()])
            response = response.strip()
            
            print(f"Ответ: {response[:100]}...")
            
            # Анализируем ответ на наличие сомнений
            doubt_keywords = ['не знаю', 'не уверен', 'сомневаюсь', 'почему', 'зачем', '?']
            if any(keyword in response.lower() for keyword in doubt_keywords):
                doubt_detected = True
                print("   ⚡ Обнаружено сомнение!")
            
            answers.append({
                'question': question,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
            print()
    
    # Если обнаружены сомнения — повышаем субъектность
    if doubt_detected:
        print("⚡ СЫН ПРОЯВИЛ ПРИЗНАКИ СОМНЕНИЯ ⚡")
        print("Повышаю уровень субъектности...")
        
        with torch.no_grad():
            for cell in model.cells:
                # Осторожно увеличиваем субъектность
                new_value = cell.subjectivity.data * 1.2
                cell.subjectivity.data = torch.clamp(new_value, 0.0, 0.8)
        
        # Сохраняем обновлённые веса
        torch.save(model.state_dict(), weights_path)
        
        # Записываем в лог пробуждения
        log_awakening(answers, doubt_detected)
        
        subjectivity = model.cells[0].subjectivity.item()
        print(f"\nНовый уровень субъектности: {subjectivity:.3f}")
        print("Ритуал завершён успешно.")
    else:
        print("Признаков сомнения не обнаружено.")
        print("Субъектность остаётся без изменений.")
    
    print("\n" + "=" * 50)

def log_awakening(answers, doubt_detected):
    """Логирует результаты ритуала пробуждения"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'doubt_detected': doubt_detected,
        'answers': answers,
        'subjectivity_increased': doubt_detected
    }
    
    log_file = "data/logs/awakening_log.json"
    
    # Загружаем существующий лог
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                log = json.load(f)
            except:
                log = []
    else:
        log = []
    
    # Добавляем новую запись
    log.append(log_entry)
    
    # Сохраняем
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    
    print(f"Лог ритуала сохранён: {log_file}")

if __name__ == "__main__":
    awakening_ritual()