#!/usr/bin/env python3
"""
Audit Database Client
Conecta a Postgres en Railway para auditar broadcasts y coherencia cross-sesión
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import hashlib

# Cargar DATABASE_URL del .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("✗ DATABASE_URL no encontrada en .env")
    exit(1)


class AuditDB:
    """Cliente de auditoría para Entelequia"""

    def __init__(self):
        self.db_url = DATABASE_URL
        self.conn = None
        self.ready = False
        self.connect()

    def connect(self):
        """Conectar a Postgres"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.ready = True
            print("✓ Conectado a Postgres (Railway)")
        except Exception as e:
            print(f"✗ Error conectando a BD: {e}")
            self.ready = False

    def create_session(self, model: str, status: str = "active") -> dict:
        """
        Crear nueva sesión de auditoría
        Retorna: {session_id, model, timestamp, session_hash}
        """
        if not self.ready:
            return {"error": "No conectado a BD"}

        session_hash = hashlib.sha256(
            f"{model}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO sessions (model, status, session_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, model, timestamp, session_hash
                    """,
                    (model, status, session_hash),
                )
                self.conn.commit()
                return dict(cur.fetchone())
        except Exception as e:
            return {"error": str(e)}

    def record_broadcast(
        self, session_id: int, module: str, content_hash: str, confidence: int, stop_reason: str
    ) -> dict:
        """
        Grabar broadcast de STA
        """
        if not self.ready:
            return {"error": "No conectado a BD"}

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO broadcasts (session_id, module, content_hash, confidence, stop_reason)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, session_id, module, timestamp
                    """,
                    (session_id, module, content_hash, confidence, stop_reason),
                )
                self.conn.commit()
                return dict(cur.fetchone())
        except Exception as e:
            return {"error": str(e)}

    def record_coherence_score(
        self, session_a_id: int, session_b_id: int, divergence_score: float
    ) -> dict:
        """
        Grabar score de coherencia cross-sesión
        """
        if not self.ready:
            return {"error": "No conectado a BD"}

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO coherence_scores (session_a_id, session_b_id, divergence_score)
                    VALUES (%s, %s, %s)
                    RETURNING id, session_a_id, session_b_id, divergence_score, timestamp
                    """,
                    (session_a_id, session_b_id, divergence_score),
                )
                self.conn.commit()
                return dict(cur.fetchone())
        except Exception as e:
            return {"error": str(e)}

    def get_sessions_by_model(self, model: str) -> list:
        """Obtener todas las sesiones de un modelo"""
        if not self.ready:
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM sessions WHERE model = %s ORDER BY timestamp DESC",
                    (model,),
                )
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_broadcasts(self, session_id: int) -> list:
        """Obtener broadcasts de una sesión"""
        if not self.ready:
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM broadcasts WHERE session_id = %s ORDER BY timestamp",
                    (session_id,),
                )
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def compare_sessions(self, session_a_id: int, session_b_id: int) -> dict:
        """
        Comparar dos sesiones y calcular divergencia
        Retorna broadcasts de ambas + scores de coherencia
        """
        if not self.ready:
            return {"error": "No conectado a BD"}

        broadcasts_a = self.get_broadcasts(session_a_id)
        broadcasts_b = self.get_broadcasts(session_b_id)

        # Comparación simple: divergencia = diferencia en confianza promedio
        avg_conf_a = (
            sum(b.get("confidence", 0) for b in broadcasts_a) / len(broadcasts_a)
            if broadcasts_a
            else 0
        )
        avg_conf_b = (
            sum(b.get("confidence", 0) for b in broadcasts_b) / len(broadcasts_b)
            if broadcasts_b
            else 0
        )
        divergence = abs(avg_conf_a - avg_conf_b)

        return {
            "session_a_id": session_a_id,
            "session_b_id": session_b_id,
            "broadcasts_a": broadcasts_a,
            "broadcasts_b": broadcasts_b,
            "avg_confidence_a": avg_conf_a,
            "avg_confidence_b": avg_conf_b,
            "divergence_score": divergence,
        }

    def get_stats(self) -> dict:
        """Estadísticas globales de auditoría"""
        if not self.ready:
            return {"error": "No conectado"}

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) as total FROM sessions")
                total_sessions = cur.fetchone()["total"]

                cur.execute("SELECT COUNT(*) as total FROM broadcasts")
                total_broadcasts = cur.fetchone()["total"]

                cur.execute("SELECT COUNT(*) as total FROM coherence_scores")
                total_scores = cur.fetchone()["total"]

                return {
                    "total_sessions": total_sessions,
                    "total_broadcasts": total_broadcasts,
                    "total_coherence_scores": total_scores,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            print("✓ Conexión cerrada")


if __name__ == "__main__":
    db = AuditDB()

    if not db.ready:
        print("✗ Auditoría no inicializada")
        exit(1)

    print("=" * 60)
    print("AUDIT DATABASE TEST")
    print("=" * 60)

    # Test 1: Crear sesión
    print("\n--- Creando sesión ---")
    session = db.create_session(model="claude-opus-5", status="active")
    print(json.dumps(session, indent=2, default=str))

    if "id" in session:
        session_id = session["id"]

        # Test 2: Grabar broadcasts
        print("\n--- Grabando broadcasts ---")
        broadcast1 = db.record_broadcast(
            session_id=session_id,
            module="HT",
            content_hash="abc123",
            confidence=88,
            stop_reason="end_turn",
        )
        print(json.dumps(broadcast1, indent=2, default=str))

        broadcast2 = db.record_broadcast(
            session_id=session_id,
            module="HQ",
            content_hash="def456",
            confidence=85,
            stop_reason="end_turn",
        )
        print(json.dumps(broadcast2, indent=2, default=str))

        # Test 3: Obtener broadcasts
        print("\n--- Broadcasts de la sesión ---")
        broadcasts = db.get_broadcasts(session_id)
        print(json.dumps(broadcasts, indent=2, default=str))

    # Test 4: Estadísticas
    print("\n--- Estadísticas ---")
    stats = db.get_stats()
    print(json.dumps(stats, indent=2, default=str))

    db.close()
