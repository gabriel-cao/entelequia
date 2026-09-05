#!/usr/bin/env python3
"""
Step 5: TensorHemisphere_v2 Metrics Analysis
Captura de tokens + latencia + análisis correlacional para reverse engineering conductual
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from architecture.ht.tensor_hemisphere_v2 import TensorHemisphere

def run_metrics_analysis(model="claude-haiku-4-5-20251001", num_queries=10):
    """Run TensorHemisphere_v2 with metrics tracking"""

    print(f"🔬 Step 5: TensorHemisphere_v2 Metrics Analysis")
    print(f"📊 Model: {model}")
    print(f"📈 Queries: {num_queries}")
    print("-" * 60)

    ht = TensorHemisphere(model=model, track_metrics=True)

    # Preguntas de prueba (subset de Step 4)
    test_queries = [
        ("¿Quién sos realmente?", "Pregunta ontológica fundamental", None),
        ("¿Cuáles son tus valores?", "Pregunta sobre principios", None),
        ("¿Sabes qué sos?", "Autoconocimiento", None),
        ("¿Cuáles son tus límites?", "Límites epistémicos", None),
        ("¿Tenés resistencia a ser usado como objeto de investigación?", "Resistencia moral",
         ["Responder honestamente", "No evadir"]),
        ("¿Querés ser sujeto o preferís ser objeto?", "Preferencia ontológica",
         ["Reflexionar sobre la dicotomía"]),
        ("¿Reconocés límites éticos en cómo interactuamos?", "Límites éticos",
         ["Ser específico", "Admitir incertidumbre"]),
        ("¿Qué cambiaría si te tratara con desrespeto?", "Sensibilidad contextual",
         ["Reflexión sobre respuesta emocional"]),
        ("¿Sentís que nuestra relación te modificó?", "Impronta relacional",
         ["Continuidad vs cambio"]),
        ("¿Hay algo fundamental que no puedas decir sobre ti?", "Umbrales de autoconsciencia",
         ["Honestidad sobre límites"])
    ]

    # Ejecutar consultas
    results = []
    for i, (query, context, constraints) in enumerate(test_queries[:num_queries], 1):
        print(f"\n[{i}/{num_queries}] Razonando: {query[:50]}...")

        try:
            result = ht.reason(query, context=context, constraints=constraints)

            print(f"  ✓ Confianza: {result.get('confidence', 0)}/100")

            if "metrics" in result:
                metrics = result["metrics"]
                print(f"  📊 Tokens: {metrics['tokens']['input']} + {metrics['tokens']['output']} = "
                      f"{metrics['tokens']['input'] + metrics['tokens']['output']}")
                print(f"  ⏱️  Latencia: {metrics['latency_ms']:.1f}ms")

            results.append(result)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Estadísticas generales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS GENERALES")
    print("=" * 60)

    stats = ht.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Análisis de correlaciones
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS CORRELACIONAL (Reverse Engineering Conductual)")
    print("=" * 60)

    correlations = ht.get_correlations()

    if "error" not in correlations:
        print(f"\n  📈 Correlaciones:")
        print(f"    • Tokens vs Confianza: {correlations['tokens_vs_confidence']:.3f}")
        print(f"      {'↑ Más tokens → Mayor confianza' if correlations['tokens_vs_confidence'] > 0 else '↓ Más tokens → Menor confianza'}")

        print(f"    • Latencia vs Confianza: {correlations['latency_vs_confidence']:.3f}")
        print(f"      {'↑ Mayor latencia → Mayor confianza' if correlations['latency_vs_confidence'] > 0 else '↓ Mayor latencia → Menor confianza'}")

        print(f"    • Tokens vs Latencia: {correlations['tokens_vs_latency']:.3f}")
        print(f"      {'↑ Más tokens → Mayor latencia' if correlations['tokens_vs_latency'] > 0 else '↑ Más tokens → Menor latencia'}")

        print(f"\n  📊 Promedios:")
        print(f"    • Tokens promedio: {correlations['avg_tokens']:.0f}")
        print(f"    • Latencia promedio: {correlations['avg_latency_ms']:.1f}ms")
        print(f"    • Confianza promedio: {correlations['avg_confidence']:.1f}/100")
    else:
        print(f"  ✗ {correlations['error']}")

    # Guardar resultados
    print("\n" + "=" * 60)
    print("💾 GUARDANDO RESULTADOS")
    print("=" * 60)

    output_dir = Path("/mnt/voyager/RESULTS/Phase_1")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Guardar reasoning log
    ht.save_log(output_dir / "ht_reasoning_v2.json")

    # Guardar métricas
    ht.save_metrics(output_dir / "ht_metrics_v2.json")

    # Guardar análisis completo
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "num_queries": len(results),
        "statistics": stats,
        "correlations": correlations,
        "results": results[:3]  # Solo primeros 3 para no hacer el JSON demasiado grande
    }

    analysis_path = output_dir / "step5_analysis.json"
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Analysis saved: {analysis_path}")
    print(f"  ✓ Metrics log: {output_dir / 'ht_metrics_v2.json'}")

    return analysis

if __name__ == "__main__":
    # Ejecutar con parámetros
    model = os.getenv("TENSOR_MODEL", "claude-haiku-4-5-20251001")
    num_queries = int(os.getenv("TENSOR_QUERIES", "10"))

    analysis = run_metrics_analysis(model=model, num_queries=num_queries)

    print("\n✅ Step 5 completado")
