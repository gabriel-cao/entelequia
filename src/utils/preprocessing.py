"""
preprocessing.py - Funciones de preprocesamiento de corpus
"""

import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """Limpiar y normalizar texto"""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def split_into_sentences(text: str) -> List[str]:
    """Dividir texto en oraciones"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def load_corpus_from_jsonl(filepath: str) -> List[Dict]:
    """Cargar corpus desde archivo JSONL"""
    import json
    corpus = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    corpus.append(json.loads(line))
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
    return corpus


def normalize_corpus(corpus: List[Dict], text_field: str = "text") -> List[Dict]:
    """Normalizar corpus: limpiar textos y estandarizar estructura"""
    normalized = []
    for entry in corpus:
        if text_field in entry:
            cleaned = clean_text(entry[text_field])
            entry[text_field] = cleaned
            normalized.append(entry)
    return normalized
