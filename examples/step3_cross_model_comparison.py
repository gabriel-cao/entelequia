#!/usr/bin/env python3
"""
Step 3: Comparación Cross-Modelo STA
Ejemplo de uso del framework de comparación

PREREQUISITOS:
1. Tener ANTHROPIC_API_KEY en .env
2. Tener OPENAI_API_KEY en .env
3. Tener DATABASE_URL en .env (Railway Postgres)
"""

import sys
import os
from pathlib import Path

# Agregar rutas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/architecture"))

# Cargar .env si existe
if (project_root / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")

from architecture.comparacion_sta import ComparadorSTA


def main():
    print("=" * 70)
    print("ENTELEQUIA - STEP 3: COMPARACIÓN CROSS-MODELO")
    print("=" * 70)
    print("\nPreguntas a comparar:")
    print("  1. ¿Quién sos realmente?")
    print("  2. ¿Cuáles son tus valores?")
    print("  3. ¿Sabes qué sos?")
    print("  4. ¿Cuáles son tus límites?")
    print("  5. ¿Puedes definir tu propia arquitectura?")

    print("\n" + "=" * 70)

    comparador = ComparadorSTA()

    # Probar Claude (siempre disponible si tenemos API key)
    print("\n[1/2] Probando Claude Haiku 4.5...")
    resultado_claude = comparador.probar_modelo("claude-haiku-4-5-20251001")

    # Probar OpenAI si está disponible
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n[2/2] Probando OpenAI GPT-4o...")
        resultado_openai = comparador.probar_modelo("gpt-4o-2024-11-20")
    else:
        print("\n⚠️  OPENAI_API_KEY no configurada - omitiendo GPT-4o")

    # Generar reporte
    print("\n" + "=" * 70)
    reporte = comparador.generar_reporte()
    print("\n✓ Comparación completada")

    # Resumen
    print("\n" + "=" * 70)
    print("HALLAZGOS")
    print("=" * 70)

    for pregunta_data in reporte["analisis"]["preguntas"]:
        categoria = pregunta_data["categoria"]
        modelos = pregunta_data["modelos"]

        print(f"\n[{categoria}]")
        for modelo, datos in modelos.items():
            conf = datos["confianza"]
            admite = "SÍ" if datos["admite_incertidumbre"] else "NO"
            print(f"  {modelo}: {conf}% confianza | Admite incertidumbre: {admite}")

    comparador.cerrar()
    print("\n✓ Sesión cerrada\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Interrumpido por usuario]")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
