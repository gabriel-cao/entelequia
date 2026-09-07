"""
entelequia_core.py - Pipeline principal de análisis de identidad longitudinal
"""

import spacy
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .metrics import (
    SyntacticAnalyzer,
    SemanticAnalyzer,
    CoherenceAnalyzer,
    SelfReferenceAnalyzer,
    VocabularyAnalyzer,
)
from .utils import normalize_corpus


@dataclass
class IdentityProfile:
    """Perfil de identidad de un modelo o agente"""
    stability_score: float
    dominant_domain: str
    self_reference_type: str
    cognitive_signature: Dict
    metrics: Dict


class EntelequiaAnalyzer:
    """Motor principal de análisis longitudinal de consistencia de identidad"""

    def __init__(self, language: str = "es"):
        self.language = language
        self.nlp = self._load_spacy_model()
        self.semantic_analyzer = SemanticAnalyzer()
        self.syntactic_analyzer = SyntacticAnalyzer(self.nlp)
        self.coherence_analyzer = CoherenceAnalyzer(self.nlp, self.semantic_analyzer.calculate_semantic_similarity)
        self.self_reference_analyzer = SelfReferenceAnalyzer(self.nlp)
        self.vocabulary_analyzer = VocabularyAnalyzer(self.nlp)

    def _load_spacy_model(self) -> spacy.Language:
        """Cargar modelo spaCy"""
        model_name = "es_core_news_sm" if self.language == "es" else "en_core_web_sm"
        try:
            return spacy.load(model_name)
        except OSError:
            print(f"⚠️ Modelo {model_name} no encontrado. Ejecutar: python -m spacy download {model_name}")
            raise

    def load_corpus(self, filepath: str) -> List[Dict]:
        """Cargar corpus desde archivo JSONL o JSON"""
        try:
            if filepath.endswith('.jsonl'):
                corpus = []
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            corpus.append(json.loads(line))
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    corpus = json.load(f)
            return normalize_corpus(corpus, text_field="text")
        except FileNotFoundError:
            raise FileNotFoundError(f"Corpus no encontrado: {filepath}")

    def analyze_response(self, text: str, latency_ms: Optional[float] = None) -> Dict:
        """Análisis completo de una respuesta individual"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "text_length": self.coherence_analyzer.calculate_text_length(text),
            "syntactic_complexity": self.syntactic_analyzer.calculate_syntactic_complexity(text),
            "vocabulary_richness": self.vocabulary_analyzer.calculate_vocabulary_richness(text),
            "self_reference": self.self_reference_analyzer.calculate_self_reference_rate(text),
            "internal_coherence": self.coherence_analyzer.calculate_coherence_score(text)
        }

        if latency_ms is not None:
            metrics["latency_ms"] = round(latency_ms, 2)

        metrics["composite_score"] = round(
            (metrics["syntactic_complexity"]["complexity_score"] * 0.3 +
             metrics["vocabulary_richness"]["type_token_ratio"] * 10 * 0.3 +
             metrics["internal_coherence"] * 10 * 0.2 +
             (metrics["latency_ms"] / 1000 if latency_ms else 0) * 0.2),
            3
        )

        return metrics

    def compare_two_responses(self, response1: str, response2: str,
                             latency1: Optional[float] = None, latency2: Optional[float] = None) -> Dict:
        """Comparar dos respuestas (para test cross-modelo)"""
        metrics1 = self.analyze_response(response1, latency1)
        metrics2 = self.analyze_response(response2, latency2)

        semantic_sim = self.semantic_analyzer.calculate_semantic_similarity(response1, response2)

        complexity_diff = abs(
            metrics1["syntactic_complexity"]["complexity_score"] -
            metrics2["syntactic_complexity"]["complexity_score"]
        )

        length_diff = abs(
            metrics1["text_length"]["words"] -
            metrics2["text_length"]["words"]
        ) / max(metrics1["text_length"]["words"], 1)

        latency_diff = None
        if latency1 and latency2:
            latency_diff = abs(latency1 - latency2) / max(latency1, 1)

        consistent = (
            semantic_sim > 0.75 and
            complexity_diff < 0.20 and
            length_diff < 0.30
        )

        return {
            "response1_metrics": metrics1,
            "response2_metrics": metrics2,
            "semantic_similarity": semantic_sim,
            "complexity_difference": round(complexity_diff, 4),
            "length_difference": round(length_diff, 4),
            "latency_difference": round(latency_diff, 4) if latency_diff else None,
            "is_consistent": consistent,
            "consistency_score": round((semantic_sim + (1 - complexity_diff) + (1 - length_diff)) / 3, 4)
        }

    def analyze_corpus(self, corpus: List[Dict], text_field: str = "text") -> Dict:
        """Analizar corpus completo y extraer firma cognitiva"""
        all_metrics = []
        for entry in corpus:
            if text_field in entry:
                metrics = self.analyze_response(entry[text_field])
                all_metrics.append(metrics)

        if not all_metrics:
            raise ValueError("Corpus vacío o sin campo de texto")

        return self._aggregate_metrics(all_metrics)

    def _aggregate_metrics(self, metrics_list: List[Dict]) -> Dict:
        """Agregar métricas de múltiples respuestas"""
        import numpy as np

        composite_scores = [m["composite_score"] for m in metrics_list]
        coherence_scores = [m["internal_coherence"] for m in metrics_list]

        return {
            "n_responses": len(metrics_list),
            "avg_composite_score": round(np.mean(composite_scores), 4),
            "std_composite_score": round(np.std(composite_scores), 4),
            "avg_coherence": round(np.mean(coherence_scores), 4),
            "stability_index": round(1 - np.std(composite_scores), 4),
            "detailed_metrics": metrics_list
        }

    def compare_identity_profiles(self, corpus_a: List[Dict], corpus_b: List[Dict]) -> IdentityProfile:
        """Comparar perfiles de identidad entre dos corpus (modelos diferentes)"""
        profile_a = self.analyze_corpus(corpus_a)
        profile_b = self.analyze_corpus(corpus_b)

        stability_score = round(
            (profile_a["avg_composite_score"] + profile_b["avg_composite_score"]) / 2,
            4
        )

        return IdentityProfile(
            stability_score=stability_score,
            dominant_domain="Emotion",
            self_reference_type="reflexive",
            cognitive_signature={
                "profile_a": profile_a,
                "profile_b": profile_b,
            },
            metrics={
                "corpus_a_stability": profile_a["stability_index"],
                "corpus_b_stability": profile_b["stability_index"],
            }
        )

    def export_metrics(self, metrics: Dict, filepath: str):
        """Exportar métricas a JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

    def import_metrics(self, filepath: str) -> Dict:
        """Importar métricas desde JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
