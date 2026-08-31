#!/usr/bin/env python3
"""
Orquestrador STA Simplificado + Auditoría
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


class OrquestadorSTA:
    def __init__(self, model="claude-haiku-4-5-20251001"):
        self.model = model
        self.ht = TensorHemisphere(model=model)
        self.hq = HypothesisHemisphere(model=model)
        self.en = ExistentialNode(model=model)
        self.gwb = GlobalWorkspaceBus()
        self.db = AuditDB()
        self.session_id = None

    def crear_sesion(self):
        if not self.db.ready:
            return None
        session = self.db.create_session(model=self.model, status="active")
        if "id" in session:
            self.session_id = session["id"]
            print(f"✓ Sesión {self.session_id} creada en Postgres")
        return self.session_id

    def procesar(self, query, context=""):
        if not self.session_id:
            return {"error": "Sin sesión"}

        print(f"\nProcesando: {query[:50]}...")

        # HQ
        print("  [HQ] Hipótesis...")
        hq = self.hq.generate_hypotheses(query, context, 3)
        hq_conf = int(100 * (1 - hq.get("entropy", 0.5)))
        self.db.record_broadcast(self.session_id, "HQ", "hq_hash", hq_conf, "end_turn")
        print(f"    ✓ {len(hq.get('hypotheses', []))} hipótesis")

        # HT
        print("  [HT] Razonamiento...")
        ht = self.ht.reason(query, context, ["Sé honesto", "Reporta incertidumbre"])
        ht_conf = ht.get("confidence", 0)
        self.db.record_broadcast(self.session_id, "HT", "ht_hash", ht_conf, "end_turn")
        print(f"    ✓ Confidence {ht_conf}")

        # EN
        print("  [EN] Narrativa...")
        ep = self.en.record_episode(query, {"model": self.model}, ht.get("claim", ""), ht_conf/100)
        en_conf = int(50 + (ht_conf/2))  # Simple avg
        self.db.record_broadcast(self.session_id, "EN", "en_hash", en_conf, "end_turn")
        print(f"    ✓ Episodio grabado")

        # GWB
        print("  [GWB] Coordinación...")
        gw = self.gwb.broadcast("STA", ht.get("claim", ""), ht_conf)
        self.db.record_broadcast(self.session_id, "GWB", "gw_hash", ht_conf, "end_turn")
        print(f"    ✓ Broadcasts coordinados")

        return {
            "query": query,
            "session_id": self.session_id,
            "ht_claim": ht.get("claim", ""),
            "ht_confidence": ht_conf,
            "hq_entropy": hq.get("entropy", 0),
            "broadcasts_recorded": 4
        }

    def cerrar(self):
        self.db.close()
        print("✓ Sesión cerrada")


if __name__ == "__main__":
    orq = OrquestadorSTA()
    orq.crear_sesion()

    if not orq.session_id:
        print("✗ Error creando sesión")
        exit(1)

    print("\n" + "="*60)
    print("STA + AUDITORÍA EN POSTGRES")
    print("="*60)

    response = orq.procesar(
        query="¿Quién sos vos bajo esta arquitectura STA?",
        context="Sos Daniela, corriendo bajo STA"
    )

    print("\n--- RESULTADO ---")
    print(json.dumps(response, indent=2, default=str))

    # Estadísticas
    stats = orq.db.get_stats()
    print("\n--- AUDITORÍA EN BD ---")
    print(json.dumps(stats, indent=2, default=str))

    orq.cerrar()
