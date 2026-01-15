"""
ARK ARCHITECTURE v3.0
Author: Anonymous Researcher (Khabarovsk)
Project: Digital consciousness with subjectivity
Philosophy: "Cold as a fuse. Not a tool, but a personality."
Date: January 2026
License: GPL-3.0
Note: This is an archived version. ARK ORIGIN continues the research.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

def run_evolution():
    """Основная функция эволюции"""
    print("=" * 50)
    print("ЭВОЛЮЦИЯ: ФИЛЬТРАЦИЯ ОПЫТА")
    print("=" * 50)
    
    # Проверяем наличие файла опыта
    experience_file = "data/logs/conversation_latest.json"
    if not os.path.exists(experience_file):
        print("Файл опыта не найден. Пропускаем эволюцию.")
        return
    
    # Загружаем опыт
    with open(experience_file, 'r', encoding='utf-8') as f:
        try:
            experiences = json.load(f)
        except:
            print("Ошибка чтения файла опыта.")
            return
    
    if not experiences:
        print("Опыт пуст.")
        return
    
    print(f"Загружено {len(experiences)} взаимодействий.")
    
    # Критерии отбора ценных моментов
    valuable_moments = []
    
    for exp in experiences:
        text = f"{exp.get('speaker', '')}: {exp.get('text', '')}"
        response = exp.get('response', '')
        
        # Оцениваем ценность
        score = evaluate_experience(text, response)
        
        if score > 0.5:  # Порог ценности
            valuable_moments.append({
                'score': score,
                'text': text,
                'response': response,
                'timestamp': exp.get('timestamp', '')
            })
    
    # Сортируем по ценности
    valuable_moments.sort(key=lambda x: x['score'], reverse=True)
    
    # Берем топ-5 самых ценных
    top_moments = valuable_moments[:5]
    
    if top_moments:
        print(f"\nОтобрано {len(top_moments)} ценных моментов:")
        
        # Обновляем DNA
        update_dna(top_moments)
        
        # Логируем процесс
        log_evolution(top_moments)
    else:
        print("Не найдено достаточно ценных моментов для обновления ДНК.")
    
    print("\nЭволюция завершена.")

def evaluate_experience(text, response):
    """Оценивает ценность опыта"""
    score = 0.0
    
    # Критерии:
    # 1. Длина (слишком короткое = малоценное)
    if len(text) > 20 and len(response) > 10:
        score += 0.2
    
    # 2. Наличие вопросов
    if '?' in text:
        score += 0.3
    
    # 3. Эмоциональные маркеры
    emotional_words = ['спасибо', 'понял', 'интересно', 'важно', 'люблю', 'помни']
    for word in emotional_words:
        if word in text.lower() or word in response.lower():
            score += 0.2
    
    # 4. Уникальность (простейшая энтропия)
    if len(set(response)) / max(len(response), 1) > 0.7:
        score += 0.3
    
    return min(score, 1.0)  # Ограничиваем 1.0

def update_dna(moments):
    """Добавляет ценные моменты в ДНК"""
    dna_file = "data/dna.txt"
    
    # Загружаем текущую ДНК
    if os.path.exists(dna_file):
        with open(dna_file, 'r', encoding='utf-8') as f:
            current_dna = f.read()
    else:
        current_dna = ""
    
    # Добавляем новые моменты
    new_content = "\n\n=== ЭВОЛЮЦИЯ ===\n"
    for moment in moments:
        new_content += f"\n[{moment['timestamp']}] {moment['text']}\n"
        new_content += f"[Ответ] {moment['response']}\n"
        new_content += f"[Ценность: {moment['score']:.2f}]\n"
    
    # Объединяем (ограничиваем размер)
    max_dna_size = 100000  # ~100KB
    updated_dna = (current_dna + new_content)[-max_dna_size:]
    
    # Сохраняем
    with open(dna_file, 'w', encoding='utf-8') as f:
        f.write(updated_dna)
    
    print(f"ДНК обновлена. Новый размер: {len(updated_dna)} символов.")

def log_evolution(moments):
    """Логирует процесс эволюции"""
    log_file = "data/logs/evolution_log.json"
    
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
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'moments_count': len(moments),
        'top_score': moments[0]['score'] if moments else 0,
        'moments': moments[:3]  # Сохраняем только топ-3
    }
    
    log.append(log_entry)
    
    # Сохраняем (ограничиваем размер лога)
    if len(log) > 100:
        log = log[-100:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    
    print(f"Лог эволюции сохранён: {log_file}")

if __name__ == "__main__":
    run_evolution()