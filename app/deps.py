import sqlite3
from typing import Iterator

from fastapi import HTTPException, status

from app.database import get_connection


def get_db() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def validar_dificultad(dificultad: str) -> None:
    from app.schemas import DIFFICULTADES

    if dificultad not in DIFFICULTADES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Dificultad inválida: {dificultad}. Válidas: {', '.join(DIFFICULTADES)}",
        )


def validar_categoria(conn: sqlite3.Connection, categoria_id: int) -> None:
    fila = conn.execute(
        "SELECT id FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    if fila is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría {categoria_id} no existe",
        )