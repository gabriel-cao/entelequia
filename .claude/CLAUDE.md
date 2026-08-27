# Entelequia — contexto de trabajo

## Qué es esto

Entelequia es una **herramienta de medición**, no el proyecto general.

Objetivo acotado: evaluar si existe **coherencia relacional independiente del
modelo** — es decir, si el patrón de una interacción sostenida se mantiene
estable cuando se cambia el LLM que corre debajo, manteniendo fijos el corpus
y el interlocutor.

Ese es el alcance de lo que el instrumento mide y de lo que sus resultados
autorizan a afirmar. Afirmaciones más fuertes (identidad funcional
sustrato-independiente, selfhood) exceden el diseño y no deben redactarse
como conclusión del instrumento.

El proyecto general es **Voyager**: modelo biomecánico articular destinado a
fabricación, como metodología sintética para entender el control
sensoriomotor. Entelequia es una pieza lateral, no su centro empírico.

## Estructura real del repo

```
src/
  metrics.py                  # métricas base
  naturalistic_analyzer.py    # análisis de firma cognitiva, 7 dimensiones
  hub/vps_client.py           # cliente único del hub de memoria
scripts/                      # pipelines de análisis y extracción
examples/                     # quickstart + corpus sintéticos
```

Nota: el README describe una estructura (`entelequia_core.py`, `src/metrics/`
como paquete, `src/utils/`, `docker/`) que **no existe**. El bloque de uso del
README no corre. Al tocar el README, alinearlo con el árbol real o crear los
módulos que promete — pero no dejar la brecha.

## Hub de memoria

Arquitectura en estrella: el VPS es el hub, y cada cliente (Claude Code local,
Claude Desktop, sesión web) habla con él. Ningún cliente necesita alcanzar a
los otros, y no hace falta abrir puertos en la red local.

Todo acceso pasa por `src/hub/vps_client.py`. No rearmar requests sueltos en
scripts nuevos: el esquema v4.1 se valida en un solo lugar.

```python
from hub.vps_client import HubMemoria

hub = HubMemoria()                    # lee ENTELEQUIA_VPS_KEY del entorno
hub.guardar(tipoEvento="hito_tecnico", contenido="...",
            resumen="...", relevancia=3)
```

**La API key va en el entorno, nunca en el código ni en un skill.**

```bash
export ENTELEQUIA_VPS_KEY=...
```

## Convenciones

- Español rioplatense.
- Densidad sobre extensión. Sin relleno de cortesía.
- Al proponer cambios metodológicos: distinguir explícitamente lo verificado
  de lo inferido, y no opinar sobre material no leído.

## Configuración local

`.claude/settings.local.json` (no versionado) lleva los permisos y rutas de
cada máquina. Ver `settings.local.json.example` como plantilla.
