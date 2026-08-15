import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_db
from app.schemas import (
    EstadisticaCategoria,
    Estadisticas,
    IntentoCreate,
    IntentoOut,
)

router = APIRouter(tags=["intentos"])


@router.post(
    "/ejercicios/{ejercicio_id}/intentos",
    response_model=IntentoOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_intento(
    ejercicio_id: int,
    datos: IntentoCreate,
    conn: sqlite3.Connection = Depends(get_db),
):
    fila = conn.execute(
        "SELECT id FROM ejercicios WHERE id = ?", (ejercicio_id,)
    ).fetchone()
    if fila is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado"
        )
    cur = conn.execute(
        "INSERT INTO intentos (ejercicio_id, resuelto) VALUES (?, ?)",
        (ejercicio_id, int(datos.resuelto)),
    )
    conn.commit()
    fila = conn.execute(
        "SELECT id, ejercicio_id, resuelto, fecha FROM intentos WHERE id = ?",
        (cur.lastrowid,),
    ).fetchone()
    return dict(fila)


@router.get("/estadisticas", response_model=Estadisticas)
def estadisticas(conn: sqlite3.Connection = Depends(get_db)):
    total_ejercicios = conn.execute(
        "SELECT COUNT(*) AS n FROM ejercicios"
    ).fetchone()["n"]
    total_intentos = conn.execute(
        "SELECT COUNT(*) AS n FROM intentos"
    ).fetchone()["n"]
    exitosos = conn.execute(
        "SELECT COUNT(*) AS n FROM intentos WHERE resuelto = 1"
    ).fetchone()["n"]

    filas = conn.execute(
        """
        SELECT
            c.id AS categoria_id,
            c.nombre,
            COUNT(e.id) AS total_ejercicios,
            COUNT(DISTINCT CASE WHEN i.resuelto = 1 THEN e.id END) AS resueltos
        FROM categorias c
        LEFT JOIN ejercicios e ON e.categoria_id = c.id
        LEFT JOIN intentos i ON i.ejercicio_id = e.id
        GROUP BY c.id
        ORDER BY c.nombre
        """
    ).fetchall()

    por_categoria = []
    for fila in filas:
        total = fila["total_ejercicios"]
        resueltos = fila["resueltos"] or 0
        por_categoria.append(
            EstadisticaCategoria(
                categoria_id=fila["categoria_id"],
                nombre=fila["nombre"],
                total_ejercicios=total,
                resueltos=resueltos,
                porcentaje=round(resueltos * 100 / total, 1) if total else 0.0,
            )
        )
    return Estadisticas(
        total_ejercicios=total_ejercicios,
        total_intentos=total_intentos,
        intentos_exitosos=exitosos,
        por_categoria=por_categoria,
    )