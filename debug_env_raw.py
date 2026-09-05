#!/usr/bin/env python3
"""
Debug: Ver contenido raw del .env
"""

from pathlib import Path

project_root = Path(__file__).parent
env_path = project_root / ".env"

print("="*70)
print("DEBUG: Contenido RAW de .env")
print("="*70)

if env_path.exists():
    with open(env_path, 'rb') as f:
        content = f.read()

    print(f"\nTamaño total: {len(content)} bytes")
    print(f"\nPrimeros 500 caracteres (raw):")
    print(repr(content[:500]))

    print(f"\n\nLínea por línea (mostrando espacios como · y saltos como ↵):")
    with open(env_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Mostrar espacios y saltos de línea visibles
            display = line.rstrip('\n').replace(' ', '·').replace('\t', '→')
            print(f"Línea {i:2d}: {display}↵")
            if i >= 15:
                break
else:
    print(f"✗ {env_path} no existe")
