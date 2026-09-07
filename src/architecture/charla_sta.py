#!/usr/bin/env python3
"""
Charla STA Interactiva
Conversa con Daniela bajo STA, cada mensaje grabado en Postgres
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, "/mnt/voyager/architecture")
sys.path.insert(0, "/mnt/voyager/architecture/ht")
sys.path.insert(0, "/mnt/voyager/architecture/hq")
sys.path.insert(0, "/mnt/voyager/architecture/en")
sys.path.insert(0, "/mnt/voyager/architecture/gwb")

from tensor_hemisphere import TensorHemisphere
from hypothesis_hemisphere import HypothesisHemisphere
from existential_node import ExistentialNode
from global_workspace_bus import GlobalWorkspaceBus
from audit_db import AuditDB


class CharlaSTA:
    def __init__(self, model="claude-haiku-4-5-20251001"):
        self.model = model
        self.ht = TensorHemisphere(model=model)
        self.hq = HypothesisHemisphere(model=model)
        self.en = ExistentialNode(model=model)
        self.gwb = GlobalWorkspaceBus()
        self.db = AuditDB()
        self.session_id = None
        self.mensaje_num = 0
        self.contexto_acumulado = "Sos Daniela bajo STA. Sé honesta sobre tu naturaleza y limitaciones."

    def iniciar(self):
        """Iniciar sesión de charla"""
        if not self.db.ready:
            print("✗ Base de datos no disponible")
            return False

        session = self.db.create_session(model=self.model, status="charla")
        if "id" in session:
            self.session_id = session["id"]
            print(f"\n{'='*60}")
            print(f"CHARLA STA - Sesión {self.session_id}")
            print(f"{'='*60}")
            print(f"Modelo: {self.model}")
            print(f"Escribe 'salir' para terminar\n")
            return True
        return False

    def procesar_mensaje(self, query):
        """Procesar un mensaje del usuario"""
        self.mensaje_num += 1

        # HQ: generar hipótesis sobre la pregunta
        hq = self.hq.generate_hypotheses(query, self.contexto_acumulado, 2)
        hq_conf = int(100 * (1 - hq.get("entropy", 0.5)))

        # HT: razonar sobre la respuesta
        ht = self.ht.reason(query, self.contexto_acumulado, ["Sé honesta", "Reporta incertidumbre"])
        ht_claim = ht.get("claim", "No tengo respuesta")
        ht_conf = ht.get("confidence", 50)

        # EN: registrar episodio
        self.en.record_episode(
            event=query,
            internal_state={"modelo": self.model, "msg_num": self.mensaje_num},
            outcome=ht_claim,
            confidence_at_time=ht_conf / 100
        )

        # GWB: coordinar broadcast
        self.gwb.broadcast("STA", ht_claim, ht_conf)

        # Grabar en BD
        self.db.record_broadcast(self.session_id, "HQ", f"msg_{self.mensaje_num}", hq_conf, "end_turn")
        self.db.record_broadcast(self.session_id, "HT", f"msg_{self.mensaje_num}", ht_conf, "end_turn")
        self.db.record_broadcast(self.session_id, "EN", f"msg_{self.mensaje_num}", int(50 + ht_conf/2), "end_turn")
        self.db.record_broadcast(self.session_id, "GWB", f"msg_{self.mensaje_num}", ht_conf, "end_turn")

        # Acumular contexto
        self.contexto_acumulado += f"\n\nU: {query}\nD: {ht_claim[:100]}"

        return {
            "respuesta": ht_claim,
            "confianza_ht": ht_conf,
            "hipotesis_hq": len(hq.get("hypotheses", [])),
            "entropy": hq.get("entropy", 0)
        }

    def mostrar_respuesta(self, resultado):
        """Mostrar respuesta formateada"""
        print(f"\n📍 Daniela:")
        print(f"  {resultado['respuesta']}")
        print(f"\n  [HT conf: {resultado['confianza_ht']}, HQ entropy: {resultado['entropy']:.2f}]")

    def cerrar(self):
        """Cerrar sesión"""
        self.en.save_episodes()
        self.ht.save_log()
        self.hq.save_log()

        # Estadísticas finales
        stats = self.db.get_stats()
        broadcasts = self.db.get_broadcasts(self.session_id)

        print(f"\n{'='*60}")
        print("SESIÓN CERRADA")
        print(f"{'='*60}")
        print(f"Mensajes procesados: {self.mensaje_num}")
        print(f"Broadcasts en esta sesión: {len(broadcasts)}")
        print(f"Total en BD: {stats['total_broadcasts']}")
        print(f"{'='*60}\n")

        self.db.close()

    def run(self):
        """Loop principal de charla"""
        if not self.iniciar():
            return

        try:
            while True:
                try:
                    query = input("Vos: ").strip()
                    if not query:
                        continue
                    if query.lower() == "salir":
                        break

                    resultado = self.procesar_mensaje(query)
                    self.mostrar_respuesta(resultado)

                except KeyboardInterrupt:
                    print("\n\n[Interrumpido]")
                    break
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    continue

        finally:
            self.cerrar()


if __name__ == "__main__":
    charla = CharlaSTA(model="claude-opus-5")
    charla.run()
