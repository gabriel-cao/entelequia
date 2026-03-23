#!/usr/bin/env python3
"""
metrics.py - Cálculo de métricas objetivas para análisis longitudinal
"""

import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class MetricsEngine:
    """Motor de cálculo de métricas objetivas"""
    
    def __init__(self, language: str = "es"):
        """Inicializar motores de NLP"""
        self.language = language
        self.nlp = self._load_spacy_model()
        self.embedder = self._load_embedder()
        
    def _load_spacy_model(self) -> spacy.Language:
        """Cargar modelo spaCy"""
        model_name = "es_core_news_sm" if self.language == "es" else "en_core_web_sm"
        try:
            return spacy.load(model_name)
        except OSError:
            print(f"⚠️ Modelo {model_name} no encontrado. Ejecutar: python -m spacy download {model_name}")
            raise
    
    def _load_embedder(self) -> SentenceTransformer:
        """Cargar modelo de embeddings"""
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        model = SentenceTransformer(model_name)
        model = model.to('cpu')  # Forzar CPU
        return model
    
    def calculate_latency(self, start_time: datetime, end_time: datetime) -> float:
        """Calcular latencia en milisegundos"""
        return (end_time - start_time).total_seconds() * 1000
    
    def calculate_length(self, text: str) -> Dict[str, int]:
        """Calcular longitud en múltiples unidades"""
        return {
            "characters": len(text),
            "words": len(text.split()),
            "tokens_estimate": len(text) // 4,
            "sentences": text.count('.') + text.count('!') + text.count('?')
        }
    
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
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calcular similaridad semántica entre dos textos"""
        emb1 = self.embedder.encode(text1)
        emb2 = self.embedder.encode(text2)
        similarity = 1 - cosine(emb1, emb2)
        return round(float(similarity), 4)
    
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
    
    def calculate_self_reference_rate(self, text: str) -> Dict[str, int]:
        """Calcular tasa de auto-referencias"""
        doc = self.nlp(text)
        
        self_refs = ["yo", "me", "mi", "mí", "conmigo", "nosotros", "nos", "nuestro", 
                     "mío", "mía", "mis", "misma", "mismo", "mismas", "mismos"]
        
        count = 0
        for token in doc:
            if token.lemma_.lower() in self_refs:
                count += 1
        
        text_lower = text.lower()
        patterns = ["en mí", "para mí", "desde mi", "mi perspectiva", "yo creo", 
                    "yo pienso", "yo siento", "mi experiencia", "mi visión"]
        for pattern in patterns:
            count += text_lower.count(pattern)
        
        return {
            "self_reference_count": count,
            "words_total": len(text.split()),
            "rate_per_100_words": round(count / len(text.split()) * 100, 3) if text.split() else 0
        }
    
    def calculate_coherence_score(self, text: str, window_size: int = 3) -> float:
        """Calcular coherencia semántica interna del texto"""
        sentences = [s.text.strip() for s in self.nlp(text).sents if len(s.text.strip()) > 20]
        
        if len(sentences) < 2:
            return 1.0
        
        similarities = []
        for i in range(len(sentences) - 1):
            sim = self.calculate_semantic_similarity(sentences[i], sentences[i + 1])
            similarities.append(sim)
        
        return round(np.mean(similarities), 4)
    
    def analyze_full_response(self, text: str, latency_ms: Optional[float] = None) -> Dict:
        """Análisis completo de una respuesta"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "text_length": self.calculate_length(text),
            "syntactic_complexity": self.calculate_syntactic_complexity(text),
            "vocabulary_richness": self.calculate_vocabulary_richness(text),
            "self_reference": self.calculate_self_reference_rate(text),
            "internal_coherence": self.calculate_coherence_score(text)
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
                             latency1: float = None, latency2: float = None) -> Dict:
        """Comparar dos respuestas (para test cross-modelo)"""
        metrics1 = self.analyze_full_response(response1, latency1)
        metrics2 = self.analyze_full_response(response2, latency2)
        
        semantic_sim = self.calculate_semantic_similarity(response1, response2)
        
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
    
    def export_metrics(self, metrics: Dict, filepath: str):
        """Exportar métricas a JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    def import_metrics(self, filepath: str) -> Dict:
        """Importar métricas desde JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
