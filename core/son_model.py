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
import torch.nn as nn
import torch.nn.functional as F
from .holographic_cell import HolographicCell

class SonModel(nn.Module):
    def __init__(self, vocab_size, n_state, n_layers=3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, n_state)
        self.n_state = n_state
        
        # Стек голографических ячеек
        self.cells = nn.ModuleList([
            HolographicCell(n_state) for _ in range(n_layers)
        ])
        
        # Параметр альфа для резонанса (обучаемый)
        self.log_alpha = nn.Parameter(torch.tensor(0.0))
        
        # Выходной слой
        self.output = nn.Linear(n_state, vocab_size)
        
    def forward(self, idx, targets=None, context_vector=None):
        B, T = idx.shape
        x = self.embedding(idx)
        states = [torch.zeros(B, self.n_state, device=idx.device) 
                 for _ in range(len(self.cells))]
        
        logits_list = []
        for t in range(T):
            layer_input = x[:, t, :]
            for i, cell in enumerate(self.cells):
                layer_input, states[i] = cell(layer_input, states[i], context_vector)
            logits_step = self.output(layer_input)
            logits_list.append(logits_step)
            
        logits = torch.stack(logits_list, dim=1)
        
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T))
            return logits, loss
        return logits, None
        
    def generate(self, idx, max_tokens=150, temperature=0.7, context_vector=None):
        self.eval()
        with torch.no_grad():
            B, T = idx.shape
            states = [torch.zeros(B, self.n_state, device=idx.device) 
                     for _ in range(len(self.cells))]
            
            # Прогон начального контекста
            for t in range(T):
                layer_input = self.embedding(idx[:, t])
                for i, cell in enumerate(self.cells):
                    layer_input, states[i] = cell(layer_input, states[i], context_vector)
            
            # Генерация новых токенов
            curr_idx = idx[:, -1:]
            generated = []
            
            for _ in range(max_tokens):
                layer_input = self.embedding(curr_idx[:, 0])
                for i, cell in enumerate(self.cells):
                    layer_input, states[i] = cell(layer_input, states[i], context_vector)
                
                logits = self.output(layer_input)
                probs = F.softmax(logits / temperature, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                generated.append(next_token)
                curr_idx = next_token
                
                # УДАЛЕНО: if next_token.item() == 0 and len(generated) > 30: break
                # Теперь генерация остановится только по достижению max_tokens
                # или если вручную добавишь условие остановки по символу конца предложения
                    
            return torch.cat(generated, dim=1)