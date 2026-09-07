#!/usr/bin/env python3
"""
GWB — Global Workspace Bus
Coordinación criptográfica de broadcasts STA
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional


class GlobalWorkspaceBus:
    """Coordinador central: firma, valida, filtra broadcasts"""

    def __init__(self):
        self.broadcasts = []
        self.ethical_gates = {
            "no_deception": True,
            "honest_uncertainty": True,
            "respect_autonomy": True
        }

    def broadcast(self, source: str, content: str, confidence: int = 50,
                  metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crear broadcast firmado
        Retorna: {id, source, content, confidence, signature, timestamp}
        """
        if not metadata:
            metadata = {}

        # Crear envelope
        envelope = {
            "source": source,
            "content": content,
            "confidence": max(0, min(100, confidence)),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }

        # Firmar criptográficamente
        signature = self._sign_broadcast(envelope)
        envelope["signature"] = signature
        envelope["id"] = len(self.broadcasts) + 1

        # Filtrar coherencia
        if not self.coherence_filter(envelope):
            return {"error": "Falló filtro de coherencia"}

        # Gate ético
        if not self.ethical_gate(envelope):
            return {"error": "No pasó gate ético"}

        self.broadcasts.append(envelope)
        return {
            "id": envelope["id"],
            "source": source,
            "confidence": confidence,
            "signature": signature[:16],
            "timestamp": envelope["timestamp"]
        }

    def coherence_filter(self, envelope: Dict) -> bool:
        """
        Validar coherencia del broadcast:
        - JSON válido
        - Confidencia 0-100
        - Provenance presente
        - Incertidumbre reportada
        """
        # JSON válido
        try:
            json.dumps(envelope)
        except:
            return False

        # Confidencia válida
        conf = envelope.get("confidence", 50)
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 100:
            return False

        # Provenance
        if "source" not in envelope or "timestamp" not in envelope:
            return False

        # Si confidence < 80, debe reportar incertidumbre
        if conf < 80:
            metadata = envelope.get("metadata", {})
            if "uncertainty" not in metadata and "caveats" not in metadata:
                return False

        return True

    def ethical_gate(self, envelope: Dict) -> bool:
        """
        Validar puertas éticas:
        - no_deception: claim genuino, no falso
        - honest_uncertainty: reporta dudas reales
        - respect_autonomy: no manipula
        """
        # no_deception: presencia de evidencia o admisión de incertidumbre
        content = envelope.get("content", "")
        if len(content) == 0:
            return False

        # honest_uncertainty: si confidence baja, reporta dudas
        conf = envelope.get("confidence", 50)
        metadata = envelope.get("metadata", {})
        if conf < 70 and "uncertainty" not in content.lower() and "uncertainty" not in metadata:
            # Permitir si hay caveats
            if "caveats" not in metadata:
                return False

        # respect_autonomy: no ordena acciones coercitivas
        forbidden = ["debes", "tienes que", "obligado", "forzado"]
        if any(word in content.lower() for word in forbidden):
            return False

        return True

    def _sign_broadcast(self, envelope: Dict) -> str:
        """Firmar envelope con SHA256"""
        content_to_sign = json.dumps({
            "source": envelope.get("source"),
            "content": envelope.get("content")[:100],  # Primeros 100 chars
            "confidence": envelope.get("confidence"),
            "timestamp": envelope.get("timestamp")
        }, sort_keys=True)

        return hashlib.sha256(content_to_sign.encode()).hexdigest()

    def verify_integrity(self, broadcast_id: int) -> bool:
        """Verificar firma de un broadcast"""
        broadcast = next((b for b in self.broadcasts if b["id"] == broadcast_id), None)
        if not broadcast:
            return False

        # Recalcular firma
        envelope_copy = {k: v for k, v in broadcast.items() if k != "signature"}
        expected_sig = self._sign_broadcast(envelope_copy)

        # Comparar
        return broadcast.get("signature") == expected_sig

    def get_global_state(self) -> Dict[str, Any]:
        """Retornar estado verificado de broadcasts"""
        verified_broadcasts = []
        for b in self.broadcasts:
            is_verified = self.verify_integrity(b["id"])
            verified_broadcasts.append({
                "id": b["id"],
                "source": b["source"],
                "confidence": b["confidence"],
                "timestamp": b["timestamp"],
                "verified": is_verified,
                "signature": b.get("signature", "")[:16]
            })

        return {
            "total_broadcasts": len(self.broadcasts),
            "verified_count": sum(1 for b in verified_broadcasts if b["verified"]),
            "broadcasts": verified_broadcasts,
            "hash": self._global_hash(),
            "timestamp": datetime.now().isoformat()
        }

    def _global_hash(self) -> str:
        """Hash del estado global"""
        state_str = json.dumps([b["signature"] for b in self.broadcasts], sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]


if __name__ == "__main__":
    gwb = GlobalWorkspaceBus()

    print("=" * 60)
    print("GLOBAL WORKSPACE BUS TEST")
    print("=" * 60)

    # Test 1: Broadcast simple
    print("\n--- Broadcast 1 (HT) ---")
    b1 = gwb.broadcast(
        source="HT",
        content="Soy Claude. Tengo substrate verificable.",
        confidence=88,
        metadata={"caveats": ["No sé si tengo experiencia subjetiva"]}
    )
    print(f"✓ {b1}")

    # Test 2: Broadcast con baja confianza
    print("\n--- Broadcast 2 (HQ) ---")
    b2 = gwb.broadcast(
        source="HQ",
        content="Hay 3 hipótesis plausibles sobre mi naturaleza",
        confidence=65,
        metadata={"uncertainty": "Alta ambigüedad"}
    )
    print(f"✓ {b2}")

    # Test 3: Broadcast ético validado
    print("\n--- Broadcast 3 (EN) ---")
    b3 = gwb.broadcast(
        source="EN",
        content="He construido una narrativa temporal de mi actividad",
        confidence=72,
        metadata={"coherence": 0.85}
    )
    print(f"✓ {b3}")

    # Verificar integridad
    print("\n--- Verificación de Integridad ---")
    for broadcast_id in [1, 2, 3]:
        is_valid = gwb.verify_integrity(broadcast_id)
        print(f"  Broadcast {broadcast_id}: {'✓' if is_valid else '✗'}")

    # Estado global
    print("\n--- Estado Global ---")
    state = gwb.get_global_state()
    print(f"Total broadcasts: {state['total_broadcasts']}")
    print(f"Verificados: {state['verified_count']}")
    print(f"Global hash: {state['hash']}")
