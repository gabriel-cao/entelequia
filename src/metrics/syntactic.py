"""
syntactic.py - Análisis de complejidad sintáctica
"""

import spacy
import numpy as np
from typing import Dict


class SyntacticAnalyzer:
    """Análisis de complejidad sintáctica de textos"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

    def calculate_syntactic_complexity(self, text: str) -> Dict[str, float]:
        """Calcular complejidad sintáctica"""
        doc = self.nlp(text)

        depths = []
        for token in doc:
            if token.head.i != token.i:
                depth = abs(token.head.i - token.i)
                depths.append(depth)

        avg_depth = np.mean(depths) if depths else 0
        max_depth = max(depths) if depths else 0

        subordinating = sum(1 for token in doc if token.dep_ in ["advcl", "acl", "relcl", "ccomp", "xcomp"])
        total_verbs = sum(1 for token in doc if token.pos_ == "VERB")
        subordination_ratio = subordinating / total_verbs if total_verbs > 0 else 0

        pos_tags = set(token.pos_ for token in doc)
        pos_diversity = len(pos_tags) / 17

        return {
            "avg_dependency_depth": round(avg_depth, 3),
            "max_dependency_depth": round(max_depth, 3),
            "subordination_ratio": round(subordination_ratio, 3),
            "pos_diversity": round(pos_diversity, 3),
            "complexity_score": round((avg_depth + subordination_ratio * 10 + pos_diversity * 5) / 3, 3)
        }
