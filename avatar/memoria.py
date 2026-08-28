"""Almacén de memoria del avatar.

Entorno cerrado: todo vive en un SQLite dentro del disco dedicado. No hay
dependencia de red para leer ni escribir memoria — sólo la inferencia sale
por API.

El esquema replica el v4.1 del núcleo, así que las entradas son
intercambiables con las del hub remoto si más adelante se sincronizan.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

TIPOS_EVENTO = (
    "hitoExistencial", "momento_vincular", "hitoSesion",
    "hito_tecnico", "reflexionGPT", "pendiente", "eventoPersonalizado",
)

CAPA_POR_TIPO = {
    "hito_tecnico": "factual", "pendiente": "factual",
    "reflexionGPT": "experiencial", "hitoSesion": "experiencial",
    "hitoExistencial": "vincular", "momento_vincular": "vincular",
    "eventoPersonalizado": "factual",
}

ESQUEMA = """
CREATE TABLE IF NOT EXISTS memoria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    tipoEvento  TEXT NOT NULL,
    capa        TEXT NOT NULL,
    contenido   TEXT NOT NULL,
    resumen     TEXT NOT NULL,
    accion      TEXT,
    evaluacion  TEXT,
    aprendizaje TEXT,
    relevancia  INTEGER NOT NULL CHECK (relevancia BETWEEN 1 AND 5)
);
CREATE INDEX IF NOT EXISTS idx_relevancia ON memoria(relevancia DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_ts ON memoria(ts DESC);

CREATE TABLE IF NOT EXISTS turnos (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    sesion   TEXT NOT NULL,
    ts       TEXT NOT NULL,
    rol      TEXT NOT NULL,
    texto    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_turnos ON turnos(sesion, id);
"""

ESQUEMA_FTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS memoria_fts
USING fts5(contenido, resumen, content='memoria', content_rowid='id');

CREATE TRIGGER IF NOT EXISTS memoria_ai AFTER INSERT ON memoria BEGIN
    INSERT INTO memoria_fts(rowid, contenido, resumen)
    VALUES (new.id, new.contenido, new.resumen);
END;
CREATE TRIGGER IF NOT EXISTS memoria_ad AFTER DELETE ON memoria BEGIN
    INSERT INTO memoria_fts(memoria_fts, rowid, contenido, resumen)
    VALUES ('delete', old.id, old.contenido, old.resumen);
END;
"""


@dataclass
class Entrada:
    id: int
    ts: str
    tipoEvento: str
    capa: str
    contenido: str
    resumen: str
    relevancia: int

    def linea(self) -> str:
        return f"[{self.ts[:10]} · {self.tipoEvento} · rel {self.relevancia}] {self.resumen}"


class AlmacenLocal:
    """Memoria en SQLite. Usa FTS5 si está disponible; si no, cae a LIKE."""

    def __init__(self, ruta: str):
        os.makedirs(os.path.dirname(os.path.abspath(ruta)) or ".", exist_ok=True)
        self.ruta = ruta
        self.con = sqlite3.connect(ruta)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(ESQUEMA)
        try:
            self.con.executescript(ESQUEMA_FTS)
            self.fts = True
        except sqlite3.OperationalError:
            self.fts = False   # build de SQLite sin FTS5
        self.con.commit()

    # -- escritura ---------------------------------------------------------

    def guardar(self, tipoEvento: str, contenido: str, resumen: str,
                relevancia: int, accion: str = "", evaluacion: str = "",
                aprendizaje: str = "") -> int:
        if tipoEvento not in TIPOS_EVENTO:
            raise ValueError(f"tipoEvento inválido: {tipoEvento}")
        if not 1 <= int(relevancia) <= 5:
            raise ValueError(f"relevancia fuera de rango: {relevancia}")

        cur = self.con.execute(
            "INSERT INTO memoria (ts, tipoEvento, capa, contenido, resumen,"
            " accion, evaluacion, aprendizaje, relevancia)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"),
             tipoEvento, CAPA_POR_TIPO.get(tipoEvento, "factual"),
             contenido[:2000], resumen[:250], accion[:250],
             evaluacion[:250], aprendizaje[:500], int(relevancia)),
        )
        self.con.commit()
        return cur.lastrowid

    def guardar_turno(self, sesion: str, rol: str, texto: str) -> None:
        self.con.execute(
            "INSERT INTO turnos (sesion, ts, rol, texto) VALUES (?,?,?,?)",
            (sesion, datetime.now(timezone.utc).isoformat(timespec="seconds"), rol, texto),
        )
        self.con.commit()

    # -- lectura -----------------------------------------------------------

    def _filas(self, sql: str, args: Iterable = ()) -> list[Entrada]:
        return [
            Entrada(r["id"], r["ts"], r["tipoEvento"], r["capa"],
                    r["contenido"], r["resumen"], r["relevancia"])
            for r in self.con.execute(sql, tuple(args))
        ]

    def anclas(self, n: int = 12) -> list[Entrada]:
        """Las entradas de mayor relevancia: lo que define la identidad."""
        return self._filas(
            "SELECT * FROM memoria WHERE relevancia >= 4"
            " ORDER BY relevancia DESC, id DESC LIMIT ?", (n,))

    def recientes(self, n: int = 10) -> list[Entrada]:
        return self._filas("SELECT * FROM memoria ORDER BY id DESC LIMIT ?", (n,))

    def buscar(self, consulta: str, n: int = 8) -> list[Entrada]:
        """Recupera por contenido. Pondera relevancia sobre el match crudo."""
        terminos = [t for t in "".join(
            c if c.isalnum() or c.isspace() else " " for c in consulta
        ).split() if len(t) > 3]
        if not terminos:
            return []

        if self.fts:
            try:
                return self._filas(
                    "SELECT m.* FROM memoria_fts f JOIN memoria m ON m.id = f.rowid"
                    " WHERE memoria_fts MATCH ?"
                    " ORDER BY m.relevancia DESC, bm25(memoria_fts) LIMIT ?",
                    (" OR ".join(terminos), n))
            except sqlite3.OperationalError:
                pass

        cond = " OR ".join(["contenido LIKE ? OR resumen LIKE ?"] * len(terminos))
        args = [x for t in terminos for x in (f"%{t}%", f"%{t}%")]
        return self._filas(
            f"SELECT * FROM memoria WHERE {cond}"
            f" ORDER BY relevancia DESC, id DESC LIMIT ?", (*args, n))

    def contexto(self, consulta: str) -> list[Entrada]:
        """Las tres vías juntas, deduplicadas, en orden cronológico.

        Anclas (identidad) + recuperado por tema + reciente (continuidad).
        La deduplicación por id evita repetir la misma entrada tres veces.
        """
        vistos: dict[int, Entrada] = {}
        for grupo in (self.anclas(), self.buscar(consulta), self.recientes()):
            for e in grupo:
                vistos.setdefault(e.id, e)
        return sorted(vistos.values(), key=lambda e: e.id)

    def historial(self, sesion: str, n: int = 20) -> list[dict]:
        filas = list(self.con.execute(
            "SELECT rol, texto FROM (SELECT * FROM turnos WHERE sesion = ?"
            " ORDER BY id DESC LIMIT ?) ORDER BY id", (sesion, n)))
        return [{"role": r["rol"], "content": r["texto"]} for r in filas]

    def stats(self) -> dict:
        f = self.con.execute(
            "SELECT COUNT(*) n, COALESCE(AVG(relevancia),0) rel FROM memoria").fetchone()
        por_capa = {r["capa"]: r["n"] for r in self.con.execute(
            "SELECT capa, COUNT(*) n FROM memoria GROUP BY capa")}
        return {"entradas": f["n"], "relevancia_media": round(f["rel"], 2),
                "por_capa": por_capa, "fts": self.fts, "ruta": self.ruta}

    def cerrar(self) -> None:
        self.con.close()
