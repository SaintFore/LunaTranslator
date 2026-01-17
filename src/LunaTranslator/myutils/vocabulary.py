import json
import os
import time
import csv
from qtsymbols import QObject, pyqtSignal
import gobject

class VocabularyManager(QObject):
    vocabulary_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.filename = gobject.getconfig("vocabulary.json")
        self.words = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.words = json.load(f)
            else:
                self.words = {}
        except:
            self.words = {}

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving vocabulary: {e}")

    def add_word(self, word, sentence="", note="", context=None):
        if not word:
            return
        
        word = word.lower()
        entry = {
            "word": word,
            "sentence": sentence,
            "note": note,
            "context": context,
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.words[word] = entry
        self.save()
        self.vocabulary_changed.emit()

    def remove_word(self, word):
        word = word.lower()
        if word in self.words:
            del self.words[word]
            self.save()
            self.vocabulary_changed.emit()

    def is_starred(self, word):
        if not word:
            return False
        return word.lower() in self.words

    def get_word(self, word):
        if not word:
            return None
        return self.words.get(word.lower())

    def get_all_words(self):
        # Return list sorted by timestamp descending
        return sorted(self.words.values(), key=lambda x: x.get('timestamp', 0), reverse=True)


    def export_to_csv(self, path):
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['word', 'sentence']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

                writer.writeheader()
                for word_data in self.words.values():
                    writer.writerow(word_data)
            return True
        except Exception as e:
            print(f"Error exporting vocabulary: {e}")
            return False
