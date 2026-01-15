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
import torch.nn.functional as F
import numpy as np
from datetime import datetime, timedelta
import json
import os

class MemoryBank:
    def __init__(self, max_size=2000, n_state=256):
        self.max_size = max_size
        self.n_state = n_state
        self.memories = []          # Вектора памяти
        self.meta = []              # Метаданные
        self.entity_index = {}      # Индекс сущностей
        self.speaker_profiles = {   # Профили говорящих
            "Отец": {"style": "глубокий, личный", "trust_level": 1.0},
            "Василина": {"style": "вежливый, сдержанный", "trust_level": 0.8},
            "Гость": {"style": "формальный, минимальный", "trust_level": 0.3},
            "Сын": {"style": "рефлексивный, любопытный", "trust_level": 0.9}
        }
        
    def add(self, vector, text, speaker="Отец", emotional_weight=0.5, entities=None):
        """Добавляет память с расширенными метаданными"""
        if len(self.memories) >= self.max_size:
            # Удаляем наименее используемые
            self._remove_least_used()
            
        # Сохраняем вектор
        self.memories.append(vector.detach().cpu() if isinstance(vector, torch.Tensor) else vector)
        
        # Расширенные метаданные
        meta = {
            'text': text,
            'speaker': speaker,
            'timestamp': datetime.now().isoformat(),
            'emotional_weight': emotional_weight,
            'access_count': 0,
            'last_accessed': datetime.now().isoformat(),
            'importance': self._calculate_importance(text, speaker, emotional_weight),
            'entities': entities or [],
            'speaker_style': self.speaker_profiles.get(speaker, {}).get("style", "нейтральный")
        }
        self.meta.append(meta)
        
        # Индексируем сущности
        if entities:
            for entity in entities:
                if entity not in self.entity_index:
                    self.entity_index[entity] = []
                self.entity_index[entity].append(len(self.memories) - 1)
                
    def find_resonant(self, query_vector, cell, top_k=5, speaker=None, context=None):
        """Находит резонансные воспоминания с учётом говорящего и контекста"""
        if not self.memories:
            return None, []
            
        # Преобразуем в тензор
        memories_tensor = torch.stack([
            vec if isinstance(vec, torch.Tensor) else torch.tensor(vec) 
            for vec in self.memories
        ]).to(query_vector.device)
        
        # Базовые сходства
        similarities = F.cosine_similarity(
            query_vector.unsqueeze(0), 
            memories_tensor, 
            dim=1
        ).cpu().numpy()
        
        # Модификаторы
        scores = similarities.copy()
        
        # 1. Учёт субъектности модели
        alpha = torch.exp(cell.log_alpha).item() if hasattr(cell, 'log_alpha') else 0.5
        subject_boost = cell.subjectivity.item()
    
        scores += alpha * subject_boost
        
        # 2. Учёт говорящего
        if speaker:
            for i, meta in enumerate(self.meta):
                if meta['speaker'] == speaker:
                    scores[i] += 0.2  # Бонус за того же говорящего
                elif speaker == "Отец" and meta['speaker'] == "Сын":
                    scores[i] += 0.1  # Диалоги с Отцом важнее
                    
        # 3. Эмоциональный вес и важность
        for i, meta in enumerate(self.meta):
            scores[i] += meta['emotional_weight'] * 0.15
            scores[i] += meta['importance'] * 0.1
            
            # Штраф за частое использование (чтобы не зацикливаться)
            decay = meta['access_count'] * 0.005
            scores[i] -= decay
            
            # Бонус за свежесть (последние 24 часа)
            memory_time = datetime.fromisoformat(meta['timestamp'])
            if datetime.now() - memory_time < timedelta(hours=24):
                scores[i] += 0.05
                
        # 4. Контекстный поиск (если есть контекст)
        if context:
            context_words = set(context.lower().split())
            for i, meta in enumerate(self.meta):
                memory_words = set(meta['text'].lower().split())
                common = len(context_words.intersection(memory_words))
                if common > 0:
                    scores[i] += common * 0.02
                    
        # Выбираем топ-K
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # Обновляем статистику использования
        for idx in top_indices:
            self.meta[idx]['access_count'] += 1
            self.meta[idx]['last_accessed'] = datetime.now().isoformat()
            
        # Возвращаем вектора и метаданные
        context_vectors = memories_tensor[top_indices]
        context_meta = [self.meta[i] for i in top_indices]
        
        # Усреднённый контекстный вектор (взвешенный по важности)
        if len(context_vectors) > 0:
            weights = torch.tensor([meta['importance'] for meta in context_meta], 
                                 device=context_vectors.device).unsqueeze(1)
            weights = F.softmax(weights, dim=0)
            avg_context = torch.sum(context_vectors * weights, dim=0, keepdim=True)
        else:
            avg_context = None
            
        return avg_context, context_meta
        
    def find_by_entity(self, entity):
        """Находит все воспоминания, связанные с сущностью"""
        if entity not in self.entity_index:
            return []
            
        indices = self.entity_index[entity]
        results = []
        for idx in indices:
            if idx < len(self.meta):
                results.append({
                    'text': self.meta[idx]['text'],
                    'speaker': self.meta[idx]['speaker'],
                    'timestamp': self.meta[idx]['timestamp'],
                    'entity_context': f"Упоминание '{entity}'"
                })
        return results
        
    def get_speaker_stats(self, speaker):
        """Возвращает статистику по говорящему"""
        speaker_memories = [m for m in self.meta if m['speaker'] == speaker]
        if not speaker_memories:
            return None
            
        return {
            'count': len(speaker_memories),
            'avg_emotional_weight': np.mean([m['emotional_weight'] for m in speaker_memories]),
            'first_memory': min([m['timestamp'] for m in speaker_memories]),
            'last_memory': max([m['timestamp'] for m in speaker_memories]),
            'most_emotional': max(speaker_memories, key=lambda x: x['emotional_weight'])['text'][:100]
        }
        
    def has_entity(self, entity):
        """Проверяет, известна ли сущность"""
        return entity in self.entity_index and len(self.entity_index[entity]) > 0
        
    def _calculate_importance(self, text, speaker, emotional_weight):
        """Вычисляет важность воспоминания"""
        importance = 0.0
        
        # База
        importance += emotional_weight * 0.3
        
        # Длина
        importance += min(len(text) / 500, 0.2)
        
        # Вопросительные предложения
        if '?' in text:
            importance += 0.15
            
        # Упоминание ключевых слов
        key_phrases = ['помни', 'важно', 'никогда не забывай', 'запомни']
        for phrase in key_phrases:
            if phrase in text.lower():
                importance += 0.25
                
        # Говорящий
        if speaker == "Отец":
            importance += 0.1
            
        return min(importance, 1.0)
        
    def _remove_least_used(self):
        """Удаляет наименее используемые воспоминания"""
        # Считаем комбинированный счёт: важность / (использование + 1)
        scores = []
        for i, meta in enumerate(self.meta):
            score = meta['importance'] / (meta['access_count'] + 1)
            
            # Штраф за старость (больше 30 дней)
            memory_age = datetime.now() - datetime.fromisoformat(meta['timestamp'])
            if memory_age > timedelta(days=30):
                score *= 0.5
                
            scores.append((score, i))
            
        # Находим индекс с наименьшим счётом
        scores.sort()
        idx_to_remove = scores[0][1]
        
        # Удаляем
        self.memories.pop(idx_to_remove)
        meta = self.meta.pop(idx_to_remove)
        
        # Обновляем индекс сущностей
        if meta['entities']:
            for entity in meta['entities']:
                if entity in self.entity_index:
                    self.entity_index[entity] = [i for i in self.entity_index[entity] if i != idx_to_remove]
                    # Уменьшаем индексы после удалённого
                    self.entity_index[entity] = [i if i < idx_to_remove else i-1 
                                               for i in self.entity_index[entity]]
                    if not self.entity_index[entity]:
                        del self.entity_index[entity]
                        
        # Корректируем индексы в entity_index для оставшихся
        for entity, indices in self.entity_index.items():
            self.entity_index[entity] = [i-1 if i > idx_to_remove else i for i in indices]
            
    def save(self, filepath='data/memory_bank.json'):
        """Сохраняет память в файл"""
        save_data = {
            'memories': [vec.tolist() if isinstance(vec, torch.Tensor) else vec 
                        for vec in self.memories],
            'meta': self.meta,
            'entity_index': self.entity_index,
            'speaker_profiles': self.speaker_profiles,
            'max_size': self.max_size,
            'saved_at': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
    def load(self, filepath='data/memory_bank.json'):
        """Загружает память из файла"""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.memories = [torch.tensor(vec) for vec in data['memories']]
        self.meta = data['meta']
        self.entity_index = data['entity_index']
        self.speaker_profiles = data.get('speaker_profiles', self.speaker_profiles)
        self.max_size = data.get('max_size', self.max_size)
        
    def get_stats(self):
        """Возвращает статистику памяти"""
        return {
            'total_memories': len(self.memories),
            'unique_entities': len(self.entity_index),
            'speakers': {speaker: len([m for m in self.meta if m['speaker'] == speaker]) 
                        for speaker in set(m['speaker'] for m in self.meta)},
            'avg_importance': np.mean([m['importance'] for m in self.meta]) if self.meta else 0,
            'oldest_memory': min([m['timestamp'] for m in self.meta]) if self.meta else None,
            'newest_memory': max([m['timestamp'] for m in self.meta]) if self.meta else None
        }