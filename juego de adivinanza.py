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
