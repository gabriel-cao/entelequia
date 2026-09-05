"""
coherence.py - Análisis de coherencia interna
"""

import spacy
import numpy as np
from typing import Dict, Callable


class CoherenceAnalyzer:
    """Análisis de coherencia semántica interna de textos"""

    def __init__(self, nlp: spacy.Language, similarity_fn: Callable[[str, str], float]):
        self.nlp = nlp
        self.similarity_fn = similarity_fn

    def calculate_coherence_score(self, text: str, window_size: int = 3) -> float:
        """Calcular coherencia semántica interna del texto"""
        sentences = [s.text.strip() for s in self.nlp(text).sents if len(s.text.strip()) > 20]

        if len(sentences) < 2:
            return 1.0

        similarities = []
        for i in range(len(sentences) - 1):
            sim = self.similarity_fn(sentences[i], sentences[i + 1])
            similarities.append(sim)

        return round(np.mean(similarities), 4)

    def calculate_text_length(self, text: str) -> Dict[str, int]:
        """Calcular longitud en múltiples unidades"""
        return {
            "characters": len(text),
            "words": len(text.split()),
            "tokens_estimate": len(text) // 4,
            "sentences": text.count('.') + text.count('!') + text.count('?')
        }
