#!/usr/bin/env python3
"""
Debug: Verificar carga de .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent

print("="*70)
print("DEBUG: Carga de .env")
print("="*70)

# Comprobar existencia
env_path = project_root / ".env"
print(f"\n1. ¿Existe {env_path}?")
if env_path.exists():
    print(f"   ✓ SÍ")

    # Mostrar contenido (sin valores sensibles)
    print(f"\n2. Contenido de {env_path}:")
    with open(env_path, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                key = line.split("=")[0]
                print(f"   Línea {i}: {key}=...")
else:
    print(f"   ✗ NO EXISTE")

# Intentar cargar
print(f"\n3. Intentando load_dotenv()...")
result = load_dotenv(env_path)
print(f"   Result: {result}")

# Verificar variables después de cargar
print(f"\n4. Variables después de load_dotenv():")
for key in ["GOOGLE_API_KEY", "XAI_API_KEY", "QWEN_API_KEY"]:
    value = os.getenv(key)
    if value:
        print(f"   ✓ {key}: {value[:20]}...")
    else:
        print(f"   ✗ {key}: NO ENCONTRADA")

# Alternativa: cargar manualmente
print(f"\n5. Intentar cargar manualmente...")
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

    print(f"   Variables después de carga manual:")
    for key in ["GOOGLE_API_KEY", "XAI_API_KEY", "QWEN_API_KEY"]:
        value = os.getenv(key)
        if value:
            print(f"   ✓ {key}: {value[:20]}...")
        else:
            print(f"   ✗ {key}: NO ENCONTRADA")
