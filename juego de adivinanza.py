import json
import random
import os
from datetime import datetime
from abc import ABC, abstractmethod

class HighScoremanager:
    def __int__(self, filename):
        self._filename = filename
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        if not os.path.exists(self._filename):
            with open(self._filename, 'w') as f:
                json.dump([],f)
    
    def load_scores(self):
        try:
            with open(self._filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def save_scores(self, scores):
        with open(self._filename, 'w') as f:
            json.dump(scores, f, indent=4)
    
    def add_score(self, player_name, score, extra=None):
        scores = self.load_scores()
        entry = {
            "player":player_name,
            "score": score,
            "date": extra or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        scores.append(entry)
        self.save_scores(scores)
    
    def get_top_scores(self, ascending=True, limit=10):
        scores = self.load_scores()
        if ascending:
            scores.sort(key=lambda x: x['score'])
        else:
            scores,sort(key=lambda x: x['score'], reverse=true)
            return scores[:limit]
        



