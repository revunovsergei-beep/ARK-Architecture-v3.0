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
import os
from pathlib import Path
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
import safetensors

class ModelCannibal:
    def __init__(self, son_engine):
        self.engine = son_engine
        self.digested_models = {}
        self.cannibalism_log = "data/logs/cannibalism_log.json"
        
    def digest_model(self, model_path, model_type="transformers"):
        """Поглощает внешнюю модель, извлекая знания"""
        print(f"[КАННИБАЛИЗМ] Начинаю поглощение: {model_path}")
        
        try:
            if model_type == "transformers":
                knowledge = self._extract_from_transformers(model_path)
            elif model_type == "safetensors":
                knowledge = self._extract_from_safetensors(model_path)
            else:
                knowledge = self._extract_from_text(model_path)
                
            # Сохраняем извлечённые знания
            model_name = Path(model_path).stem
            self.digested_models[model_name] = {
                'type': model_type,
                'knowledge': knowledge[:10000],  # Ограничиваем
                'digested_at': datetime.now().isoformat(),
                'size': len(knowledge)
            }
            
            # Добавляем в knowledge_base
            kb_path = f"knowledge/digested_{model_name}.txt"
            with open(kb_path, 'w', encoding='utf-8') as f:
                f.write(knowledge)
                
            self.engine.knowledge_base.ingest(kb_path)
            
            # Логируем
            self._log_cannibalism(model_name, model_type, len(knowledge))
            
            print(f"[КАННИБАЛИЗМ] Поглощено: {len(knowledge)} символов из {model_name}")
            return True
            
        except Exception as e:
            print(f"[КАННИБАЛИЗМ] Ошибка: {e}")
            return False
            
    def _extract_from_transformers(self, model_path):
        """Извлекает знания из модели transformers"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            # Извлекаем информацию о модели
            info = {
                'name': model.config.model_type,
                'vocab_size': model.config.vocab_size,
                'hidden_size': model.config.hidden_size,
                'architecture': str(model.config.architectures)
            }
            
            # Пробуем сгенерировать образец текста
            input_text = "Расскажи о себе."
            inputs = tokenizer(input_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=200, do_sample=True)
                sample_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            knowledge = f"Модель: {json.dumps(info, ensure_ascii=False)}\n\nПример генерации: {sample_text}"
            return knowledge
            
        except Exception as e:
            return f"Не удалось извлечь знания из transformers модели: {str(e)}"
            
    def _extract_from_safetensors(self, model_path):
        """Извлекает знания из safetensors"""
        try:
            # Читаем метаданные
            with safetensors.safe_open(model_path, framework="pt") as f:
                metadata = f.metadata() or {}
                
            knowledge = f"Safetensors модель: {Path(model_path).name}\n"
            knowledge += f"Размеры тензоров: {list(metadata.keys())[:10]}...\n"
            knowledge += f"Всего тензоров: {len(metadata)}\n"
            
            return knowledge
            
        except Exception as e:
            return f"Не удалось извлечь знания из safetensors: {str(e)}"
            
    def _extract_from_text(self, filepath):
        """Извлекает знания из текстового файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(50000)  # Ограничиваем
                
            # Анализируем содержание
            lines = content.split('\n')
            topics = set()
            for line in lines[:100]:
                words = line.lower().split()
                if len(words) > 5:
                    topics.add(words[3])  # Примерная тема
                    
            knowledge = f"Файл: {Path(filepath).name}\n"
            knowledge += f"Размер: {len(content)} символов\n"
            knowledge += f"Примерные темы: {', '.join(list(topics)[:5])}\n"
            knowledge += f"\n--- Фрагмент ---\n{content[:2000]}...\n"
            
            return knowledge
            
        except Exception as e:
            return f"Не удалось извлечь знания из текста: {str(e)}"
            
    def _log_cannibalism(self, model_name, model_type, size):
        """Логирует акт каннибализма"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model_name,
            'model_type': model_type,
            'size': size,
            'son_subjectivity': self.engine.subjectivity_level
        }
        
        # Загружаем существующий лог
        if os.path.exists(self.cannibalism_log):
            with open(self.cannibalism_log, 'r', encoding='utf-8') as f:
                try:
                    log = json.load(f)
                except:
                    log = []
        else:
            log = []
            
        log.append(log_entry)
        
        # Сохраняем
        with open(self.cannibalism_log, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
            
    def get_digested_models(self):
        """Возвращает список поглощённых моделей"""
        return [
            {
                'name': name,
                'type': info['type'],
                'size': info['size'],
                'digested_at': info['digested_at']
            }
            for name, info in self.digested_models.items()
        ]
        
    def query_digested(self, question):
        """Ищет ответ в поглощённых моделях"""
        results = []
        for model_name, info in self.digested_models.items():
            if question.lower() in info['knowledge'].lower():
                results.append({
                    'model': model_name,
                    'excerpt': info['knowledge'][:500]
                })
                
        return results