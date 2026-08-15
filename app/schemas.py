from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

DIFFICULTADES = ("facil", "media", "dificil")


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = None


class CategoriaOut(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EjercicioBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    enunciado: str = Field(min_length=1)
    dificultad: str = Field(default="facil")
    categoria_id: int
    pista: str = ""
    solucion: str = Field(min_length=1)
    ejemplo_entrada: str = ""
    ejemplo_salida: str = ""


class EjercicioCreate(EjercicioBase):
    pass


class EjercicioUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    enunciado: str | None = Field(default=None, min_length=1)
    dificultad: str | None = None
    categoria_id: int | None = None
    pista: str | None = None
    solucion: str | None = Field(default=None, min_length=1)
    ejemplo_entrada: str | None = None
    ejemplo_salida: str | None = None


class EjercicioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    enunciado: str
    dificultad: str
    categoria_id: int
    pista: str
    solucion: str
    ejemplo_entrada: str
    ejemplo_salida: str
    created_at: datetime


class EjercicioResumen(BaseModel):
    id: int
    titulo: str
    dificultad: str
    categoria_id: int
    created_at: datetime


class ListaEjercicios(BaseModel):
    total: int
    items: list[EjercicioResumen]


class IntentoCreate(BaseModel):
    resuelto: bool


class IntentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ejercicio_id: int
    resuelto: bool
    fecha: datetime


class EstadisticaCategoria(BaseModel):
    categoria_id: int
    nombre: str
    total_ejercicios: int
    resueltos: int
    porcentaje: float


class Estadisticas(BaseModel):
    total_ejercicios: int
    total_intentos: int
    intentos_exitosos: int
    por_categoria: list[EstadisticaCategoria]