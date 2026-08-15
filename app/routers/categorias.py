import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_db
from app.schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
)


@router.get("", response_model=list[CategoriaOut])
def listar_categorias(conn: sqlite3.Connection = Depends(get_db)):
    filas = conn.execute("SELECT * FROM categorias ORDER BY nombre").fetchall()
    return [dict(fila) for fila in filas]


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    datos: CategoriaCreate, conn: sqlite3.Connection = Depends(get_db)
):
    try:
        cur = conn.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
            (datos.nombre, datos.descripcion),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría llamada '{datos.nombre}'",
        )
    fila = conn.execute(
        "SELECT * FROM categorias WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return dict(fila)


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(
    categoria_id: int, conn: sqlite3.Connection = Depends(get_db)
):
    fila = conn.execute(
        "SELECT * FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    return dict(fila)


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaUpdate,
    conn: sqlite3.Connection = Depends(get_db),
):
    fila = conn.execute(
        "SELECT * FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    nombre = datos.nombre if datos.nombre is not None else fila["nombre"]
    descripcion = (
        datos.descripcion if datos.descripcion is not None else fila["descripcion"]
    )
    try:
        conn.execute(
            "UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?",
            (nombre, descripcion, categoria_id),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría llamada '{nombre}'",
        )
    fila = conn.execute(
        "SELECT * FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    return dict(fila)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: int, conn: sqlite3.Connection = Depends(get_db)
):
    fila = conn.execute(
        "SELECT id FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    if fila is None:
        raise NOT_FOUND
    ejercicios = conn.execute(
        "SELECT COUNT(*) AS n FROM ejercicios WHERE categoria_id = ?",
        (categoria_id,),
    ).fetchone()["n"]
    if ejercicios:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar: la categoría tiene {ejercicios} ejercicio(s)",
        )
    conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
    conn.commit()