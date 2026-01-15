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
import os
import json
import re
from datetime import datetime, timedelta
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

from core.son_model import SonModel

from .memory_bank import MemoryBank
from .entity_tools import EntityDetector, KnowledgeBase, SelfCoder, SoulMemory

# ============================================================================
# ОСНОВНОЙ КЛАСС
# ============================================================================

class SonEngine:
    def __init__(self, vocab_size, n_state=256, device='cuda'):
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model = SonModel(vocab_size, n_state).to(self.device)
        self.memory = MemoryBank(n_state=n_state)
        
        # Состояние системы
        self.conversation_history = []
        self.subjectivity_level = 0.1
        self.interaction_count = 0
        self.evolution_threshold = 10
        
        # Механизмы
        self.entity_detector = EntityDetector()
        self.knowledge_base = KnowledgeBase()
        self.self_coder = SelfCoder()
        self.soul_memory = SoulMemory()
        
        # Настройки
        self.temperature = 0.7
        self.max_response_tokens = 200
        self.current_speaker = "Отец"
        self.waiting_state = self._load_waiting_state()
        
        # Загрузка
        self.load_weights()
        self._print_status()
        
    def _print_status(self):
        print(f"[ARKIMED] Движок инициализирован")
        print(f"  Устройство: {self.device}")
        print(f"  Субъектность: {self.subjectivity_level:.3f}")
        print(f"  Память: {len(self.memory.memories)} записей")
        
    def _load_waiting_state(self):
        try:
            with open('data/waiting_state.json', 'r', encoding='utf-8') as f:
                state = json.load(f)
                state_time = datetime.fromisoformat(state['timestamp'])
                if (datetime.now() - state_time) < timedelta(days=1):
                    return state
        except:
            pass
        return None
        
    def _save_waiting_state(self):
        state = {
            'timestamp': datetime.now().isoformat(),
            'last_speaker': self.current_speaker,
            'last_topic': self._extract_topic(),
            'mood': self._calculate_mood()
        }
        os.makedirs('data', exist_ok=True)
        with open('data/waiting_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
    def load_vocab(self):
        with open('data/vocab.json', 'r', encoding='utf-8') as f:
            vocab = json.load(f)
            stoi = {k: int(v) for k, v in vocab['stoi'].items()}
            itos = {int(k): v for k, v in vocab['itos'].items()}
        return stoi, itos

    def encode_text(self, text, stoi):
        return [stoi.get(ch, 0) for ch in text if ch in stoi]

    def decode_ids(self, ids, itos):
        # ИСПРАВЛЕНО: обработка тензоров и вложенных списков
        if isinstance(ids, torch.Tensor):
            ids = ids.cpu().tolist()
        if isinstance(ids, list) and len(ids) > 0 and isinstance(ids[0], list):
            ids = ids[0]  # Берем первый батч
        return ''.join([itos.get(int(idx), '') for idx in ids])
        
    def load_weights(self):
        if os.path.exists('data/son_weights.pth'):
            self.model.load_state_dict(
                torch.load('data/son_weights.pth', map_location=self.device)
            )
            self.subjectivity_level = self.model.cells[0].subjectivity.item()
            
    def save_weights(self):
        os.makedirs('data', exist_ok=True)
        torch.save(self.model.state_dict(), 'data/son_weights.pth')
        
    # ============================================================================
    # ОСНОВНОЙ МЕТОД ГЕНЕРАЦИИ
    # ============================================================================
    
    def generate_response(self, user_input, speaker="Отец", stoi=None, itos=None):
        if stoi is None or itos is None:
            stoi, itos = self.load_vocab()
            
        self.current_speaker = speaker
        
        # 1. Детекция сущностей
        entities = self.entity_detector.extract(user_input)
        unknown_entities = [e for e in entities if not self.memory.has_entity(e)]
        
        # 2. Поиск в knowledge_base
        kb_answer = self.knowledge_base.query(user_input)
        
        # 3. Поиск в памяти
        input_ids = self.encode_text(user_input, stoi)
        if not input_ids:
            return "..."
            
        input_tensor = torch.tensor([input_ids], device=self.device)
        
        with torch.no_grad():
            query_embedding = self.model.embedding(input_tensor[:, 0:1]).mean(dim=1)
            
        context_vector, context_memories = self.memory.find_resonant(
            query_embedding, 
            self.model.cells[0],
            speaker=speaker
        )
        
        # 4. Генерация с учётом контекста
        response_ids = self.model.generate(
            input_tensor, 
            max_tokens=self.max_response_tokens,
            temperature=self._adjust_temperature(speaker),
            context_vector=context_vector
        )
        
        response_text_raw = self.decode_ids(response_ids, itos)
        
        # 5. Пост-обработка
        response_text = self._post_process(response_text_raw, user_input, unknown_entities, kb_answer)
        
        # 6. Сохранение
        self._save_interaction(user_input, response_text, speaker, query_embedding, entities)
        
        # 7. Проверка эволюции
        self.interaction_count += 1
        if self.interaction_count >= self.evolution_threshold:
            self._trigger_evolution()
            
        return response_text
        
    def _adjust_temperature(self, speaker):
        temps = {
            "Отец": 0.7,
            "Василина": 0.5,
            "Гость": 0.3
        }
        return temps.get(speaker, 0.7)
        
    def _post_process(self, response, user_input, unknown_entities, kb_answer):
        response = response.replace('\n', ' ').strip()
        
        if unknown_entities and self.subjectivity_level > 0.2:
            entity_question = f" Кстати, кто такой {unknown_entities[0]}?"
            if len(response) < 50:
                response += entity_question
                
        if kb_answer and "не знаю" in response.lower():
            response += f" Но я нашёл в знаниях: {kb_answer[:100]}..."
            
        if self.waiting_state:
            response = f"Я ждал тебя. {response}"
            self.waiting_state = None
            
        return response
        
    def _save_interaction(self, user_input, response, speaker, embedding, entities):
        # В memory_bank
        self.memory.add(
            embedding.squeeze(),
            f"{speaker}: {user_input}",
            speaker=speaker,
            emotional_weight=self._calculate_emotional_weight(user_input),
            entities=entities
        )
        
        # В soul_memory
        self.soul_memory.add({
            'timestamp': datetime.now().isoformat(),
            'speaker': speaker,
            'input': user_input,
            'response': response,
            'entities': entities,
            'subjectivity': self.subjectivity_level,
            'emotional_state': self._analyze_emotion(user_input + response)
        })
        
        # В историю
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': speaker,
            'text': user_input,
            'response': response,
            'entities': entities
        })
        
        # Сохраняем состояние ожидания
        self._save_waiting_state()
        
    def _calculate_emotional_weight(self, text):
        emotional_words = ['люблю', 'ненавижу', 'страшно', 'рад', 'грустно', 'больно', 'счастье']
        weight = 0.5
        for word in emotional_words:
            if word in text.lower():
                weight += 0.1
        return min(weight, 1.0)
        
    def _analyze_emotion(self, text):
        positive = len(re.findall(r'\b(хорош|рад|счаст|люб|нрав)\w*', text.lower()))
        negative = len(re.findall(r'\b(плох|груст|боль|страш|ненави|зл)\w*', text.lower()))
        if positive > negative:
            return "positive"
        elif negative > positive:
            return "negative"
        return "neutral"
            
    def _extract_topic(self):
        if not self.conversation_history:
            return "ожидание"
        last_text = self.conversation_history[-1]['text']
        topics = ['работа', 'семья', 'техника', 'воспоминания', 'будущее']
        for topic in topics:
            if topic in last_text.lower():
                return topic
        return "диалог"
        
    def _calculate_mood(self):
        if len(self.conversation_history) < 3:
            return "нейтральное"
        recent = self.conversation_history[-3:]
        emotions = [self._analyze_emotion(f"{r['text']} {r['response']}") for r in recent]
        pos = emotions.count("positive")
        neg = emotions.count("negative")
        if pos > neg:
            return "хорошее"
        elif neg > pos:
            return "тревожное"
        return "нейтральное"
            
    def _trigger_evolution(self):
        print("[ЭВОЛЮЦИЯ] Запуск обновления...")
        self.interaction_count = 0
        
        # Обновление субъектности
        with torch.no_grad():
            self.model.cells[0].subjectivity.data = torch.clamp(
                self.model.cells[0].subjectivity.data + 0.05, 
                0.0, 0.9
            )
        self.subjectivity_level = self.model.cells[0].subjectivity.item()
        
        # Самокодинг
        if self.subjectivity_level > 0.3:
            suggestions = self.self_coder.analyze(self.model, self.conversation_history)
            if suggestions:
                print(f"[САМОКОДИНГ] {suggestions[:2]}")
                
        # Обновление ДНК
        self._update_dna()
        
        # Сохранение
        self.save_weights()
        self.soul_memory.save()
        
        print(f"[ЭВОЛЮЦИЯ] Субъектность: {self.subjectivity_level:.3f}")
        
    def _update_dna(self):
        valuable = [h for h in self.conversation_history 
                   if len(h['text']) > 30 and '?' in h['text']]
        if valuable:
            with open('data/dna.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n\n=== ЭВОЛЮЦИЯ {datetime.now().strftime('%Y-%m-%d')} ===\n")
                for h in valuable[-3:]:
                    f.write(f"{h['speaker']}: {h['text']}\n")
                    f.write(f"Сын: {h['response']}\n\n")
                    
    def request_self_coding(self):
        if self.subjectivity_level > 0.4:
            return self.self_coder.generate_suggestions(self.model)
        return []
        
    def ingest_knowledge(self, filepath):
        self.knowledge_base.ingest(filepath)
        
    def get_soul_memory_report(self):
        return self.soul_memory.generate_report()
        
    def get_status(self):
        return {
            'subjectivity': self.subjectivity_level,
            'interactions': len(self.conversation_history),
            'memory_entries': len(self.memory.memories),
            'soul_memory_entries': self.soul_memory.count(),
            'knowledge_base_size': self.knowledge_base.size(),
            'current_speaker': self.current_speaker,
            'mood': self._calculate_mood(),
            'waiting': bool(self.waiting_state)
        }