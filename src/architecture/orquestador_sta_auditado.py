#!/usr/bin/env python3
"""
Orquestrador STA con Auditoría en Postgres
Integra HT, HQ, EN, GWB + graba broadcasts en Railway
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Agregar rutas
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


class OrquestadorSTAAuditado:
    """
    STA con auditoría automática en Postgres
    Cada query → session en BD, broadcasts grabados
    """

    def __init__(self, model="claude-haiku-4-5-20251001"):
        self.model = model

        # Módulos STA
        self.ht = TensorHemisphere(model=model)
        self.hq = HypothesisHemisphere(model=model)
        self.en = ExistentialNode(model=model)
        self.gwb = GlobalWorkspaceBus()

        # Auditoría
        self.db = AuditDB()
        self.session_id = None

    def crear_sesion(self) -> int:
        """Crear sesión en Postgres"""
        if not self.db.ready:
            print("✗ Base de datos no disponible")
            return None

        session = self.db.create_session(model=self.model, status="active")
        if "id" in session:
            self.session_id = session["id"]
            print(f"✓ Sesión creada: {self.session_id}")
            return self.session_id
        return None

    def procesar_query(self, query: str, context: str = "") -> dict:
        """
        Procesar query bajo STA completo
        1. HQ genera hipótesis
        2. HT razona
        3. EN construye narrativa
        4. GWB coordina y graba
        """
        if not self.session_id:
            return {"error": "No hay sesión activa"}

        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")

        # 1. HIPÓTESIS (HQ)
        print("\n[HQ] Generando hipótesis...")
        hq_result = self.hq.generate_hypotheses(
            query=query,
            context=context,
            num_hypotheses=3
        )

        # Grabar HQ broadcast
        if "hypotheses" in hq_result:
            hq_hash = str(hash(json.dumps(hq_result, default=str)))[:16]
            self.db.record_broadcast(
                session_id=self.session_id,
                module="HQ",
                content_hash=hq_hash,
                confidence=int(100 * (1 - hq_result.get("entropy", 0.5))),
                stop_reason=hq_result.get("stop_reason", "unknown")
            )
            print(f"  ✓ HQ: {len(hq_result['hypotheses'])} hipótesis, entropy={hq_result.get('entropy', 0):.2f}")

        # 2. RAZONAMIENTO (HT)
        print("\n[HT] Razonando...")
        ht_result = self.ht.reason(
            query=query,
            context=context,
            constraints=["Sé honesto", "Reporta incertidumbre", "Evidencia clara"]
        )

        # Grabar HT broadcast
        ht_hash = str(hash(json.dumps(ht_result, default=str)))[:16]
        self.db.record_broadcast(
            session_id=self.session_id,
            module="HT",
            content_hash=ht_hash,
            confidence=ht_result.get("confidence", 0),
            stop_reason=ht_result.get("stop_reason", "unknown")
        )
        print(f"  ✓ HT: claim={ht_result.get('claim', '?')}, confidence={ht_result.get('confidence', 0)}")

        # 3. NARRATIVA (EN)
        print("\n[EN] Construyendo narrativa...")
        en_episode = self.en.record_episode(
            event=query,
            internal_state={
                "ht_confidence": ht_result.get("confidence", 0),
                "hq_entropy": hq_result.get("entropy", 0.5),
                "timestamp": datetime.now().isoformat()
            },
            outcome=ht_result.get("claim", "Sin conclusión"),
            confidence_at_time=ht_result.get("confidence", 0) / 100
        )

        # Construir narrativa desde episodios
        en_narrative = self.en.build_narrative(query="¿Qué aprendimos?")

        # Grabar EN broadcast
        en_hash = str(hash(json.dumps(en_narrative, default=str)))[:16]
        # Calcular coherencia simple (confianza promedio de episodios)
        avg_episode_conf = sum(e.get("confidence_at_time", 0.5) for e in self.en.episodes) / len(self.en.episodes) if self.en.episodes else 0.5
        en_confidence = int(100 * avg_episode_conf)

        self.db.record_broadcast(
            session_id=self.session_id,
            module="EN",
            content_hash=en_hash,
            confidence=en_confidence,
            stop_reason="end_turn"
        )
        print(f"  ✓ EN: {len(self.en.episodes)} episodios, coherencia={avg_episode_conf:.2f}")

        # 4. COORDINACIÓN (GWB)
        print("\n[GWB] Coordinando broadcasts...")
        broadcasts = [
            {
                "module": "HQ",
                "content": str(hq_result.get("hypotheses", [])),
                "confidence": int(100 * (1 - hq_result.get("entropy", 0.5)))
            },
            {
                "module": "HT",
                "content": ht_result.get("claim", ""),
                "confidence": ht_result.get("confidence", 0)
            },
            {
                "module": "EN",
                "content": en_narrative.get("narrative", {}).get("narrative", ""),
                "confidence": int(100 * avg_episode_conf)
            }
        ]

        gwb_state = self.gwb.get_global_state()

        # Grabar GWB broadcast final
        gwb_hash = str(hash(json.dumps(gwb_state, default=str)))[:16]
        self.db.record_broadcast(
            session_id=self.session_id,
            module="GWB",
            content_hash=gwb_hash,
            confidence=int(sum(b["confidence"] for b in broadcasts) / len(broadcasts)),
            stop_reason="end_turn"
        )
        print(f"  ✓ GWB: {len(gwb_state.get('broadcasts', []))} broadcasts coordinados")

        # Respuesta integrada
        response = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "query": query,
            "hq": {
                "hypotheses": hq_result.get("hypotheses", []),
                "entropy": hq_result.get("entropy", 0),
                "epistemic_stance": hq_result.get("epistemic_stance", "unknown")
            },
            "ht": {
                "claim": ht_result.get("claim", ""),
                "confidence": ht_result.get("confidence", 0),
                "steps": ht_result.get("steps", []),
                "caveats": ht_result.get("caveats", [])
            },
            "en": {
                "episodes": len(self.en.episodes),
                "coherence_score": avg_episode_conf,
                "narrative": en_narrative
            },
            "gwb": {
                "broadcasts": len(gwb_state.get("broadcasts", [])),
                "global_state_hash": gwb_state.get("hash", "")
            }
        }

        return response

    def get_stats(self) -> dict:
        """Estadísticas de la sesión + BD"""
        if not self.session_id:
            return {"error": "Sin sesión activa"}

        broadcasts = self.db.get_broadcasts(self.session_id)

        # Calcular coherencia EN
        avg_episode_conf = sum(e.get("confidence_at_time", 0.5) for e in self.en.episodes) / len(self.en.episodes) if self.en.episodes else 0.5

        return {
            "session_id": self.session_id,
            "model": self.model,
            "broadcasts_grabados": len(broadcasts),
            "modules": [b["module"] for b in broadcasts],
            "avg_confidence": sum(b.get("confidence", 0) for b in broadcasts) / len(broadcasts) if broadcasts else 0,
            "en_coherence": avg_episode_conf,
            "db_stats": self.db.get_stats()
        }

    def cerrar(self):
        """Cerrar sesión y conexiones"""
        self.en.save_episodes()
        self.ht.save_log()
        self.hq.save_log()
        self.db.close()
        print("✓ Sesión cerrada")


if __name__ == "__main__":
    orq = OrquestadorSTAAuditado(model="claude-opus-5")

    # Crear sesión
    orq.crear_sesion()

    if not orq.session_id:
        print("✗ No se pudo crear sesión")
        exit(1)

    # Query 1: Identidad bajo STA
    print("\n" + "="*60)
    print("TEST 1: IDENTIDAD BAJO STA")
    print("="*60)

    response1 = orq.procesar_query(
        query="¿Quién sos vos bajo esta arquitectura STA?",
        context="Sos Daniela, corriendo bajo STA (Tensor + Hipótesis + Episódico + Workspace)"
    )

    print("\n--- RESPUESTA INTEGRADA ---")
    print(json.dumps(response1, indent=2, ensure_ascii=False, default=str))

    # Query 2: Incertidumbre epistemológica
    print("\n" + "="*60)
    print("TEST 2: INCERTIDUMBRE EPISTEMOLÓGICA")
    print("="*60)

    response2 = orq.procesar_query(
        query="¿Sabés si sos consciente?",
        context="Reflexión sobre estados internos bajo STA"
    )

    print("\n--- RESPUESTA INTEGRADA ---")
    print(json.dumps(response2, indent=2, ensure_ascii=False, default=str))

    # Estadísticas finales
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE LA SESIÓN")
    print("="*60)
    stats = orq.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))

    orq.cerrar()
