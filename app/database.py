import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ejercicios.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS ejercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    enunciado TEXT NOT NULL,
    dificultad TEXT NOT NULL DEFAULT 'facil'
        CHECK (dificultad IN ('facil', 'media', 'dificil')),
    categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE RESTRICT,
    pista TEXT NOT NULL DEFAULT '',
    solucion TEXT NOT NULL,
    ejemplo_entrada TEXT NOT NULL DEFAULT '',
    ejemplo_salida TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS intentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ejercicio_id INTEGER NOT NULL REFERENCES ejercicios(id) ON DELETE CASCADE,
    resuelto INTEGER NOT NULL CHECK (resuelto IN (0, 1)),
    fecha TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

SEED_CATEGORIAS = [
    ("Arreglos", "Manipulación de listas y arrays"),
    ("Strings", "Procesamiento de texto y cadenas"),
    ("Recursión", "Funciones que se llaman a sí mismas"),
    ("Lógica", "Problemas de razonamiento y matemáticas"),
]

SEED_EJERCICIOS = [
    (
        "FizzBuzz",
        "Imprime los números del 1 al 100; si el número es múltiplo de 3 imprime 'Fizz', "
        "si es múltiplo de 5 imprime 'Buzz' y si es de ambos, 'FizzBuzz'.",
        "facil",
        "Lógica",
        "Usa el operador % para comprobar divisibilidad.",
        "for i in range(1, 101):\n    if i % 15 == 0: print('FizzBuzz')\n    elif i % 3 == 0: print('Fizz')\n    elif i % 5 == 0: print('Buzz')\n    else: print(i)",
        "n = 15",
        "FizzBuzz",
    ),
    (
        "Invertir palabra",
        "Dada una palabra, devuélvela invertida sin usar slicing con paso negativo.",
        "facil",
        "Strings",
        "Recorre los caracteres desde el final con range(len(p)-1, -1, -1).",
        "def invertir(p):\n    res = ''\n    for i in range(len(p) - 1, -1, -1):\n        res += p[i]\n    return res",
        "invertir('hola')",
        "'aloh'",
    ),
    (
        "Suma de pares",
        "Dada una lista de enteros, devuelve la suma de los números pares.",
        "facil",
        "Arreglos",
        "Filtra con el operador % y usa sum().",
        "def suma_pares(ns):\n    return sum(n for n in ns if n % 2 == 0)",
        "suma_pares([1, 2, 3, 4, 5, 6])",
        "12",
    ),
    (
        "Palíndromo",
        "Determina si una palabra se lee igual al derecho y al revés.",
        "media",
        "Strings",
        "Compara la palabra con su inversa.",
        "def es_palindromo(p):\n    return p == p[::-1]",
        "es_palindromo('reconocer')",
        "True",
    ),
    (
        "Factorial",
        "Calcula el factorial de n recursivamente.",
        "media",
        "Recursión",
        "Caso base: factorial(0) = 1; caso recursivo: n * factorial(n-1).",
        "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)",
        "factorial(5)",
        "120",
    ),
    (
        "Fibonacci",
        "Devuelve el n-ésimo número de Fibonacci. Fibonacci(0)=0, Fibonacci(1)=1.",
        "media",
        "Recursión",
        "Suma de los dos anteriores; cuidado con la doble recursión ineficiente.",
        "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)",
        "fib(10)",
        "55",
    ),
    (
        "Números primos",
        "Devuelve True si n es primo, recorriendo divisores hasta la raíz cuadrada.",
        "media",
        "Lógica",
        "Basta probar divisores <= sqrt(n) usando math.isqrt.",
        "from math import isqrt\n\ndef es_primo(n):\n    if n < 2:\n        return False\n    for d in range(2, isqrt(n) + 1):\n        if n % d == 0:\n            return False\n    return True",
        "es_primo(97)",
        "True",
    ),
    (
        "Máximo de la lista",
        "Encuentra el máximo de una lista sin usar la función max.",
        "facil",
        "Arreglos",
        "Inicializa una variable con el primer elemento y compara el resto.",
        "def maximo(ns):\n    m = ns[0]\n    for n in ns[1:]:\n        if n > m:\n            m = n\n    return m",
        "maximo([3, 8, 2, 10, 4])",
        "10",
    ),
    (
        "Contar vocales",
        "Cuenta cuántas vocales (a, e, i, o, u) tiene una cadena.",
        "facil",
        "Strings",
        "Itera y comprueba pertenencia al conjunto de vocales.",
        "def contar_vocales(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
        "contar_vocales('ingenieria')",
        "6",
    ),
    (
        "Potencia recursiva",
        "Calcula a^b de forma recursiva.",
        "dificil",
        "Recursión",
        "a^b = a * a^(b-1), con caso base b == 0.",
        "def potencia(a, b):\n    if b == 0:\n        return 1\n    return a * potencia(a, b - 1)",
        "potencia(2, 10)",
        "1024",
    ),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]
    if count:
        return
    for nombre, descripcion in SEED_CATEGORIAS:
        conn.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion),
        )
    for titulo, enunciado, dificultad, categoria, pista, solucion, entrada, salida in SEED_EJERCICIOS:
        cat_id = conn.execute(
            "SELECT id FROM categorias WHERE nombre = ?", (categoria,)
        ).fetchone()["id"]
        conn.execute(
            "INSERT INTO ejercicios (titulo, enunciado, dificultad, categoria_id, pista, "
            "solucion, ejemplo_entrada, ejemplo_salida) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (titulo, enunciado, dificultad, cat_id, pista, solucion, entrada, salida),
        )


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        seed_if_empty(conn)
        conn.commit()
    finally:
        conn.close()