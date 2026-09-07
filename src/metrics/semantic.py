"""
semantic.py - Análisis de similaridad semántica
"""

from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from typing import List


class SemanticAnalyzer:
    """Análisis de similaridad y coherencia semántica"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.embedder = SentenceTransformer(model_name)
        self.embedder = self.embedder.to('cpu')

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calcular similaridad semántica entre dos textos"""
        emb1 = self.embedder.encode(text1)
        emb2 = self.embedder.encode(text2)
        similarity = 1 - cosine(emb1, emb2)
        return round(float(similarity), 4)

    def calculate_similarities_batch(self, texts: List[str]) -> List[List[float]]:
        """Calcular matriz de similaridad entre múltiples textos"""
        embeddings = self.embedder.encode(texts)
        similarities = []
        for i in range(len(embeddings)):
            row = []
            for j in range(len(embeddings)):
                sim = 1 - cosine(embeddings[i], embeddings[j])
                row.append(round(float(sim), 4))
            similarities.append(row)
        return similarities
