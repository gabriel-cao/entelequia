"""
vocabulary.py - Análisis de riqueza de vocabulario
"""

import spacy
from typing import Dict


class VocabularyAnalyzer:
    """Análisis de diversidad y riqueza de vocabulario"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

    def calculate_vocabulary_richness(self, text: str) -> Dict[str, float]:
        """Calcular riqueza de vocabulario"""
        doc = self.nlp(text)
        words = [token.lemma_.lower() for token in doc if token.is_alpha]

        if not words:
            return {"type_token_ratio": 0, "hapax_legomena_ratio": 0, "unique_words": 0}

        unique_words = set(words)
        type_token_ratio = len(unique_words) / len(words)

        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        hapax = sum(1 for count in word_counts.values() if count == 1)
        hapax_ratio = hapax / len(words)

        return {
            "type_token_ratio": round(type_token_ratio, 4),
            "hapax_legomena_ratio": round(hapax_ratio, 4),
            "unique_words": len(unique_words),
            "total_words": len(words)
        }
