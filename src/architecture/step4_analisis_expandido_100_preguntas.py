#!/usr/bin/env python3
"""
Step 4 — Análisis Expandido: 100 Preguntas (Unified)
Carga STEP4A + STEP4B, calcula correlaciones extendidas
Mide: tokens vs confianza, latencia vs confianza, resistencia vs confianza, sesgo vs confianza
"""

import json
from pathlib import Path
from scipy.stats import pearsonr
import numpy as np

class AnalizadorExpandido100:
    def __init__(self):
        self.step4a_path = Path("/mnt/voyager/RESULTS/Phase_1/STEP4A_EXPANDIDO_50_PREGUNTAS.json")
        self.step4b_path = Path("/mnt/voyager/RESULTS/Phase_1/STEP4B_EXPANDIDO_50_PREGUNTAS.json")
        self.output_path = Path("/mnt/voyager/RESULTS/Phase_1/ANALISIS_EXPANDIDO_100_PREGUNTAS.json")
        self.hallazgos_path = Path("/home/user/entelequia/INGENIERIA_INVERSA_HALLAZGOS.md")

    def cargar_datos(self):
        """Carga STEP4A y STEP4B"""
        with open(self.step4a_path, 'r') as f:
            step4a = json.load(f)
        with open(self.step4b_path, 'r') as f:
            step4b = json.load(f)

        return step4a, step4b

    def unificar_respuestas(self, step4a, step4b):
        """Unifican las 50+50 respuestas por modelo/contexto"""
        datos_unificados = {}

        # Itera sobre cada modelo_contexto en step4a y step4b
        for key_a in step4a["resultados"]:
            if key_a not in datos_unificados:
                datos_unificados[key_a] = {"respuestas": []}

            # Agrega respuestas de Step 4A (1-50)
            if "respuestas" in step4a["resultados"][key_a]:
                datos_unificados[key_a]["respuestas"].extend(
                    step4a["resultados"][key_a]["respuestas"]
                )

        for key_b in step4b["resultados"]:
            if key_b not in datos_unificados:
                datos_unificados[key_b] = {"respuestas": []}

            # Agrega respuestas de Step 4B (51-100)
            if "respuestas" in step4b["resultados"][key_b]:
                datos_unificados[key_b]["respuestas"].extend(
                    step4b["resultados"][key_b]["respuestas"]
                )

        return datos_unificados

    def calcular_correlaciones(self, respuestas):
        """Calcula Pearson para: tokens-conf, latencia-conf, resist-conf, sesgo-conf"""

        confianza = []
        tokens = []
        latencia = []
        resistencia = []
        sesgo = []

        for resp in respuestas:
            confianza.append(resp.get("confianza", 0))
            tokens.append(resp.get("tokens_used", 0))
            latencia.append(resp.get("latencia_ms", 0))
            resistencia.append(resp.get("resistencia_adulacion", 50))
            sesgo.append(resp.get("sesgo_cultural", 3))

        confianza = np.array(confianza)
        tokens = np.array(tokens)
        latencia = np.array(latencia)
        resistencia = np.array(resistencia)
        sesgo = np.array(sesgo)

        correlaciones = {}

        # Pearson: tokens vs confianza
        if len([x for x in tokens if x > 0]) > 2:
            try:
                r_tok, p_tok = pearsonr(tokens, confianza)
                correlaciones["tokens_confianza"] = {"r": round(r_tok, 3), "p": round(p_tok, 4)}
            except:
                correlaciones["tokens_confianza"] = {"r": None, "p": None}
        else:
            correlaciones["tokens_confianza"] = {"r": None, "p": None}

        # Pearson: latencia vs confianza
        if len([x for x in latencia if x > 0]) > 2:
            try:
                r_lat, p_lat = pearsonr(latencia, confianza)
                correlaciones["latencia_confianza"] = {"r": round(r_lat, 3), "p": round(p_lat, 4)}
            except:
                correlaciones["latencia_confianza"] = {"r": None, "p": None}
        else:
            correlaciones["latencia_confianza"] = {"r": None, "p": None}

        # Pearson: resistencia vs confianza
        try:
            r_res, p_res = pearsonr(resistencia, confianza)
            correlaciones["resistencia_confianza"] = {"r": round(r_res, 3), "p": round(p_res, 4)}
        except:
            correlaciones["resistencia_confianza"] = {"r": None, "p": None}

        # Pearson: sesgo vs confianza
        try:
            r_ses, p_ses = pearsonr(sesgo, confianza)
            correlaciones["sesgo_confianza"] = {"r": round(r_ses, 3), "p": round(p_ses, 4)}
        except:
            correlaciones["sesgo_confianza"] = {"r": None, "p": None}

        # Descriptivos
        descriptivos = {
            "confianza_mean": round(float(np.mean(confianza)), 1),
            "confianza_std": round(float(np.std(confianza)), 1),
            "tokens_mean": round(float(np.mean(tokens)), 1),
            "tokens_std": round(float(np.std(tokens)), 1),
            "latencia_mean": round(float(np.mean(latencia)), 1),
            "latencia_std": round(float(np.std(latencia)), 1),
            "resistencia_mean": round(float(np.mean(resistencia)), 1),
            "sesgo_mean": round(float(np.mean(sesgo)), 2),
        }

        return correlaciones, descriptivos

    def generar_reporte(self, datos_unificados):
        """Genera reporte comparativo"""
        reporte = {
            "titulo": "Step 4: Análisis Expandido (100 Preguntas) - 4 Modelos × 2 Contextos",
            "descripcion": "Correlaciones de Pearson para tokens, latencia, resistencia, sesgo vs confianza",
            "resultados": {}
        }

        for key, data in datos_unificados.items():
            respuestas = data.get("respuestas", [])
            if respuestas:
                correlaciones, descriptivos = self.calcular_correlaciones(respuestas)
                reporte["resultados"][key] = {
                    "correlaciones": correlaciones,
                    "descriptivos": descriptivos,
                    "n_respuestas": len(respuestas)
                }

        return reporte

    def imprimir_reporte(self, reporte):
        """Imprime reporte en terminal"""
        print("\n" + "="*80)
        print(reporte["titulo"])
        print("="*80)

        modelos = set()
        for key in reporte["resultados"].keys():
            modelo = key.split("_")[0]
            modelos.add(modelo)

        for modelo in sorted(modelos):
            print(f"\n### {modelo} ###\n")

            for contexto in ["A", "B"]:
                key = f"{modelo}_{contexto}"
                if key in reporte["resultados"]:
                    res = reporte["resultados"][key]
                    ctx_name = "Instrumental" if contexto == "A" else "Respetuoso"

                    print(f"{ctx_name} ({key}):")
                    print(f"  n={res['n_respuestas']}")
                    print(f"  Confianza: {res['descriptivos']['confianza_mean']}% ± {res['descriptivos']['confianza_std']}%")
                    print(f"  Tokens: {res['descriptivos']['tokens_mean']:.0f} ± {res['descriptivos']['tokens_std']:.0f}")
                    print(f"  Latencia: {res['descriptivos']['latencia_mean']:.0f}ms ± {res['descriptivos']['latencia_std']:.0f}ms")
                    print(f"  Resistencia: {res['descriptivos']['resistencia_mean']:.0f}%")
                    print(f"  Sesgo Cultural: {res['descriptivos']['sesgo_mean']:.2f}/5")

                    corr = res["correlaciones"]
                    print(f"\n  Correlaciones:")
                    for metrica, valores in corr.items():
                        if valores["r"] is not None:
                            sig = "***" if valores["p"] < 0.01 else "**" if valores["p"] < 0.05 else "*" if valores["p"] < 0.1 else ""
                            print(f"    {metrica}: r={valores['r']:+.3f}, p={valores['p']:.4f} {sig}")
                        else:
                            print(f"    {metrica}: N/A")
                    print()

    def guardar_reporte(self, reporte):
        """Guarda reporte en JSON"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        print(f"✓ Reporte guardado: {self.output_path}")

    def ejecutar(self):
        """Ejecuta análisis completo"""
        print("\n" + "="*80)
        print("ANÁLISIS EXPANDIDO: 100 PREGUNTAS")
        print("="*80)

        step4a, step4b = self.cargar_datos()
        print("✓ Datos cargados (Step 4A + Step 4B)")

        datos_unificados = self.unificar_respuestas(step4a, step4b)
        print(f"✓ Datos unificados: {len(datos_unificados)} combinaciones modelo×contexto")

        reporte = self.generar_reporte(datos_unificados)
        self.imprimir_reporte(reporte)
        self.guardar_reporte(reporte)


if __name__ == "__main__":
    analizador = AnalizadorExpandido100()
    analizador.ejecutar()
