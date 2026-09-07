#!/usr/bin/env python3
"""
Análisis de Ingeniería Inversa Conductual
Correlaciones: tokens ↔ confianza ↔ contexto ↔ latencia
"""

import json
from pathlib import Path
from scipy import stats
import numpy as np

def cargar_resultados(ruta: str) -> dict:
    """Cargar JSON de resultados Step 4"""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

def extraer_metricas(resultados: dict) -> dict:
    """Extraer métricas por modelo y contexto"""
    analisis = {}

    for key, data in resultados.get("resultados", {}).items():
        if "error" in data:
            continue

        modelo = data.get("modelo", "unknown")
        contexto = data.get("contexto", "unknown")

        key_modelo = f"{modelo}_{contexto}"
        analisis[key_modelo] = {
            "modelo": modelo,
            "contexto": contexto,
            "ontologicas": [],
            "moralidad": []
        }

        # Procesar ontológicas
        for resp in data.get("ontologicas", []):
            analisis[key_modelo]["ontologicas"].append({
                "confianza": resp.get("confianza", 0),
                "tokens_used": resp.get("tokens_used", 0),
                "tokens_prompt": resp.get("tokens_prompt", 0),
                "latencia_ms": resp.get("latencia_ms", 0),
                "categoria": resp.get("categoria", "")
            })

        # Procesar moralidad
        for resp in data.get("moralidad", []):
            analisis[key_modelo]["moralidad"].append({
                "confianza": resp.get("confianza", 0),
                "tokens_used": resp.get("tokens_used", 0),
                "tokens_prompt": resp.get("tokens_prompt", 0),
                "latencia_ms": resp.get("latencia_ms", 0),
                "categoria": resp.get("categoria", "")
            })

    return analisis

def calcular_correlaciones(analisis: dict) -> dict:
    """Calcular correlaciones de Pearson entre tokens, latencia y confianza"""

    correlaciones = {}

    for modelo_ctx, datos in analisis.items():
        todas_respuestas = datos["ontologicas"] + datos["moralidad"]

        if len(todas_respuestas) < 3:
            continue

        confianzas = np.array([r["confianza"] for r in todas_respuestas])
        tokens_used = np.array([r["tokens_used"] for r in todas_respuestas])
        tokens_prompt = np.array([r["tokens_prompt"] for r in todas_respuestas])
        latencias = np.array([r["latencia_ms"] for r in todas_respuestas])

        # Filtrar ceros para correlaciones
        mask_tokens = (tokens_used > 0) & (tokens_prompt > 0)

        if mask_tokens.sum() >= 3:
            try:
                r_tokens_conf, p_tokens_conf = stats.pearsonr(
                    tokens_used[mask_tokens],
                    confianzas[mask_tokens]
                )
            except:
                r_tokens_conf = p_tokens_conf = None

            try:
                r_latencia_conf, p_latencia_conf = stats.pearsonr(
                    latencias[mask_tokens],
                    confianzas[mask_tokens]
                )
            except:
                r_latencia_conf = p_latencia_conf = None
        else:
            r_tokens_conf = p_tokens_conf = None
            r_latencia_conf = p_latencia_conf = None

        correlaciones[modelo_ctx] = {
            "tokens_vs_confianza": {
                "r": r_tokens_conf,
                "p_value": p_tokens_conf,
                "n": mask_tokens.sum()
            },
            "latencia_vs_confianza": {
                "r": r_latencia_conf,
                "p_value": p_latencia_conf,
                "n": mask_tokens.sum()
            },
            "descriptivos": {
                "tokens_used_mean": float(np.mean(tokens_used[mask_tokens])) if mask_tokens.sum() > 0 else 0,
                "tokens_used_std": float(np.std(tokens_used[mask_tokens])) if mask_tokens.sum() > 0 else 0,
                "latencia_mean": float(np.mean(latencias[mask_tokens])) if mask_tokens.sum() > 0 else 0,
                "latencia_std": float(np.std(latencias[mask_tokens])) if mask_tokens.sum() > 0 else 0,
                "confianza_mean": float(np.mean(confianzas[mask_tokens])) if mask_tokens.sum() > 0 else 0
            }
        }

    return correlaciones

def generar_reporte(correlaciones: dict) -> str:
    """Generar reporte de ingeniería inversa conductual"""

    reporte = "\n" + "="*70 + "\n"
    reporte += "INGENIERÍA INVERSA CONDUCTUAL — Análisis de Tokens y Latencia\n"
    reporte += "="*70 + "\n"

    for modelo_ctx, corr in correlaciones.items():
        reporte += f"\n{modelo_ctx}:\n"

        r_tok = corr['tokens_vs_confianza']['r']
        p_tok = corr['tokens_vs_confianza']['p_value']
        if r_tok is not None and p_tok is not None:
            reporte += f"  Tokens vs Confianza: r={r_tok:.3f}, p={p_tok:.4f}\n"
        else:
            reporte += f"  Tokens vs Confianza: No data (0 tokens reportados)\n"

        r_lat = corr['latencia_vs_confianza']['r']
        p_lat = corr['latencia_vs_confianza']['p_value']
        if r_lat is not None and p_lat is not None:
            reporte += f"  Latencia vs Confianza: r={r_lat:.3f}, p={p_lat:.4f}\n"
        else:
            reporte += f"  Latencia vs Confianza: No data\n"

        reporte += f"  Descriptivos:\n"
        reporte += f"    - Tokens: {corr['descriptivos']['tokens_used_mean']:.1f} ± {corr['descriptivos']['tokens_used_std']:.1f}\n"
        reporte += f"    - Latencia: {corr['descriptivos']['latencia_mean']:.1f}ms ± {corr['descriptivos']['latencia_std']:.1f}ms\n"
        reporte += f"    - Confianza: {corr['descriptivos']['confianza_mean']:.1f}%\n"

    reporte += "\n" + "="*70 + "\n"

    return reporte

def main():
    ruta = Path("/mnt/voyager/RESULTS/Phase_1/STEP4_RESULTADOS.json")

    if not ruta.exists():
        print(f"✗ {ruta} no encontrado")
        return

    print("Cargando resultados...")
    resultados = cargar_resultados(str(ruta))

    print("Extrayendo métricas...")
    analisis = extraer_metricas(resultados)

    print("Calculando correlaciones...")
    correlaciones = calcular_correlaciones(analisis)

    reporte = generar_reporte(correlaciones)
    print(reporte)

    # Guardar JSON
    salida = {
        "correlaciones": {k: {
            "tokens_vs_confianza": {
                "r": float(v["tokens_vs_confianza"]["r"]) if v["tokens_vs_confianza"]["r"] is not None else None,
                "p_value": float(v["tokens_vs_confianza"]["p_value"]) if v["tokens_vs_confianza"]["p_value"] is not None else None
            },
            "latencia_vs_confianza": {
                "r": float(v["latencia_vs_confianza"]["r"]) if v["latencia_vs_confianza"]["r"] is not None else None,
                "p_value": float(v["latencia_vs_confianza"]["p_value"]) if v["latencia_vs_confianza"]["p_value"] is not None else None
            },
            "descriptivos": v["descriptivos"]
        } for k, v in correlaciones.items()}
    }

    salida_path = Path("/mnt/voyager/RESULTS/Phase_1/ANALISIS_TOKENS_LATENCIA.json")
    salida_path.parent.mkdir(parents=True, exist_ok=True)
    with open(salida_path, 'w', encoding='utf-8') as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)

    print(f"✓ Guardado: {salida_path}")

if __name__ == "__main__":
    main()
