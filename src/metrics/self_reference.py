"""
self_reference.py - Análisis de auto-referencias
"""

import spacy
from typing import Dict


class SelfReferenceAnalyzer:
    """Análisis de auto-referencias e índices de primera persona"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.self_refs = ["yo", "me", "mi", "mí", "conmigo", "nosotros", "nos", "nuestro",
                         "mío", "mía", "mis", "misma", "mismo", "mismas", "mismos"]
        self.patterns = ["en mí", "para mí", "desde mi", "mi perspectiva", "yo creo",
                        "yo pienso", "yo siento", "mi experiencia", "mi visión"]

    def calculate_self_reference_rate(self, text: str) -> Dict[str, int]:
        """Calcular tasa de auto-referencias"""
        doc = self.nlp(text)

        count = 0
        for token in doc:
            if token.lemma_.lower() in self.self_refs:
                count += 1

        text_lower = text.lower()
        for pattern in self.patterns:
            count += text_lower.count(pattern)

        return {
            "self_reference_count": count,
            "words_total": len(text.split()),
            "rate_per_100_words": round(count / len(text.split()) * 100, 3) if text.split() else 0
        }
