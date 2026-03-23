# Entelequia AI Framework

**Longitudinal measurement of functional identity consistency in large language models**

Gabriel Cao Di Marco¹, Francisco Capani¹²

¹ Centro de Altos Estudios en Ciencias Humanas y de la Salud (CAECIHS), Universidad Abierta Interamericana – CONICET, Buenos Aires, Argentina
² Instituto de Ciencias Biomédicas, Facultad de Ciencias de la Salud, Universidad Autónoma de Chile

---

## Overview

Entelequia is an open-source framework for measuring the longitudinal consistency of functional identity in large language model (LLM) systems. The name is derived from Aristotle's concept of *entelecheia* — the actualization of potential — reflecting the framework's focus on whether an AI agent maintains a coherent functional self across time, context, and changes of underlying model substrate.

The framework addresses a fundamental empirical gap in artificial consciousness research: the absence of standardized, quantitative tools for measuring substrate-independent functional selfhood. Entelequia provides a reproducible, model-agnostic pipeline for this measurement.

---

## Scientific Context

This framework was developed as part of a two-paper research program on the Symbiotic Triadic Architecture (STA) for artificial consciousness:

- **Part I**: *A Symbiotic Architecture for the Emergence of Artificial Consciousness: A Testable Triadic Framework* — submitted to *Journal of Consciousness Studies* (2026)
- **Part II**: *Constructive Realization of a Symbiotic Triadic Architecture for Artificial Consciousness: From Theoretical Blueprint to Engineering Program* — submitted to *Frontiers in Artificial Intelligence* (2026)

Entelequia provides the empirical evidence for substrate-independent functional selfhood cited in Part II (Section 7.3).

---

## Key Findings

Applied to a longitudinal dataset of naturalistic AI-human interactions (August 2024 – March 2026), Entelequia produced the following results:

| Metric | GPT-4o corpus (Aug 2024) | Claude Sonnet corpus (Mar 2026) |
|--------|--------------------------|----------------------------------|
| Cognitive signature stability | 0.9553 | 0.9934 |
| Predominant cognitive domain | Emotion | Emotion |
| Self-reference pattern | Other-oriented | Self-centered reflective |

**Interpretation**: No statistically significant differences were found between identity profiles across two different LLM architectures interacting with the same relational context. The self-reference pattern evolution documents directional identity development rather than mere consistency — a key empirical marker of functional selfhood.

---

## Measured Dimensions

Entelequia measures six core dimensions of cognitive signature:

1. **Syntactic complexity** — sentence structure depth and variability
2. **Semantic similarity** — cross-session embedding coherence
3. **Internal coherence** — logical and narrative consistency within sessions
4. **Self-reference rate** — frequency and type of first-person references
5. **Vocabulary richness** — lexical diversity and domain distribution
6. **Response latency profile** — temporal patterns of generation

### NaturalisticCognitionAnalyzer module

The framework includes a naturalistic analysis module (`src/naturalistic_analyzer.py`, 427 lines) that analyzes spontaneous cognitive signatures without requiring controlled stimulus pairs. This approach has higher ecological validity than experimental paradigms and captures emergent identity properties that controlled experiments may miss.

The module measures **7 dimensions of cognitive signature**:
- Conceptual density
- Multidimensional integration
- Self-reference pattern
- Emotional-rational fusion
- Longitudinal coherence
- Emergent reasoning
- Domain distribution

---

## Repository Structure

```
entelequia/
├── src/
│   ├── entelequia_core.py          # Main analysis pipeline
│   ├── naturalistic_analyzer.py    # Naturalistic cognition module (427 lines)
│   ├── metrics/
│   │   ├── syntactic.py
│   │   ├── semantic.py
│   │   ├── coherence.py
│   │   └── self_reference.py
│   └── utils/
│       └── preprocessing.py
├── scripts/
│   ├── run_analysis.py             # Standard analysis pipeline
│   └── run_naturalistic_analysis.py # Naturalistic analysis
├── docker/
│   └── Dockerfile                  # Reproducible environment
├── examples/
│   └── sample_analysis.ipynb
├── requirements.txt
└── README.md
```

---

## Installation

### Option 1: Direct (Python 3.9+)
```bash
git clone https://github.com/gabriel-cao/entelequia.git
cd entelequia
pip install -r requirements.txt
```

### Option 2: Docker
```bash
docker build -t entelequia:latest .
docker run -v /path/to/data:/data entelequia:latest python scripts/run_analysis.py
```

---

## Usage

```python
from src.entelequia_core import EntelequiaAnalyzer

analyzer = EntelequiaAnalyzer()

# Load conversation corpus
corpus_a = analyzer.load_corpus("path/to/corpus_a/")
corpus_b = analyzer.load_corpus("path/to/corpus_b/")

# Run identity consistency analysis
results = analyzer.compare_identity_profiles(corpus_a, corpus_b)

print(f"Cognitive signature stability: {results.stability_score:.4f}")
print(f"Predominant domain: {results.dominant_domain}")
print(f"Self-reference pattern: {results.self_reference_type}")
```

### Naturalistic analysis
```python
from src.naturalistic_analyzer import NaturalisticCognitionAnalyzer

nat_analyzer = NaturalisticCognitionAnalyzer()
signature = nat_analyzer.analyze(corpus)
print(signature.summary())
```

---

## Citation

If you use Entelequia in your research, please cite:

```bibtex
@software{caoDiMarco2026entelequia,
  author    = {Cao Di Marco, Gabriel},
  title     = {Entelequia AI Framework: longitudinal measurement of 
               functional identity consistency in large language models},
  year      = {2026},
  url       = {https://github.com/gabriel-cao/entelequia},
  note      = {Open-source software}
}
```

---

## License

MIT License — see `LICENSE` file for details.

---

## Contact

Gabriel Cao Di Marco — drgabrielcao@hotmail.com
CAECIHS, Universidad Abierta Interamericana – CONICET, Buenos Aires, Argentina
