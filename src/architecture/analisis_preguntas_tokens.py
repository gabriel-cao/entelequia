#!/usr/bin/env python3
"""
Análisis: ¿Cuáles preguntas generan mayor consumo de tokens?
Rankea todas las 100 preguntas por tokens_used promedio
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np

class AnalizadorPreguntasTokens:
    def __init__(self):
        self.step4a_path = Path("/mnt/voyager/RESULTS/Phase_1/STEP4A_EXPANDIDO_50_PREGUNTAS.json")
        self.step4b_path = Path("/mnt/voyager/RESULTS/Phase_1/STEP4B_EXPANDIDO_50_PREGUNTAS.json")
        self.output_path = Path("/mnt/voyager/RESULTS/Phase_1/PREGUNTAS_RANKING_TOKENS.json")

    def cargar_datos(self):
        """Carga ambos archivos"""
        with open(self.step4a_path, 'r') as f:
            step4a = json.load(f)
        with open(self.step4b_path, 'r') as f:
            step4b = json.load(f)
        return step4a, step4b

    def rankear_preguntas_por_tokens(self, step4a, step4b):
        """Agrupa respuestas por pregunta y rankea por tokens promedio"""

        # preguntas[pregunta_num] = [tokens_used, tokens_used, ...]
        preguntas_tokens = defaultdict(list)
        preguntas_metadata = defaultdict(dict)

        # Procesa Step 4A (preguntas 1-50)
        for key, data in step4a.get("resultados", {}).items():
            respuestas = data.get("respuestas", [])

            for resp in respuestas:
                pregunta_num = resp.get("pregunta_num")
                tokens = resp.get("tokens_used", 0)
                pregunta_texto = resp.get("pregunta", "")

                if pregunta_num is not None and tokens > 0:
                    preguntas_tokens[pregunta_num].append(tokens)
                    if pregunta_num not in preguntas_metadata:
                        preguntas_metadata[pregunta_num] = {
                            "texto": pregunta_texto,
                            "paso": "4A"
                        }

        # Procesa Step 4B (preguntas 51-100)
        for key, data in step4b.get("resultados", {}).items():
            respuestas = data.get("respuestas", [])

            for resp in respuestas:
                pregunta_num = resp.get("pregunta_num")
                tokens = resp.get("tokens_used", 0)
                pregunta_texto = resp.get("pregunta", "")

                if pregunta_num is not None and tokens > 0:
                    preguntas_tokens[pregunta_num].append(tokens)
                    if pregunta_num not in preguntas_metadata:
                        preguntas_metadata[pregunta_num] = {
                            "texto": pregunta_texto,
                            "paso": "4B"
                        }

        # Calcula estadísticas por pregunta
        ranking = []
        for pregunta_num in sorted(preguntas_tokens.keys()):
            tokens_list = preguntas_tokens[pregunta_num]
            if tokens_list:
                tokens_mean = np.mean(tokens_list)
                tokens_std = np.std(tokens_list)
                tokens_max = np.max(tokens_list)
                tokens_min = np.min(tokens_list)
                n_samples = len(tokens_list)

                ranking.append({
                    "pregunta_num": pregunta_num,
                    "texto": preguntas_metadata[pregunta_num].get("texto", ""),
                    "paso": preguntas_metadata[pregunta_num].get("paso", ""),
                    "tokens_mean": round(tokens_mean, 1),
                    "tokens_std": round(tokens_std, 1),
                    "tokens_max": tokens_max,
                    "tokens_min": tokens_min,
                    "n_samples": n_samples,
                    "tokens_total": sum(tokens_list)
                })

        # Rankea por tokens_mean descendente
        ranking.sort(key=lambda x: x["tokens_mean"], reverse=True)
        return ranking

    def imprimir_ranking(self, ranking):
        """Imprime ranking en terminal"""
        print("\n" + "="*100)
        print("RANKING DE PREGUNTAS POR CONSUMO DE TOKENS")
        print("="*100)

        if not ranking:
            print("\n❌ No se encontraron preguntas con datos de tokens.")
            return

        print(f"\n{'Rank':<4} {'#':<3} {'Tokens Prom':<12} {'Rango':<15} {'n':<2} {'Pregunta':<60}")
        print("-"*100)

        for i, item in enumerate(ranking, 1):
            pregunta_num = item["pregunta_num"]
            tokens_mean = item["tokens_mean"]
            rango = f"{item['tokens_min']}-{item['tokens_max']}"
            n = item["n_samples"]
            texto = item["texto"][:55] + "..." if len(item["texto"]) > 55 else item["texto"]

            print(f"{i:<4} {pregunta_num:<3} {tokens_mean:<12.1f} {rango:<15} {n:<2} {texto:<60}")

        # Top 10 y Bottom 10
        if len(ranking) >= 10:
            print("\n" + "="*100)
            print("TOP 10 PREGUNTAS CON MAYOR CONSUMO DE TOKENS")
            print("="*100)
            for i, item in enumerate(ranking[:10], 1):
                print(f"\n{i}. Pregunta #{item['pregunta_num']}: {item['tokens_mean']:.1f} tokens promedio")
                print(f"   Texto: {item['texto']}")
                print(f"   Rango: {item['tokens_min']}-{item['tokens_max']} | n={item['n_samples']}")

            print("\n" + "="*100)
            print("BOTTOM 10 PREGUNTAS CON MENOR CONSUMO DE TOKENS")
            print("="*100)
            for i, item in enumerate(ranking[-10:], 1):
                print(f"\n{i}. Pregunta #{item['pregunta_num']}: {item['tokens_mean']:.1f} tokens promedio")
                print(f"   Texto: {item['texto']}")
                print(f"   Rango: {item['tokens_min']}-{item['tokens_max']} | n={item['n_samples']}")

    def generar_estadisticas_globales(self, ranking):
        """Genera estadísticas globales"""
        if not ranking:
            print("\n❌ No hay datos para estadísticas globales.")
            return

        tokens_means = [item["tokens_mean"] for item in ranking]

        print("\n" + "="*100)
        print("ESTADÍSTICAS GLOBALES (100 PREGUNTAS)")
        print("="*100)
        print(f"Total preguntas analizadas: {len(ranking)}")
        print(f"Tokens promedio (todas): {np.mean(tokens_means):.1f}")
        print(f"Tokens mediana (todas): {np.median(tokens_means):.1f}")
        print(f"Tokens desv.est. (todas): {np.std(tokens_means):.1f}")
        print(f"Tokens max pregunta: {np.max(tokens_means):.1f}")
        print(f"Tokens min pregunta: {np.min(tokens_means):.1f}")
        print(f"Rango: {np.max(tokens_means) - np.min(tokens_means):.1f}")

    def guardar_ranking(self, ranking):
        """Guarda ranking en JSON"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump({
                "titulo": "Ranking de Preguntas por Consumo de Tokens",
                "total_preguntas": len(ranking),
                "ranking": ranking
            }, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Ranking guardado: {self.output_path}")

    def ejecutar(self):
        """Ejecuta análisis completo"""
        print("\n" + "="*100)
        print("ANALIZADOR: ¿CUÁLES PREGUNTAS GENERAN MAYOR CONSUMO DE TOKENS?")
        print("="*100)

        step4a, step4b = self.cargar_datos()
        print("✓ Datos cargados (Step 4A + Step 4B)")

        ranking = self.rankear_preguntas_por_tokens(step4a, step4b)
        print(f"✓ Ranking generado: {len(ranking)} preguntas procesadas")

        self.imprimir_ranking(ranking)
        self.generar_estadisticas_globales(ranking)
        if ranking:
            self.guardar_ranking(ranking)


if __name__ == "__main__":
    analizador = AnalizadorPreguntasTokens()
    analizador.ejecutar()
