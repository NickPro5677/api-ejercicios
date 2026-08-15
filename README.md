# API Ejercicios

API REST con un banco de ejercicios de programación (Python) para repasar antes
de exámenes: enunciado, pista, solución, dificultad, categoría e historial de
intentos con estadísticas de progreso.

Stack: FastAPI + SQLite (stdlib) + Pydantic v2. Pensada para correr localmente
en Termux (ligera en RAM y CPU).

## Puesta en marcha

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

La primera vez se crea `data/ejercicios.db` automáticamente con 4 categorías y
10 ejercicios de ejemplo (seed).

Documentación interactiva: http://127.0.0.1:8000/docs (Swagger).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/categorias` | Lista de categorías |
| POST | `/categorias` | Crear categoría |
| GET/PUT/DELETE | `/categorias/{id}` | CRUD de categoría |
| GET | `/ejercicios?categoria_id=&dificultad=&q=&limite=&offset=` | Lista con filtros y paginación |
| POST | `/ejercicios` | Crear ejercicio |
| GET/PUT/DELETE | `/ejercicios/{id}` | CRUD de ejercicio |
| POST | `/ejercicios/{id}/intentos` | Registrar intento `{"resuelto": true}` |
| GET | `/estadisticas` | Progreso global y por categoría |

## Ejemplos con curl

```sh
# Listar ejercicios fáciles
curl 'http://127.0.0.1:8000/ejercicios?dificultad=facil'

# Buscar por título
curl 'http://127.0.0.1:8000/ejercicios?q=Fizz'

# Ver un ejercicio completo (con solución)
curl http://127.0.0.1:8000/ejercicios/1

# Crear un ejercicio
curl -X POST http://127.0.0.1:8000/ejercicios \
  -H 'Content-Type: application/json' \
  -d '{"titulo": "Ordenar lista",
       "enunciado": "Ordena una lista de números.",
       "dificultad": "media",
       "categoria_id": 1,
       "solucion": "sorted(ns)",
       "ejemplo_entrada": "[3, 1, 2]",
       "ejemplo_salida": "[1, 2, 3]"}'

# Registrar un intento
curl -X POST http://127.0.0.1:8000/ejercicios/1/intentos \
  -H 'Content-Type: application/json' -d '{"resuelto": true}'

# Ver progreso
curl http://127.0.0.1:8000/estadisticas
```

## Shell de práctica

REPL interactivo (en español) para experimentar con la API y repasar ejercicios
sin escribir curl. Requiere la API corriendo en otra terminal:

```sh
.venv/bin/uvicorn app.main:app --reload
# en otra terminal:
.venv/bin/python shell.py
```

Comandos:

| Comando | Qué hace |
|---|---|
| `lista dificultad facil` | Lista con filtros: `dificultad`, `categoria N`, `q TEXTO`, `limite N` |
| `cat` | Lista categorías |
| `ver N` | Ejercicio completo (enunciado, pista, solución) |
| `pista N` / `solucion N` | Solo pista o solo solución |
| `aleatorio [dificultad]` | Reto al azar para practicar |
| `intento N si\|no` | Registra el resultado de tu intento |
| `stats` | Progreso global y por categoría con barras |
| `crear` | Guía paso a paso para añadir un ejercicio |
| `cat_nueva`, `cat_borrar`, `borrar N` | Alta/baja de categorías y ejercicios |
| `help`, `exit` | Ayuda y salida |

## Tests

```sh
.venv/bin/pytest -q
```

Los tests usan una base de datos temporal (no tocan `data/ejercicios.db`).

## Estructura

```
app/
├── main.py          # app FastAPI, lifespan (init_db) y raíz
├── database.py      # esquema SQL, conexión y seed
├── deps.py          # get_db y validaciones compartidas
├── schemas.py       # modelos Pydantic
└── routers/         # categorias.py, ejercicios.py, intentos.py
tests/               # conftest + tests por recurso
data/                # ejercicios.db (generado, gitignored)
```