#!/usr/bin/env python3
"""Migración ETL desde Hugo Markdown (P1.1) hacia Chyrp Lite SQLite (P1.2)."""
import argparse
import json
import pathlib
import sqlite3
import sys
from index import parse_front_matter

FECHA_NULA = "1000-01-01 00:00:00"

def extraer(carpeta_posts: pathlib.Path) -> list[dict]:
    entradas = []
    for ruta in sorted(carpeta_posts.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        meta, cuerpo = parse_front_matter(texto)
        entradas.append({
            "slug": ruta.stem,
            "title": meta.get("title", ruta.stem),
            "date": str(meta.get("date", "2026-01-01")),
            "draft": bool(meta.get("draft", False)),
            "tags": list(meta.get("tags", [])),
            "author": meta.get("author"),
            "body": cuerpo.strip(),
        })
    return entradas

def normalizar_fecha(fecha: str) -> str:
    fecha = fecha.strip()
    if len(fecha) == 10:
        return f"{fecha} 00:00:00"
    return fecha.replace("T", " ")[:19]

def etiquetas_json(tags: list) -> str:
    return json.dumps([str(t) for t in tags], ensure_ascii=False)

def transformar(entrada: dict, user_id: int = 1) -> tuple[dict, list[tuple[str, str]]]:
    slug = entrada["slug"]
    status = "draft" if entrada.get("draft", False) else "public"
    fila_post = {
        "feather": "text",
        "clean": slug,
        "url": slug,
        "pinned": 0,
        "status": status,
        "user_id": user_id,
        "created_at": normalizar_fecha(entrada["date"]),
        "updated_at": FECHA_NULA,
    }
    atributos = [
        ("title", entrada["title"]),
        ("body", entrada["body"]),
        ("tags", etiquetas_json(entrada.get("tags", []))),
    ]
    return fila_post, atributos

def ya_existe(cur: sqlite3.Cursor, clean: str) -> bool:
    cur.execute("SELECT 1 FROM posts WHERE clean = ?", (clean,))
    return cur.fetchone() is not None

def insertar(cur: sqlite3.Cursor, fila_post: dict, atributos: list[tuple[str, str]]) -> int:
    cur.execute(
        """INSERT INTO posts (feather, clean, url, pinned, status, user_id, created_at, updated_at)
           VALUES (:feather, :clean, :url, :pinned, :status, :user_id, :created_at, :updated_at)""",
        fila_post,
    )
    post_id = cur.lastrowid
    for name, value in atributos:
        cur.execute(
            "INSERT INTO post_attributes (post_id, name, value) VALUES (?, ?, ?)",
            (post_id, name, value),
        )
    return post_id

def cargar(ruta_db: pathlib.Path, entradas: list[dict], user_id: int = 1, simulacro: bool = False) -> tuple[int, int]:
    if not ruta_db.exists():
        sys.exit(f"migrar.py: no existe {ruta_db}")
    con = sqlite3.connect(ruta_db)
    try:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_attributes'")
        if not cur.fetchone():
            sys.exit(f"migrar.py: {ruta_db} no parece una base de datos de Chyrp Lite")
        nuevas = 0
        omitidas = 0
        with con:
            for e in entradas:
                fila_post, atributos = transformar(e, user_id=user_id)
                if ya_existe(cur, fila_post["clean"]):
                    print(f"omitida   {fila_post['clean']}")
                    omitidas += 1
                elif simulacro:
                    print(f"simulada  {fila_post['clean']}")
                    nuevas += 1
                else:
                    insertar(cur, fila_post, atributos)
                    print(f"creada    {fila_post['clean']}")
                    nuevas += 1
        return nuevas, omitidas
    finally:
        con.close()

def main():
    parser = argparse.ArgumentParser(description="Migra posts de Hugo a Chyrp Lite")
    parser.add_argument("destino", type=pathlib.Path, help="Ruta al fichero .sqlite de Chyrp Lite")
    parser.add_argument("--origen", type=pathlib.Path, default=pathlib.Path("content/posts"))
    parser.add_argument("--autor", type=int, default=1, help="ID del usuario autor en Chyrp Lite")
    parser.add_argument("--simulacro", action="store_true", help="No escribe cambios en la BD")
    args = parser.parse_args()

    entradas = extraer(args.origen)
    nuevas, omitidas = cargar(args.destino, entradas, user_id=args.autor, simulacro=args.simulacro)
    print(f"migrar: {len(entradas)} entradas leídas, {nuevas} nuevas, {omitidas} ya estaban")

if __name__ == "__main__":
    main()
