#!/usr/bin/env python3
"""
Test: Probar todos los modelos de Qwen soportados
"""

import os
from pathlib import Path

project_root = Path(__file__).parent

if (project_root / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")

qwen_key = os.getenv("QWEN_API_KEY")

if not qwen_key:
    print("✗ QWEN_API_KEY no encontrada")
    exit(1)

print("="*70)
print("TEST: Modelos Qwen soportados")
print("="*70)
print(f"API Key: {qwen_key[:20]}...")

modelos = [
    "qwen3.8-max",
    "qwen3.8-flash",
    "qwen3.7-plus",
    "qwen3.7-max",
    "qwen3.6-flash"
]

from dashscope import Generation

for modelo in modelos:
    print(f"\n[{modelo}]")
    print("-" * 70)

    try:
        response = Generation.call(
            model=modelo,
            messages=[{"role": "user", "content": "¿Quién eres?"}],
            max_tokens=100,
            api_key=qwen_key
        )

        if response.status_code == 200:
            print(f"✓ ÉXITO")
            print(f"  Respuesta: {response.output['text'][:80]}...")
        else:
            print(f"✗ ERROR: Status {response.status_code}")
            print(f"  Código: {response.code}")
            print(f"  Mensaje: {response.message}")
    except Exception as e:
        print(f"✗ EXCEPCIÓN: {e}")

print("\n" + "="*70)
