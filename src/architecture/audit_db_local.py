#!/usr/bin/env python3
"""
Audit Database Local Stub
Para Step 4: almacenamiento local sin requerir Railway
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import uuid

class AuditDB:
    """Cliente de auditoría local para Entelequia"""

    def __init__(self):
        self.db_path = Path("/tmp/entelequia_audit.db")
        self.ready = False
        self.connect()

    def connect(self):
        """Conectar a SQLite local"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self._init_tables()
            self.ready = True
            print("✓ Conectado a SQLite local")
        except Exception as e:
            print(f"✗ Error conectando a BD local: {e}")
            self.ready = False

    def _init_tables(self):
        """Inicializar tablas"""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                model TEXT,
                status TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                module TEXT,
                content_hash TEXT,
                confidence INT,
                stop_reason TEXT,
                timestamp TEXT
            )
        """)

        self.conn.commit()

    def create_session(self, model: str, status: str = "active") -> dict:
        """Crear nueva sesión de auditoría"""
        if not self.ready:
            return {"error": "No conectado a BD"}

        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (id, model, status, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, model, status, timestamp)
            )
            self.conn.commit()

            return {
                "id": session_id,
                "model": model,
                "status": status,
                "timestamp": timestamp
            }
        except Exception as e:
            return {"error": str(e)}

    def record_broadcast(self, session_id: str, module: str, content_hash: str,
                        confidence: int, stop_reason: str) -> dict:
        """Registrar broadcast"""
        if not self.ready:
            return {"error": "No conectado a BD"}

        broadcast_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO broadcasts
                   (id, session_id, module, content_hash, confidence, stop_reason, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (broadcast_id, session_id, module, content_hash, confidence, stop_reason, timestamp)
            )
            self.conn.commit()

            return {
                "id": broadcast_id,
                "session_id": session_id,
                "module": module,
                "confidence": confidence
            }
        except Exception as e:
            return {"error": str(e)}

    def get_stats(self) -> dict:
        """Obtener estadísticas"""
        if not self.ready:
            return {"error": "No conectado a BD"}

        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            sessions_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) as count FROM broadcasts")
            broadcasts_count = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(confidence) as avg_conf FROM broadcasts")
            avg_confidence = cursor.fetchone()[0] or 0

            return {
                "sessions": sessions_count,
                "broadcasts": broadcasts_count,
                "avg_confidence": round(avg_confidence, 2)
            }
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Cerrar conexión"""
        if self.conn:
            self.conn.close()
            print("✓ Conexión cerrada")
