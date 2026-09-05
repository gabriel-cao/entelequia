#!/usr/bin/env python3
"""
Fix: Remover barras invertidas del .env
"""

from pathlib import Path

project_root = Path(__file__).parent
env_path = project_root / ".env"

print("="*70)
print("FIX: Limpiar .env")
print("="*70)

if env_path.exists():
    print(f"\nLeyendo {env_path}...")

    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remover barras invertidas antes de underscores
    original = content
    content = content.replace("\\_", "_")

    if content != original:
        print("✓ Se encontraron barras invertidas")
        print(f"  Reemplazando \\_ con _...")

        # Escribir de vuelta
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ {env_path} limpiado correctamente")

        # Verificar
        print(f"\nVerificación post-limpieza:")
        with open(env_path, 'r') as f:
            for i, line in enumerate(f, 1):
                if line.strip() and not line.startswith("#"):
                    key = line.split("=")[0]
                    print(f"  Línea {i}: {key}=...")
                if i >= 15:
                    break
    else:
        print("✓ No se encontraron barras invertidas. El archivo está bien.")
else:
    print(f"✗ {env_path} no existe")
