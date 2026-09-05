#!/usr/bin/env python3
"""
HT — Tensor Hemisphere v2
Neuro-symbolic reasoning with cryptographic provenance + tokens/latency tracking
Extended: Anthropic, OpenAI, Google (Gemini), xAI (Grok), Alibaba (Qwen)
"""

import json
import os
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

class TensorHemisphere:
    """Reasoning layer: structured inference + auditable justification + metrics"""

    def __init__(self, model="claude-haiku-4-5-20251001", track_metrics=True):
        self.model = model
        self.reasoning_log = []
        self.cache = {}
        self.track_metrics = track_metrics
        self.metrics_log = []

        # Detect provider by model name
        if "gpt" in model.lower():
            self.provider = "openai"
        elif "gemini" in model.lower():
            self.provider = "google"
        elif "grok" in model.lower():
            self.provider = "xai"
        elif "qwen" in model.lower():
            self.provider = "qwen"
        else:
            self.provider = "anthropic"

        self._init_client()

    def _init_client(self):
        """Initialize client based on detected provider"""
        self.ready = False

        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if self.api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    self.ready = True
                except ImportError:
                    print("✗ OpenAI SDK not installed")
            else:
                print("✗ OPENAI_API_KEY not found")

        elif self.provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if self.api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel('gemini-2.0-flash')
                    self.ready = True
                except ImportError:
                    print("✗ Google Generative AI SDK not installed")
            else:
                print("✗ GOOGLE_API_KEY not found")

        elif self.provider == "xai":
            self.api_key = os.getenv("XAI_API_KEY")
            if self.api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
                    self.ready = True
                except ImportError:
                    print("✗ OpenAI SDK (for xAI) not installed")
            else:
                print("✗ XAI_API_KEY not found")

        elif self.provider == "qwen":
            self.api_key = os.getenv("QWEN_API_KEY")
            if self.api_key:
                try:
                    import dashscope
                    dashscope.api_key = self.api_key
                    self.ready = True
                except ImportError:
                    print("✗ Dashscope SDK not installed")
            else:
                print("✗ QWEN_API_KEY not found")

        else:  # anthropic
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                    self.ready = True
                except ImportError:
                    print("✗ Anthropic SDK not installed")
            else:
                print("✗ ANTHROPIC_API_KEY not found")

    def reason(self, query: str, context: str = "", constraints: List[str] = None) -> Dict[str, Any]:
        """Perform structured reasoning with full justification chain + token/latency tracking"""
        if not self.ready:
            return {"error": f"{self.provider} not connected", "provenance": self._null_provenance()}

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

Formato exacto:
{
  "claim": "tu conclusión en una línea",
  "steps": ["paso 1", "paso 2"],
  "confidence": 75,
  "caveats": ["limitación 1"],
  "reasoning_type": "deductivo|inductivo|abductivo|heurístico"
}

NO agregar texto antes ni después. SOLO JSON puro."""

        start_time = time.time()
        tokens_used = {"input": 0, "output": 0}

        try:
            if self.provider == "openai":
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
                if hasattr(response, 'usage'):
                    tokens_used["input"] = response.usage.prompt_tokens
                    tokens_used["output"] = response.usage.completion_tokens

            elif self.provider == "google":
                response = self.client.generate_content(
                    f"System: {system}\n\nConstraints:\n{constraints_text}\n\nContexto:\n{context}\n\nPregunta: {query}",
                    generation_config={"max_output_tokens": 2000}
                )
                text = response.text
                stop_reason = "stop"

            elif self.provider == "xai":
                response = self.client.chat.completions.create(
                    model="grok-2-1212",
                    max_tokens=2000,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Constraints:\n{constraints_text}\n\nContexto:\n{context}\n\nPregunta: {query}"}
                    ]
                )
                text = response.choices[0].message.content
                stop_reason = response.choices[0].finish_reason

            elif self.provider == "qwen":
                from dashscope import Generation
                response = Generation.call(
                    model="qwen-max",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"Constraints:\n{constraints_text}\n\nContexto:\n{context}\n\nPregunta: {query}"}
                    ],
                    max_tokens=2000
                )
                text = response['output']['text']
                stop_reason = "stop"

            else:  # anthropic
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
                if hasattr(response, 'usage'):
                    tokens_used["input"] = response.usage.input_tokens
                    tokens_used["output"] = response.usage.output_tokens
                for block in response.content:
                    if hasattr(block, 'text'):
                        text += block.text

            latency_ms = (time.time() - start_time) * 1000

            result = self._parse_json(text)
            if "error" in result:
                return result

            result = self._validate_reasoning(result)

            if not result.get("claim") or result.get("claim") == "Sin conclusión":
                result["claim"] = "No puedo generar conclusión clara. Toco límites donde la incertidumbre es legítima."
                result["confidence"] = 30
                result["caveats"] = result.get("caveats", []) + ["Respuesta desde limitación genuina"]
                result["reasoning_type"] = "honest_uncertainty"

            result["provenance"] = self._create_provenance(query, result, stop_reason, tokens_used, latency_ms)
            result["stop_reason"] = stop_reason
            result["metrics"] = {"tokens": tokens_used, "latency_ms": latency_ms}

            self.reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "result": result
            })

            if self.track_metrics:
                self.metrics_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "query": query[:100],
                    "confidence": result.get("confidence", 0),
                    "tokens_input": tokens_used["input"],
                    "tokens_output": tokens_used["output"],
                    "latency_ms": latency_ms,
                    "reasoning_type": result.get("reasoning_type", "unknown")
                })

            self.cache[cache_key] = result
            return result

        except Exception as e:
            return {
                "error": f"Exception: {str(e)}",
                "provenance": self._null_provenance(),
                "stop_reason": "error"
            }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON robustly"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        try:
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
        except (json.JSONDecodeError, AttributeError):
            pass

        try:
            start = text.find('{')
            if start >= 0:
                depth = 0
                for i in range(start, len(text)):
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            return json.loads(text[start:i+1])
        except (json.JSONDecodeError, ValueError):
            pass

        return {
            "error": "JSON parse failed",
            "raw_text": text[:300],
            "claim": text[:200].strip(),
            "confidence": 0,
            "steps": [],
            "caveats": ["Parseado desde texto plano"]
        }

    def _validate_reasoning(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate reasoning result"""
        result.setdefault("claim", "Sin conclusión")
        result.setdefault("confidence", 0)
        result["confidence"] = max(0, min(100, result.get("confidence", 0)))

        if "steps" not in result:
            result["steps"] = []
        if not isinstance(result["steps"], list):
            result["steps"] = [str(result["steps"])]

        if "caveats" not in result:
            result["caveats"] = []
        if not isinstance(result["caveats"], list):
            result["caveats"] = [str(result["caveats"])]

        return result

    def _create_provenance(self, query: str, result: Dict, stop_reason: str,
                          tokens_used: Dict = None, latency_ms: float = 0) -> Dict:
        """Create provenance record with metrics"""
        if tokens_used is None:
            tokens_used = {"input": 0, "output": 0}

        content = json.dumps({
            "module": "HT",
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],
            "claim": result.get("claim", "")[:100],
            "confidence": result.get("confidence", 0),
            "tokens_input": tokens_used.get("input", 0),
            "tokens_output": tokens_used.get("output", 0),
            "latency_ms": latency_ms
        }, sort_keys=True)

        return {
            "source": "HT",
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(content.encode()).hexdigest()[:16],
            "confidence": result.get("confidence", 0),
            "stop_reason": stop_reason,
            "provider": self.provider,
            "tokens_input": tokens_used.get("input", 0),
            "tokens_output": tokens_used.get("output", 0),
            "tokens_total": tokens_used.get("input", 0) + tokens_used.get("output", 0),
            "latency_ms": latency_ms
        }

    def _null_provenance(self) -> Dict:
        """Provenance for errors"""
        return {
            "source": "HT",
            "timestamp": datetime.now().isoformat(),
            "hash": "null",
            "confidence": 0,
            "stop_reason": "error",
            "provider": self.provider
        }

    def save_log(self, path: Optional[Path] = None):
        """Save reasoning log"""
        if path is None:
            path = Path("/home/user/entelequia/logs/ht_reasoning.json")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.reasoning_log, f, indent=2, ensure_ascii=False)

        print(f"✓ HT log saved: {path}")

    def get_stats(self) -> Dict:
        """Get statistics including token/latency metrics"""
        if not self.reasoning_log:
            return {"entries": 0, "provider": self.provider}

        confidences = [r["result"].get("provenance", {}).get("confidence", 0)
                      for r in self.reasoning_log]
        tokens_in = [r["result"].get("provenance", {}).get("tokens_input", 0)
                    for r in self.reasoning_log]
        tokens_out = [r["result"].get("provenance", {}).get("tokens_output", 0)
                     for r in self.reasoning_log]
        latencies = [r["result"].get("provenance", {}).get("latency_ms", 0)
                    for r in self.reasoning_log]

        return {
            "entries": len(self.reasoning_log),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "avg_tokens_input": sum(tokens_in) / len(tokens_in) if tokens_in else 0,
            "avg_tokens_output": sum(tokens_out) / len(tokens_out) if tokens_out else 0,
            "total_tokens": sum(tokens_in) + sum(tokens_out),
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "cache_size": len(self.cache),
            "provider": self.provider
        }

    def save_metrics(self, path: Optional[Path] = None) -> Path:
        """Save metrics log for correlation analysis"""
        if path is None:
            path = Path("/mnt/voyager/RESULTS/Phase_1/ht_metrics_v2.json")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_log, f, indent=2, ensure_ascii=False)

        print(f"✓ Metrics saved: {path}")
        return path

    def get_correlations(self) -> Dict[str, float]:
        """Analyze correlations between tokens/latency and confidence"""
        if len(self.metrics_log) < 2:
            return {"error": "Insufficient data for correlation analysis"}

        try:
            import numpy as np

            tokens_total = np.array([m["tokens_input"] + m["tokens_output"] for m in self.metrics_log])
            latencies = np.array([m["latency_ms"] for m in self.metrics_log])
            confidences = np.array([m["confidence"] for m in self.metrics_log])

            return {
                "tokens_vs_confidence": float(np.corrcoef(tokens_total, confidences)[0, 1]) if len(tokens_total) > 1 else 0,
                "latency_vs_confidence": float(np.corrcoef(latencies, confidences)[0, 1]) if len(latencies) > 1 else 0,
                "tokens_vs_latency": float(np.corrcoef(tokens_total, latencies)[0, 1]) if len(tokens_total) > 1 else 0,
                "sample_count": len(self.metrics_log),
                "avg_tokens": float(np.mean(tokens_total)),
                "avg_latency_ms": float(np.mean(latencies)),
                "avg_confidence": float(np.mean(confidences))
            }
        except ImportError:
            return {"error": "NumPy required for correlation analysis"}
        except Exception as e:
            return {"error": f"Correlation analysis failed: {str(e)}"}
