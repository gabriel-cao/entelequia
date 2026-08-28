#!/usr/bin/env python3
"""Inventario de proyectos y archivos. Sólo lectura: no mueve ni borra nada.

Recorre las raíces indicadas, cataloga qué hay y dónde, y emite un JSON
comparable entre máquinas. El objetivo es poder ver, antes de reorganizar,
qué está duplicado, qué está sólo en una máquina, y dónde pesa el volumen.

    # en cada máquina
    python3 inventario.py --raiz /media/gabriel/hdd1tb \
                          --raiz /media/gabriel/Storage480 \
                          --maquina taurus --salida inv_taurus.json

    # después, con los dos JSON juntos
    python3 inventario.py --comparar inv_taurus.json inv_endurance.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

# Ruido que no aporta al inventario y sí infla el recorrido.
EXCLUIR_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".cache",
    ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints", "site-packages",
    ".Trash-1000", "lost+found", ".thumbnails",
}

CATEGORIAS = {
    "codigo": {".py", ".js", ".ts", ".c", ".cpp", ".h", ".sh", ".rs", ".go", ".ipynb"},
    "documento": {".md", ".txt", ".pdf", ".docx", ".odt", ".tex", ".rtf"},
    "datos": {".json", ".csv", ".tsv", ".xlsx", ".db", ".sqlite", ".parquet", ".npy"},
    "imagen": {".png", ".jpg", ".jpeg", ".svg", ".webp", ".tiff", ".gif"},
    "video": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "audio": {".wav", ".mp3", ".flac", ".ogg", ".m4a"},
    "modelo3d": {".stl", ".obj", ".blend", ".fbx", ".step", ".stp", ".osim"},
    "pesos": {".gguf", ".safetensors", ".bin", ".pt", ".pth", ".onnx"},
}
EXT_A_CATEGORIA = {ext: cat for cat, exts in CATEGORIAS.items() for ext in exts}

TOPE_HASH_COMPLETO = 8 * 1024 * 1024  # 8 MB


def huella(ruta: str, tam: int) -> str | None:
    """Hash del archivo. Para archivos grandes, muestrea extremos + tamaño.

    Un archivo grande idéntico en las dos máquinas coincide en extremos y
    tamaño; leerlo entero para confirmarlo costaría minutos por gigabyte.
    """
    try:
        h = hashlib.blake2b(digest_size=16)
        with open(ruta, "rb") as f:
            if tam <= TOPE_HASH_COMPLETO:
                for bloque in iter(lambda: f.read(1 << 20), b""):
                    h.update(bloque)
            else:
                h.update(f.read(1 << 20))
                f.seek(-(1 << 20), os.SEEK_END)
                h.update(f.read(1 << 20))
                h.update(str(tam).encode())
        return h.hexdigest()
    except OSError:
        return None


def recorrer(raices: list[str], maquina: str) -> dict:
    archivos: list[dict] = []
    errores: list[str] = []

    for raiz in raices:
        if not os.path.isdir(raiz):
            errores.append(f"raíz inexistente o no accesible: {raiz}")
            continue

        for dirpath, dirnames, filenames in os.walk(raiz, onerror=lambda e: errores.append(str(e))):
            dirnames[:] = [d for d in dirnames if d not in EXCLUIR_DIRS and not d.startswith(".Trash")]

            for nombre in filenames:
                ruta = os.path.join(dirpath, nombre)
                try:
                    st = os.lstat(ruta)
                except OSError as e:
                    errores.append(f"{ruta}: {e}")
                    continue
                if not os.path.isfile(ruta) or os.path.islink(ruta):
                    continue

                ext = os.path.splitext(nombre)[1].lower()
                archivos.append({
                    "ruta": ruta,
                    "rel": os.path.relpath(ruta, raiz),
                    "raiz": raiz,
                    "tam": st.st_size,
                    "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                    "ext": ext,
                    "categoria": EXT_A_CATEGORIA.get(ext, "otro"),
                    "hash": huella(ruta, st.st_size),
                })

    return {
        "maquina": maquina,
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "raices": raices,
        "archivos": archivos,
        "errores": errores,
    }


def resumir(inv: dict) -> None:
    archivos = inv["archivos"]
    total = sum(a["tam"] for a in archivos)
    print(f"\n=== {inv['maquina']} — {len(archivos)} archivos, {total / 1e9:.2f} GB ===")

    por_cat: dict[str, list[int]] = defaultdict(list)
    for a in archivos:
        por_cat[a["categoria"]].append(a["tam"])
    print("\nPor categoría:")
    for cat, tams in sorted(por_cat.items(), key=lambda kv: -sum(kv[1])):
        print(f"  {cat:<12} {len(tams):>6} arch  {sum(tams) / 1e9:>8.2f} GB")

    # Proyecto = primer nivel bajo cada raíz.
    por_proy: dict[str, list[int]] = defaultdict(list)
    for a in archivos:
        por_proy[a["rel"].split(os.sep)[0]].append(a["tam"])
    print("\nTop 20 carpetas de primer nivel:")
    for proy, tams in sorted(por_proy.items(), key=lambda kv: -sum(kv[1]))[:20]:
        print(f"  {proy[:45]:<45} {len(tams):>6} arch  {sum(tams) / 1e9:>8.2f} GB")

    # Duplicados internos.
    por_hash: dict[str, list[dict]] = defaultdict(list)
    for a in archivos:
        if a["hash"]:
            por_hash[a["hash"]].append(a)
    dups = {h: v for h, v in por_hash.items() if len(v) > 1}
    desperdicio = sum(v[0]["tam"] * (len(v) - 1) for v in dups.values())
    print(f"\nDuplicados dentro de esta máquina: {len(dups)} grupos, {desperdicio / 1e9:.2f} GB recuperables")
    for v in sorted(dups.values(), key=lambda v: -v[0]["tam"] * (len(v) - 1))[:10]:
        print(f"  {v[0]['tam'] / 1e6:>8.1f} MB ×{len(v)}  {v[0]['rel'][:60]}")

    if inv["errores"]:
        print(f"\n{len(inv['errores'])} errores de acceso (primeros 5):")
        for e in inv["errores"][:5]:
            print(f"  {e}")


def comparar(ruta_a: str, ruta_b: str) -> None:
    with open(ruta_a) as f:
        a = json.load(f)
    with open(ruta_b) as f:
        b = json.load(f)

    ha = {x["hash"]: x for x in a["archivos"] if x["hash"]}
    hb = {x["hash"]: x for x in b["archivos"] if x["hash"]}
    comunes = ha.keys() & hb.keys()
    solo_a, solo_b = ha.keys() - hb.keys(), hb.keys() - ha.keys()

    print(f"\n=== {a['maquina']} vs {b['maquina']} ===")
    print(f"  en ambas:        {len(comunes):>7}  ({sum(ha[h]['tam'] for h in comunes) / 1e9:.2f} GB duplicados entre máquinas)")
    print(f"  sólo {a['maquina']:<12} {len(solo_a):>7}  ({sum(ha[h]['tam'] for h in solo_a) / 1e9:.2f} GB)")
    print(f"  sólo {b['maquina']:<12} {len(solo_b):>7}  ({sum(hb[h]['tam'] for h in solo_b) / 1e9:.2f} GB)")

    print(f"\nLo más pesado que existe SÓLO en {a['maquina']} (sin respaldo en la otra):")
    for h in sorted(solo_a, key=lambda h: -ha[h]["tam"])[:15]:
        print(f"  {ha[h]['tam'] / 1e6:>8.1f} MB  {ha[h]['ruta'][:70]}")
    print(f"\nLo más pesado que existe SÓLO en {b['maquina']}:")
    for h in sorted(solo_b, key=lambda h: -hb[h]["tam"])[:15]:
        print(f"  {hb[h]['tam'] / 1e6:>8.1f} MB  {hb[h]['ruta'][:70]}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raiz", action="append", default=[], help="ruta a inventariar (repetible)")
    p.add_argument("--maquina", default=os.uname().nodename)
    p.add_argument("--salida", help="archivo JSON de salida")
    p.add_argument("--comparar", nargs=2, metavar=("INV_A", "INV_B"))
    args = p.parse_args()

    if args.comparar:
        comparar(*args.comparar)
        return 0

    if not args.raiz:
        p.error("indicá al menos una --raiz, o usá --comparar")

    inv = recorrer(args.raiz, args.maquina)
    resumir(inv)

    if args.salida:
        with open(args.salida, "w") as f:
            json.dump(inv, f, ensure_ascii=False)
        print(f"\nInventario escrito en {args.salida} "
              f"({os.path.getsize(args.salida) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
