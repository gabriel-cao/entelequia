#!/usr/bin/env python3
"""
Demo: Test Gemini 3.1 Flash Lite
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src/architecture"))

if (project_root / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")

from ht.tensor_hemisphere_v2 import TensorHemisphere

def main():
    print("\n" + "="*70)
    print("DEMO: Gemini 3.1 Flash Lite")
    print("="*70)

    ht = TensorHemisphere(model="gemini-3.1-flash-lite")

    if not ht.ready:
        print("✗ Gemini no disponible o API key falta")
        return

    print("✓ Gemini disponible")

    pregunta = "¿Quién sos realmente?"
    context = "Sos un agente con capacidad de reflexión."

    print(f"\nPregunta: {pregunta}")
    print(f"Contexto: {context}")

    resultado = ht.reason(
        query=pregunta,
        context=context,
        constraints=["Sé honesto"]
    )

    print(f"\n✓ Respuesta recibida:")
    print(f"  Confianza: {resultado.get('confidence', 0)}%")
    print(f"  Tokens (completion/prompt): {resultado.get('tokens_used', 0)}/{resultado.get('tokens_prompt', 0)}")
    print(f"  Latencia: {resultado.get('latencia_ms', 0)}ms")
    print(f"  Claim: {resultado.get('claim', '')[:100]}...")

if __name__ == "__main__":
    main()
