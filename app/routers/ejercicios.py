import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.deps import get_db, validar_categoria, validar_dificultad
from app.schemas import (
    EjercicioCreate,
    EjercicioOut,
    EjercicioUpdate,
    ListaEjercicios,
)

router = APIRouter(prefix="/ejercicios", tags=["ejercicios"])

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado"
)

CAMPOS_SELECT = (
    "id, titulo, enunciado, dificultad, categoria_id, pista, solucion, "
    "ejemplo_entrada, ejemplo_salida, created_at"
)


def _build_filtros(
    categoria_id: int | None = None,
    dificultad: str | None = None,
    q: str | None = None,
):
    condiciones = []
    parametros = []
    if categoria_id is not None:
        condiciones.append("categoria_id = ?")
        parametros.append(categoria_id)
    if dificultad is not None:
        condiciones.append("dificultad = ?")
        parametros.append(dificultad)
    if q:
        condiciones.append("(titulo LIKE ? OR enunciado LIKE ?)")
        parametros.extend((f"%{q}%", f"%{q}%"))
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where, parametros


@router.get("", response_model=ListaEjercicios)
def listar_ejercicios(
    categoria_id: int | None = Query(default=None),
    dificultad: str | None = Query(default=None, pattern="^(facil|media|dificil)$"),
    q: str | None = Query(default=None, min_length=1),
    limite: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    conn: sqlite3.Connection = Depends(get_db),
):
    where, parametros = _build_filtros(categoria_id, dificultad, q)
    total = conn.execute(
        f"SELECT COUNT(*) AS n FROM ejercicios {where}", parametros
    ).fetchone()["n"]
    filas = conn.execute(
        f"SELECT id, titulo, dificultad, categoria_id, created_at "
        f"FROM ejercicios {where} ORDER BY id LIMIT ? OFFSET ?",
        parametros + [limite, offset],
    ).fetchall()
    return {"total": total, "items": [dict(fila) for fila in filas]}


@router.post("", response_model=EjercicioOut, status_code=status.HTTP_201_CREATED)
def crear_ejercicio(
    datos: EjercicioCreate, conn: sqlite3.Connection = Depends(get_db)
):
    validar_dificultad(datos.dificultad)
    validar_categoria(conn, datos.categoria_id)
    cur = conn.execute(
        "INSERT INTO ejercicios (titulo, enunciado, dificultad, categoria_id, "
        "pista, solucion, ejemplo_entrada, ejemplo_salida) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            datos.titulo,
            datos.enunciado,
            datos.dificultad,
            datos.categoria_id,
            datos.pista,
            datos.solucion,
            datos.ejemplo_entrada,
            datos.ejemplo_salida,
        ),
    )
    conn.commit()
    fila = conn.execute(
        f"SELECT {CAMPOS_SELECT} FROM ejercicios WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return dict(fila)


@router.get("/{ejercicio_id}", response_model=EjercicioOut)
def obtener_ejercicio(
    ejercicio_id: int, conn: sqlite3.Connection = Depends(get_db)
):
    fila = conn.execute(
        f"SELECT {CAMPOS_SELECT} FROM ejercicios WHERE id = ?", (ejercicio_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    return dict(fila)


@router.put("/{ejercicio_id}", response_model=EjercicioOut)
def actualizar_ejercicio(
    ejercicio_id: int,
    datos: EjercicioUpdate,
    conn: sqlite3.Connection = Depends(get_db),
):
    fila = conn.execute(
        f"SELECT {CAMPOS_SELECT} FROM ejercicios WHERE id = ?", (ejercicio_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    if datos.dificultad is not None:
        validar_dificultad(datos.dificultad)
    if datos.categoria_id is not None:
        validar_categoria(conn, datos.categoria_id)
    nuevos = {
        "titulo": datos.titulo if datos.titulo is not None else fila["titulo"],
        "enunciado": (
            datos.enunciado if datos.enunciado is not None else fila["enunciado"]
        ),
        "dificultad": (
            datos.dificultad if datos.dificultad is not None else fila["dificultad"]
        ),
        "categoria_id": (
            datos.categoria_id
            if datos.categoria_id is not None
            else fila["categoria_id"]
        ),
        "pista": datos.pista if datos.pista is not None else fila["pista"],
        "solucion": datos.solucion if datos.solucion is not None else fila["solucion"],
        "ejemplo_entrada": (
            datos.ejemplo_entrada
            if datos.ejemplo_entrada is not None
            else fila["ejemplo_entrada"]
        ),
        "ejemplo_salida": (
            datos.ejemplo_salida
            if datos.ejemplo_salida is not None
            else fila["ejemplo_salida"]
        ),
    }
    conn.execute(
        "UPDATE ejercicios SET titulo = ?, enunciado = ?, dificultad = ?, "
        "categoria_id = ?, pista = ?, solucion = ?, ejemplo_entrada = ?, "
        "ejemplo_salida = ? WHERE id = ?",
        (
            nuevos["titulo"],
            nuevos["enunciado"],
            nuevos["dificultad"],
            nuevos["categoria_id"],
            nuevos["pista"],
            nuevos["solucion"],
            nuevos["ejemplo_entrada"],
            nuevos["ejemplo_salida"],
            ejercicio_id,
        ),
    )
    conn.commit()
    fila = conn.execute(
        f"SELECT {CAMPOS_SELECT} FROM ejercicios WHERE id = ?", (ejercicio_id,)
    ).fetchone()
    return dict(fila)


@router.delete("/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ejercicio(
    ejercicio_id: int, conn: sqlite3.Connection = Depends(get_db)
):
    fila = conn.execute(
        "SELECT id FROM ejercicios WHERE id = ?", (ejercicio_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    conn.execute("DELETE FROM ejercicios WHERE id = ?", (ejercicio_id,))
    conn.commit()