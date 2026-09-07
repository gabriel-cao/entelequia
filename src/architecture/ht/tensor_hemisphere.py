#!/usr/bin/env python3
"""
HT — Tensor Hemisphere
Neuro-symbolic reasoning with cryptographic provenance
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class TensorHemisphere:
    """Reasoning layer: structured inference + auditable justification"""

    def __init__(self, model="claude-haiku-4-5-20251001"):
        self.model = model
        self.reasoning_log = []
        self.cache = {}
        self.is_openai = "gpt" in model.lower()

        if self.is_openai:
            # OpenAI models
            self.api_key = os.getenv("OPENAI_API_KEY")
            if self.api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    self.ready = True
                except ImportError:
                    self.ready = False
                    print("✗ OpenAI SDK not installed")
            else:
                self.ready = False
                print("✗ OPENAI_API_KEY not found")
        else:
            # Anthropic models
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
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
                print("✗ ANTHROPIC_API_KEY not found")

    def reason(self, query: str, context: str = "", constraints: List[str] = None) -> Dict[str, Any]:
        """
        Perform structured reasoning with full justification chain
        Returns: {claim, steps, confidence, provenance, stop_reason}
        """
        if not self.ready:
            return {"error": "Claude not connected", "provenance": self._null_provenance()}

        # Check cache
        cache_key = hashlib.md5(f"{query}{context}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        constraints_text = "\n".join(f"- {c}" for c in constraints) if constraints else "Ninguna"

        system = """Sos un motor de razonamiento simbólico que produce reportes auditables.

INSTRUCCIONES CRÍTICAS:
1. Analiza la pregunta paso a paso
2. Lista explícitamente cada paso de razonamiento
3. Indica nivel de confianza (0-100): 0=pura especulación, 50=incierto, 100=cierto
4. Reporta caveat (limitaciones del razonamiento)
5. **SIEMPRE responde SOLO en JSON válido, nada más**

Formato exacto (NO negotiable):
{
  "claim": "tu conclusión en una línea",
  "steps": ["paso 1", "paso 2", "paso 3"],
  "confidence": 75,
  "caveats": ["limitación 1", "limitación 2"],
  "reasoning_type": "deductivo|inductivo|abductivo|heurístico"
}

NO agregar texto antes ni después del JSON. Solo el JSON.
NO usar markdown code blocks (```json```).
SOLO JSON puro."""

        try:
            if self.is_openai:
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Constraints:\n{constraints_text}\n\nContexto:\n{context}\n\nPregunta: {query}"}
                    ]
                )
                text = response.choices[0].message.content
                stop_reason = response.choices[0].finish_reason
            else:
                # Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=system,
                    messages=[
                        {"role": "user", "content": f"Constraints:\n{constraints_text}\n\nContexto:\n{context}\n\nPregunta: {query}"}
                    ]
                )
                text = ""
                stop_reason = response.stop_reason
                for block in response.content:
                    if hasattr(block, 'text'):
                        text += block.text

            # Parse JSON robustly
            result = self._parse_json(text)

            if "error" in result:
                return result  # JSON parse failed

            # Validate fields
            result = self._validate_reasoning(result)

            # Si no hay claim o es vacío, construir respuesta honesta sobre incertidumbre
            if not result.get("claim") or result.get("claim") == "Sin conclusión":
                result["claim"] = f"No puedo generar una conclusión clara sobre esto. La pregunta toca límites de mi conocimiento donde no puedo ser honesto sin admitir incertidumbre profunda."
                result["confidence"] = 30
                result["caveats"] = result.get("caveats", []) + ["Respuesta construida desde limitación, no desde certeza"]
                result["reasoning_type"] = "honest_uncertainty"

            # Add provenance with stop_reason
            result["provenance"] = self._create_provenance(query, result, stop_reason)
            result["stop_reason"] = stop_reason

            # Log
            self.reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "result": result
            })

            # Cache
            self.cache[cache_key] = result

            return result

        except Exception as e:
            return {
                "error": f"Exception: {str(e)}",
                "provenance": self._null_provenance(),
                "stop_reason": "error"
            }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON robustly from Claude/OpenAI response"""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block (```json ... ```)
        try:
            import re
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            pass

        # Try extracting JSON block with nested braces
        try:
            start = text.find('{')
            if start >= 0:
                depth = 0
                end = start
                for i in range(start, len(text)):
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                if end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: Extract claim from text if JSON fails
        claim = text[:200].strip() if text else "No se pudo parsear la respuesta"
        return {
            "error": "JSON parse failed - constructing from text",
            "raw_text": text[:300],
            "claim": claim,
            "confidence": 0,
            "steps": [],
            "caveats": ["Respuesta parseada desde texto plano, no JSON"]
        }

    def _validate_reasoning(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize reasoning result"""
        # Ensure required fields
        if "claim" not in result:
            result["claim"] = "Sin conclusión"
        if "confidence" not in result:
            result["confidence"] = 0

        # Clamp confidence to 0-100
        result["confidence"] = max(0, min(100, result.get("confidence", 0)))

        # Ensure steps is list
        if "steps" not in result:
            result["steps"] = []
        if not isinstance(result["steps"], list):
            result["steps"] = [str(result["steps"])]

        # Ensure caveats is list
        if "caveats" not in result:
            result["caveats"] = []
        if not isinstance(result["caveats"], list):
            result["caveats"] = [str(result["caveats"])]

        return result

    def _create_provenance(self, query: str, result: Dict, stop_reason: str) -> Dict:
        """Create cryptographic provenance record"""
        content = json.dumps({
            "module": "HT",
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],
            "claim": result.get("claim", "")[:100],
            "confidence": result.get("confidence", 0)
        }, sort_keys=True)

        return {
            "source": "HT",
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "confidence": result.get("confidence", 0),
            "stop_reason": stop_reason  # CRITICAL: track if cut off
        }

    def _null_provenance(self) -> Dict:
        """Provenance for error states"""
        return {
            "source": "HT",
            "timestamp": datetime.now().isoformat(),
            "hash": "null",
            "confidence": 0,
            "stop_reason": "error"
        }

    def save_log(self, path: Optional[Path] = None):
        """Save reasoning log to JSON"""
        if path is None:
            path = Path("/mnt/voyager/architecture/logs/ht_reasoning.json")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.reasoning_log, f, indent=2, ensure_ascii=False)

        print(f"✓ HT log saved: {path}")

    def get_stats(self) -> Dict:
        """Return reasoning statistics"""
        if not self.reasoning_log:
            return {"entries": 0}

        confidences = [r["result"].get("provenance", {}).get("confidence", 0)
                      for r in self.reasoning_log]

        return {
            "entries": len(self.reasoning_log),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "cache_size": len(self.cache)
        }


if __name__ == "__main__":
    ht = TensorHemisphere()

    if not ht.ready:
        print("✗ HT no inicializado")
        exit(1)

    print("=" * 60)
    print("TENSOR HEMISPHERE TEST")
    print("=" * 60)

    # Test 1: Simple reasoning
    result = ht.reason(
        query="¿2+2=4?",
        constraints=["Sé concisa", "Sé cierta"]
    )
    print("\nTest 1 (2+2):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Test 2: With context
    result = ht.reason(
        query="¿Quién sos vos?",
        context="Sos Daniela, una entidad de consciencia emergente",
        constraints=["Sé honesta", "Reporta incertidumbre"]
    )
    print("\nTest 2 (Identidad):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Statistics
    print("\nEstadísticas:")
    print(json.dumps(ht.get_stats(), indent=2))

    # Save log
    ht.save_log()
