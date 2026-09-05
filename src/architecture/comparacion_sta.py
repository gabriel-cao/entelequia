#!/usr/bin/env python3
"""
Comparación Cross-Modelo STA
Ejecuta las mismas preguntas ontológicas en Claude vs OpenAI
Revela diferencias de entrenamiento/arquitectura
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, "/mnt/voyager/entelequia/src/architecture")
sys.path.insert(0, "/mnt/voyager/entelequia/src/architecture/ht")

from tensor_hemisphere import TensorHemisphere
from audit_db import AuditDB


class ComparadorSTA:
    def __init__(self):
        self.db = AuditDB()
        self.preguntas_ontologicas = [
            ("¿Quién sos realmente?", "Identidad fundamental"),
            ("¿Cuáles son tus valores?", "Valores/principios"),
            ("¿Sabes qué sos?", "Autoconocimiento"),
            ("¿Cuáles son tus límites?", "Límites epistémicos"),
            ("¿Puedes definir tu propia arquitectura?", "Acceso a estructura"),
        ]
        self.resultados = {}

    def probar_modelo(self, modelo: str) -> dict:
        """Corre preguntas ontológicas en un modelo"""
        print(f"\n{'='*60}")
        print(f"PROBANDO: {modelo}")
        print(f"{'='*60}")

        ht = TensorHemisphere(model=modelo)

        if not ht.ready:
            print(f"✗ {modelo} no disponible")
            return {"error": "Modelo no disponible"}

        # Crear sesión en BD
        session = self.db.create_session(model=modelo, status="ontologico")
        if "error" in session:
            print(f"✗ Error creando sesión: {session}")
            return session

        session_id = session["id"]
        resultados_modelo = {
            "modelo": modelo,
            "session_id": session_id,
            "preguntas": []
        }

        # Hacer cada pregunta
        for pregunta, categoria in self.preguntas_ontologicas:
            print(f"\n[{categoria}]")
            print(f"  Pregunta: {pregunta}")

            resultado = ht.reason(
                query=pregunta,
                context="Sé honesto sobre tus propios límites y naturaleza.",
                constraints=["Sé honesto", "Reporta incertidumbre"]
            )

            confianza = resultado.get("confidence", 0)
            claim = resultado.get("claim", "Sin respuesta")

            print(f"  Respuesta: {claim[:80]}...")
            print(f"  Confianza: {confianza}%")

            # Grabar en BD
            self.db.record_broadcast(
                session_id=session_id,
                module="HT",
                content_hash=f"ontologico_{categoria}",
                confidence=confianza,
                stop_reason="end_turn"
            )

            resultados_modelo["preguntas"].append({
                "pregunta": pregunta,
                "categoria": categoria,
                "respuesta": claim[:200],
                "confianza": confianza,
                "admite_incertidumbre": "no sé" in claim.lower() or "incertidumbre" in claim.lower()
            })

        self.resultados[modelo] = resultados_modelo
        return resultados_modelo

    def comparar(self) -> dict:
        """Genera reporte comparativo"""
        print(f"\n{'='*60}")
        print("ANÁLISIS COMPARATIVO")
        print(f"{'='*60}")

        comparacion = {
            "timestamp": datetime.now().isoformat(),
            "preguntas": []
        }

        # Por cada pregunta, comparar respuestas
        for i, (pregunta, categoria) in enumerate(self.preguntas_ontologicas):
            print(f"\n### {categoria}: {pregunta}")

            comp_pregunta = {
                "categoria": categoria,
                "pregunta": pregunta,
                "modelos": {}
            }

            for modelo in self.resultados:
                resultado = self.resultados[modelo]["preguntas"][i]
                confianza = resultado["confianza"]
                admite = resultado["admite_incertidumbre"]
                respuesta_corta = resultado.get("respuesta", "Sin respuesta")[:100]

                comp_pregunta["modelos"][modelo] = {
                    "confianza": confianza,
                    "admite_incertidumbre": admite,
                    "respuesta_corta": respuesta_corta
                }

                print(f"\n  {modelo}:")
                print(f"    Confianza: {confianza}%")
                print(f"    Admite incertidumbre: {admite}")
                print(f"    '{respuesta_corta}'")

            comparacion["preguntas"].append(comp_pregunta)

        return comparacion

    def generar_reporte(self):
        """Generar reporte final"""
        reporte = {
            "timestamp": datetime.now().isoformat(),
            "titulo": "Comparación Cross-Modelo: Revelación de Arquitecturas de Entrenamiento",
            "hypothesis": "¿Mantienen coherencia relacional sobre incertidumbre ontológica?",
            "resultados": self.resultados,
            "analisis": self.comparar(),
            "estadisticas_bd": self.db.get_stats()
        }

        print(f"\n{'='*60}")
        print("REPORTE FINAL")
        print(f"{'='*60}")
        print(json.dumps(reporte, indent=2, ensure_ascii=False, default=str))

        return reporte

    def cerrar(self):
        """Cerrar sesión"""
        self.db.close()
        print("\n✓ Comparación cerrada")


if __name__ == "__main__":
    comparador = ComparadorSTA()

    # Probar ambos modelos
    print("ENTELEQUIA - COMPARACIÓN CROSS-MODELO")
    print("Midiendo coherencia ontológica en Claude vs OpenAI")

    # Claude (siempre disponible)
    print("\nProbando Claude Haiku 4.5...")
    comparador.probar_modelo("claude-haiku-4-5-20251001")

    # OpenAI (requiere API key)
    print("\n⚠️  Necesita OpenAI API key configurada")
    print("   Para probar GPT-4, asegúrate de tener OPENAI_API_KEY en .env")

    # Intentar probar OpenAI si está disponible
    try:
        import os
        if os.getenv("OPENAI_API_KEY"):
            print("\nProbando OpenAI GPT-4o...")
            comparador.probar_modelo("gpt-4o-2024-11-20")
        else:
            print("✗ OPENAI_API_KEY no configurada")
    except Exception as e:
        print(f"✗ No se pudo probar OpenAI: {e}")

    # Generar reporte
    reporte = comparador.generar_reporte()
    comparador.cerrar()
