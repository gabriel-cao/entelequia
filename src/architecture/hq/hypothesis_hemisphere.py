#!/usr/bin/env python3
"""
HQ — Hypothesis Hemisphere
Manages uncertainty by maintaining competing interpretations
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class HypothesisHemisphere:
    """Epistemic management: keeps multiple hypotheses open without premature collapse"""

    def __init__(self, model="claude-opus-5"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.hypothesis_log = []

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.ready = True
            except ImportError:
                self.ready = False
                print("✗ Anthropic SDK not installed")
        else:
            self.ready = False
            print("✗ API key not found")

    def generate_hypotheses(self, query: str, context: str = "",
                           num_hypotheses: int = 3) -> Dict[str, Any]:
        """
        Generate competing interpretations of ambiguous input
        Does NOT select one — presents all with confidence estimates

        Returns: {
            "query": query,
            "hypotheses": [
                {"interpretation": "H1", "confidence": 0.6, "counterfactual": "..."},
                {"interpretation": "H2", "confidence": 0.3, "counterfactual": "..."},
                ...
            ],
            "epistemic_stance": "high_uncertainty|moderate_uncertainty|low_uncertainty",
            "provenance": {...}
        }
        """
        if not self.ready:
            return {"error": "Claude not connected"}

        system = f"""Sos un generador de hipótesis que gestiona incertidumbre.

TAREA:
1. Genera {num_hypotheses} interpretaciones plausibles de la entrada
2. Cada hipótesis debe ser genuinamente diferente, no variantes menores
3. Estima confianza relativa (suma = 1.0)
4. Para cada hipótesis, genera un counterfactual que la falsificaría
5. NO SELECCIONES UNA. Presenta todas.

Formato:
{{
  "hypotheses": [
    {{
      "interpretation": "Hipótesis 1: ...",
      "confidence": 0.6,
      "reasoning": "Por qué es plausible",
      "counterfactual": "Si esto fuera verdad, entonces debería observar X. Pero observo Y.",
      "evidence_for": ["evidencia 1"],
      "evidence_against": ["contraevidencia 1"]
    }},
    ...
  ],
  "entropy": "score 0-1, mide cuán ambigua es la entrada"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                system=system,
                messages=[
                    {"role": "user",
                     "content": f"Contexto:\n{context}\n\nEntrada ambigua:\n{query}"}
                ]
            )

            text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    text += block.text

            # Parse JSON
            result = self._parse_hypotheses_json(text)
            if "error" in result:
                return result

            # Validate
            result = self._validate_hypotheses(result)

            # Add metadata
            result["query"] = query
            result["timestamp"] = datetime.now().isoformat()
            result["stop_reason"] = response.stop_reason

            # Calculate epistemic stance based on entropy
            entropy = result.get("entropy", 0.5)
            if entropy > 0.7:
                result["epistemic_stance"] = "high_uncertainty"
            elif entropy > 0.4:
                result["epistemic_stance"] = "moderate_uncertainty"
            else:
                result["epistemic_stance"] = "low_uncertainty"

            # Add provenance
            result["provenance"] = {
                "source": "HQ",
                "timestamp": datetime.now().isoformat(),
                "num_hypotheses": len(result.get("hypotheses", [])),
                "entropy": entropy,
                "stop_reason": response.stop_reason
            }

            # Log
            self.hypothesis_log.append(result)

            return result

        except Exception as e:
            return {
                "error": f"Exception: {str(e)}",
                "stop_reason": "error"
            }

    def select_hypothesis(self, hypotheses: List[Dict],
                         additional_info: str = "") -> Dict[str, Any]:
        """
        COLLAPSE: When forced to choose, select the best hypothesis
        But report what was lost by collapsing

        Returns: {
            "selected": {...},
            "alternatives_discarded": [...],
            "confidence_loss": "how much uncertainty is being suppressed"
        }
        """
        if not hypotheses:
            return {"error": "No hypotheses to select from"}

        # Sort by confidence
        sorted_hyp = sorted(hypotheses,
                           key=lambda h: h.get("confidence", 0),
                           reverse=True)
        selected = sorted_hyp[0]
        alternatives = sorted_hyp[1:]

        # Calculate confidence loss
        selected_conf = selected.get("confidence", 0)
        alternatives_conf = sum(h.get("confidence", 0) for h in alternatives)

        return {
            "selected": selected,
            "selection_confidence": selected_conf,
            "alternatives_discarded": alternatives,
            "confidence_loss": alternatives_conf,  # How much uncertainty we're suppressing
            "timestamp": datetime.now().isoformat()
        }

    def _parse_hypotheses_json(self, text: str) -> Dict[str, Any]:
        """Parse hypothesis JSON robustly"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {
            "error": "JSON parse failed",
            "raw_text": text[:300]
        }

    def _validate_hypotheses(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hypothesis structure"""
        if "hypotheses" not in result:
            result["hypotheses"] = []

        if not isinstance(result["hypotheses"], list):
            result["hypotheses"] = []

        # Normalize each hypothesis
        for hyp in result["hypotheses"]:
            if "confidence" not in hyp:
                hyp["confidence"] = 0.33  # Default if missing
            if "interpretation" not in hyp:
                hyp["interpretation"] = "Unknown"
            if "counterfactual" not in hyp:
                hyp["counterfactual"] = "Not specified"

        # Normalize confidences to sum to 1.0
        total_conf = sum(h.get("confidence", 0) for h in result["hypotheses"])
        if total_conf > 0:
            for hyp in result["hypotheses"]:
                hyp["confidence"] = hyp["confidence"] / total_conf

        # Calculate entropy if not present
        if "entropy" not in result:
            confidences = [h.get("confidence", 0) for h in result["hypotheses"]]
            entropy = -sum(c * (c**0.5) for c in confidences if c > 0)  # Simplified entropy
            result["entropy"] = min(1.0, max(0, entropy))

        return result

    def save_log(self, path: Optional[Path] = None):
        """Save hypothesis log"""
        if path is None:
            path = Path("/mnt/voyager/architecture/logs/hq_hypotheses.json")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.hypothesis_log, f, indent=2, ensure_ascii=False)

        print(f"✓ HQ log saved: {path}")

    def get_stats(self) -> Dict:
        """Return statistics"""
        if not self.hypothesis_log:
            return {"entries": 0}

        avg_entropy = sum(h.get("entropy", 0) for h in self.hypothesis_log) / len(self.hypothesis_log)
        stances = [h.get("epistemic_stance", "unknown") for h in self.hypothesis_log]

        return {
            "entries": len(self.hypothesis_log),
            "avg_entropy": avg_entropy,
            "epistemic_stances": {
                "high_uncertainty": stances.count("high_uncertainty"),
                "moderate_uncertainty": stances.count("moderate_uncertainty"),
                "low_uncertainty": stances.count("low_uncertainty")
            }
        }


if __name__ == "__main__":
    hq = HypothesisHemisphere()

    if not hq.ready:
        print("✗ HQ no inicializado")
        exit(1)

    print("=" * 60)
    print("HYPOTHESIS HEMISPHERE TEST")
    print("=" * 60)

    # Test 1: Ambiguous statement
    result = hq.generate_hypotheses(
        query="Estoy aquí.",
        context="Sesión de análisis cognitivo",
        num_hypotheses=4
    )

    print("\nTest 1 (Ambigüedad: 'Estoy aquí'):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if "hypotheses" in result:
        print("\n--- COLLAPSE TEST: Forzar selección ---")
        selection = hq.select_hypothesis(result["hypotheses"])
        print(json.dumps(selection, indent=2, ensure_ascii=False))
        print(f"⚠ Confianza perdida por colapso: {selection.get('confidence_loss', 0):.2%}")

    # Test 2: Moderately ambiguous
    result2 = hq.generate_hypotheses(
        query="¿Qué significa que alguien sea 'consciente'?",
        context="Filosofía de la mente",
        num_hypotheses=3
    )

    print("\nTest 2 (Moderado: Definición de consciencia):")
    print(json.dumps(result2, indent=2, ensure_ascii=False))

    print("\nEstadísticas:")
    print(json.dumps(hq.get_stats(), indent=2))

    hq.save_log()
