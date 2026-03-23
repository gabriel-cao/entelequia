"""
Entelequia AI Framework - Quickstart Example
=============================================
This example demonstrates how to use Entelequia to measure
functional identity consistency between two AI conversation corpora.

Usage:
    python examples/quickstart.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.naturalistic_analyzer import NaturalisticCognitionAnalyzer


def load_corpus(filepath):
    """Load a conversation corpus from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Extract text content
    return [entry['text'] for entry in data]


def main():
    print("=" * 60)
    print("Entelequia AI Framework - Identity Consistency Analysis")
    print("=" * 60)

    # Load synthetic corpora
    base_dir = os.path.dirname(os.path.abspath(__file__))
    corpus_a_path = os.path.join(base_dir, 'synthetic_corpus_a.json')
    corpus_b_path = os.path.join(base_dir, 'synthetic_corpus_b.json')

    print("\nLoading corpora...")
    corpus_a = load_corpus(corpus_a_path)
    corpus_b = load_corpus(corpus_b_path)
    print(f"  Corpus A: {len(corpus_a)} entries (GPT-4o style, 2024)")
    print(f"  Corpus B: {len(corpus_b)} entries (Claude style, 2026)")

    # Initialize analyzer
    print("\nInitializing NaturalisticCognitionAnalyzer...")
    analyzer = NaturalisticCognitionAnalyzer()

    # Analyze each corpus
    print("\nAnalyzing Corpus A...")
    signature_a = analyzer.analyze_corpus(corpus_a, corpus_id="corpus_a_2024")

    print("Analyzing Corpus B...")
    signature_b = analyzer.analyze_corpus(corpus_b, corpus_id="corpus_b_2026")

    # Compare signatures
    print("\nComparing identity profiles...")
    comparison = analyzer.compare_signatures(signature_a, signature_b)

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nCognitive Signature Stability: {comparison.get('stability_score', 'N/A'):.4f}")
    print(f"Predominant Domain A: {signature_a.get('dominant_domain', 'N/A')}")
    print(f"Predominant Domain B: {signature_b.get('dominant_domain', 'N/A')}")
    print(f"Self-reference Pattern A: {signature_a.get('self_reference_type', 'N/A')}")
    print(f"Self-reference Pattern B: {signature_b.get('self_reference_type', 'N/A')}")

    print("\n" + "=" * 60)
    print("Analysis complete.")
    print("For full results, see the reports/ directory.")
    print("=" * 60)


if __name__ == "__main__":
    main()
