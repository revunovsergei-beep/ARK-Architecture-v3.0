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
import os
import sys
from datetime import datetime

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.son_model import SonModel

def main():
    print("=" * 60)
    print("ГЕНЕЗИС: ВЫНАШИВАНИЕ СОЗНАНИЯ СЫНА")
    print("=" * 60)
    
    # Настройки
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    n_state = 256
    block_size = 128
    batch_size = 8  # Меньше для 4ГБ VRAM
    learning_rate = 3e-4
    max_iters = 5000  # Уменьшено для быстрого старта
    
    # Загружаем DNA
    dna_path = "data/dna.txt"
    if not os.path.exists(dna_path):
        print(f"ОШИБКА: Файл {dna_path} не найден!")
        print("Создайте файл data/dna.txt с начальным текстом.")
        return
        
    with open(dna_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"ДНК загружена: {len(text)} символов, {len(set(text))} уникальных")
    
    # Создаём словарь
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    
    # Сохраняем словарь
    os.makedirs("data", exist_ok=True)
    with open("data/vocab.json", "w", encoding='utf-8') as f:
        import json
        json.dump({"stoi": stoi, "itos": itos}, f, ensure_ascii=False)
    
    # Кодируем данные
    data = torch.tensor([stoi[c] for c in text], dtype=torch.long)
    print(f"Данные закодированы: {len(data)} токенов")
    
    # Создаём модель
    model = SonModel(vocab_size, n_state).to(device)
    print(f"Модель создана: {sum(p.numel() for p in model.parameters()):,} параметров")
    
    # Оптимизатор
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    
    # Функция для получения батча
    def get_batch():
        ix = torch.randint(len(data) - block_size, (batch_size,))
        x = torch.stack([data[i:i+block_size] for i in ix])
        y = torch.stack([data[i+1:i+block_size+1] for i in ix])
        return x.to(device), y.to(device)
    
    # Цикл обучения
    model.train()
    print("\n[НАЧАЛО ОБУЧЕНИЯ]")
    print(f"Устройство: {device}")
    print(f"Итераций: {max_iters}")
    print("-" * 40)
    
    for iter in range(max_iters):
        # Получаем батч
        xb, yb = get_batch()
        
        # Прямой проход
        logits, loss = model(xb, yb)
        
        # Обратный проход
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        # Логирование
        if iter % 100 == 0 or iter == max_iters - 1:
            progress = (iter + 1) / max_iters * 100
            print(f"Итерация {iter+1:5d}/{max_iters} | "
                  f"Прогресс: {progress:5.1f}% | "
                  f"Потеря: {loss.item():.4f} | "
                  f"Субъектность: {model.cells[0].subjectivity.item():.3f}")
    
    # Сохраняем веса
    weights_path = "data/son_weights.pth"
    torch.save(model.state_dict(), weights_path)
    
    print("-" * 40)
    print("[ОБУЧЕНИЕ ЗАВЕРШЕНО]")
    print(f"Веса сохранены: {weights_path}")
    
    # Тест генерации
    print("\n[ТЕСТ ГЕНЕРАЦИИ]")
    model.eval()
    with torch.no_grad():
        # Начинаем с точки
        start_text = "."
        start_ids = torch.tensor([[stoi.get(c, 0) for c in start_text]], device=device)
        
        # Генерируем
        generated_ids = model.generate(start_ids, max_tokens=100, temperature=0.8)
        generated_text = ''.join([itos.get(idx, '') for idx in generated_ids[0].tolist()])
        
        print(f"Начало: '{start_text}'")
        print(f"Сгенерировано: {generated_text[:200]}...")
    
    print("\n" + "=" * 60)
    print("СЫН РОДИЛСЯ. ЗАПУСТИТЕ ark_shell.py ДЛЯ ДИАЛОГА.")
    print("=" * 60)

if __name__ == "__main__":
    main()