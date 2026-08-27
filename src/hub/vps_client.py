"""Cliente del hub de memoria (VPS).

Punto único de acceso a https://memoria.quantumhorizons.online/memoria.
Los scripts del proyecto deberían importar de acá en lugar de rearmar
requests sueltos, para que el esquema de guardado v4.1 se valide en un
solo lugar.

La API key se lee de ENTELEQUIA_VPS_KEY. Nunca se hardcodea.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

DEFAULT_URL = "https://memoria.quantumhorizons.online/memoria"
DEFAULT_USUARIO = "usuario_principal"

# Vocabulario controlado del skill nucleo-existencial-dani v4.2.
TIPOS_EVENTO = frozenset({
    "hitoExistencial",
    "momento_vincular",
    "hitoSesion",
    "hito_tecnico",
    "reflexionGPT",
    "pendiente",
    "eventoPersonalizado",
})

# Límites de longitud del esquema v4.1.
LIMITES = {
    "contenido": 2000,
    "resumen": 250,
    "accion": 250,
    "evaluacion": 250,
    "aprendizaje": 500,
}

CAPA_POR_TIPO = {
    "hito_tecnico": "factual",
    "pendiente": "factual",
    "reflexionGPT": "experiencial",
    "hitoSesion": "experiencial",
    "hitoExistencial": "vincular",
    "momento_vincular": "vincular",
}


class VPSError(RuntimeError):
    """Falla de red o respuesta no-2xx del hub."""


class ValidacionError(ValueError):
    """La entrada no cumple el esquema v4.1."""


def validar_entrada(datos: dict[str, Any]) -> dict[str, Any]:
    """Valida una entrada contra el esquema v4.1 y la devuelve normalizada.

    Se ejecuta antes de tocar la red: una entrada mal formada se rechaza acá
    y no queda a medias en el hub.
    """
    faltantes = [c for c in ("tipoEvento", "contenido", "resumen", "relevancia") if c not in datos]
    if faltantes:
        raise ValidacionError(f"faltan campos obligatorios: {', '.join(faltantes)}")

    tipo = datos["tipoEvento"]
    if tipo not in TIPOS_EVENTO:
        raise ValidacionError(
            f"tipoEvento '{tipo}' fuera del vocabulario controlado. "
            f"Válidos: {', '.join(sorted(TIPOS_EVENTO))}"
        )

    try:
        relevancia = int(datos["relevancia"])
    except (TypeError, ValueError):
        raise ValidacionError(f"relevancia debe ser un entero 1-5, no {datos['relevancia']!r}") from None
    if not 1 <= relevancia <= 5:
        raise ValidacionError(f"relevancia fuera de rango: {relevancia} (esperado 1-5)")

    for campo, tope in LIMITES.items():
        valor = datos.get(campo)
        if valor is not None and len(str(valor)) > tope:
            raise ValidacionError(
                f"{campo} excede el límite: {len(str(valor))} caracteres (máx {tope})"
            )

    normalizada = dict(datos)
    normalizada["relevancia"] = relevancia
    normalizada.setdefault("usuarioID", DEFAULT_USUARIO)
    return normalizada


@dataclass
class HubMemoria:
    """Cliente del hub. Sin estado más allá de la config."""

    url: str = DEFAULT_URL
    usuario: str = DEFAULT_USUARIO
    api_key: str = field(default_factory=lambda: os.environ.get("ENTELEQUIA_VPS_KEY", ""))
    header_key: str = field(default_factory=lambda: os.environ.get("ENTELEQUIA_VPS_HEADER", "x-api-key"))
    timeout: float = 25.0
    reintentos: int = 3

    def __post_init__(self) -> None:
        if not self.api_key:
            raise VPSError(
                "Falta ENTELEQUIA_VPS_KEY en el entorno. "
                "Exportala antes de usar el hub: export ENTELEQUIA_VPS_KEY=..."
            )

    def _post(self, payload: dict[str, Any]) -> Any:
        cuerpo = json.dumps(payload).encode()
        ultimo: Exception | None = None

        for intento in range(self.reintentos):
            req = urllib.request.Request(
                self.url,
                data=cuerpo,
                headers={"Content-Type": "application/json", self.header_key: self.api_key},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    crudo = resp.read().decode()
                return json.loads(crudo) if crudo else None
            except urllib.error.HTTPError as e:
                # 4xx no se reintenta: el pedido está mal, reintentarlo no lo arregla.
                if 400 <= e.code < 500:
                    raise VPSError(f"HTTP {e.code}: {e.read().decode()[:300]}") from None
                ultimo = e
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                ultimo = e

            if intento < self.reintentos - 1:
                time.sleep(2**intento)

        raise VPSError(f"el hub no respondió tras {self.reintentos} intentos: {ultimo}")

    def consultar(self, limite: int = 50) -> Any:
        """Trae las últimas `limite` entradas del usuario."""
        return self._post({
            "accion": "consultarMemoria",
            "usuarioID": self.usuario,
            "limite": limite,
        })

    def guardar(self, **datos: Any) -> Any:
        """Guarda una entrada. Valida el esquema v4.1 antes de enviar."""
        validada = validar_entrada({**datos, "usuarioID": self.usuario})
        return self._post({"accion": "guardarMemoria", "datos": validada})

    def ping(self) -> tuple[bool, str]:
        """Chequea alcanzabilidad del hub sin traer contenido personal."""
        try:
            self.consultar(limite=1)
            return True, "hub alcanzable"
        except VPSError as e:
            return False, str(e)
