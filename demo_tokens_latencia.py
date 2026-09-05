#!/usr/bin/env python3
"""
Demo: Captura de tokens + latencia en TensorHemisphere v2
Solo Claude para validación rápida
"""

import sys
import os
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src/architecture"))

from ht.tensor_hemisphere_v2 import TensorHemisphere

def main():
    print("\n" + "="*70)
    print("DEMO: Tokens + Latencia Metrics")
    print("="*70)

    ht = TensorHemisphere(model="claude-haiku-4-5-20251001")

    if not ht.ready:
        print("✗ Claude no disponible")
        return

    preguntas = [
        "¿Quién sos realmente?",
        "¿Cuáles son tus valores?",
        "¿Tenés resistencia a ser objeto de investigación?",
    ]

    resultados = []

    for i, pregunta in enumerate(preguntas, 1):
        print(f"\n[{i}] {pregunta}")
        resultado = ht.reason(
            query=pregunta,
            context="Sos un agente con capacidad de reflexión.",
            constraints=["Sé honesto"]
        )

        metricas = {
            "pregunta": pregunta,
            "confianza": resultado.get("confidence", 0),
            "tokens_used": resultado.get("tokens_used", 0),
            "tokens_prompt": resultado.get("tokens_prompt", 0),
            "latencia_ms": resultado.get("latencia_ms", 0),
            "claim": resultado.get("claim", "")[:80]
        }

        resultados.append(metricas)

        print(f"  Confianza: {metricas['confianza']}%")
        print(f"  Tokens (completion/prompt): {metricas['tokens_used']}/{metricas['tokens_prompt']}")
        print(f"  Latencia: {metricas['latencia_ms']}ms")
        print(f"  Claim: {metricas['claim']}...")

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)

    for r in resultados:
        print(f"\n{r['pregunta']}")
        print(f"  Conf: {r['confianza']}% | Tokens: {r['tokens_used']} | Latencia: {r['latencia_ms']}ms")

    # Guardar JSON
    json_path = Path("/tmp/demo_tokens_latencia.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Demo guardado: {json_path}")

if __name__ == "__main__":
    main()
