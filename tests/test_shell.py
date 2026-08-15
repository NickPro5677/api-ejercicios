import io
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from shell import ApiShell


@pytest.fixture()
def shell(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "shell-test.db")
    database.init_db()
    return ApiShell(client=TestClient(app))


def _ejecutar(shell, comando):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        shell.onecmd(comando)
    return buffer.getvalue()


def test_lista_muestra_resumen(shell):
    salida = _ejecutar(shell, "lista dificultad facil")
    assert "5 de 5 ejercicios" in salida
    assert "FizzBuzz" in salida


def test_lista_con_busqueda(shell):
    salida = _ejecutar(shell, "lista q Fizz")
    assert "1 de 1 ejercicios" in salida


def test_ver_muestra_solucion(shell):
    salida = _ejecutar(shell, "ver 1")
    assert "FizzBuzz" in salida
    assert "for i in range(1, 101)" in salida


def test_ver_inexistente_muestra_error(shell):
    salida = _ejecutar(shell, "ver 999")
    assert "Error" in salida


def test_pista(shell):
    salida = _ejecutar(shell, "pista 1")
    assert "operador %" in salida


def test_solucion(shell):
    salida = _ejecutar(shell, "solucion 1")
    assert "FizzBuzz" in salida


def test_cat_lista_categorias(shell):
    salida = _ejecutar(shell, "cat")
    assert "Arreglos" in salida
    assert "Lógica" in salida


def test_aleatorio_elige_reto(shell):
    salida = _ejecutar(shell, "aleatorio facil")
    assert "RETO #" in salida


def test_intento_si(shell):
    salida = _ejecutar(shell, "intento 1 si")
    assert "RESUELTO" in salida


def test_stats_refleja_progreso(shell):
    _ejecutar(shell, "intento 1 si")
    _ejecutar(shell, "intento 2 no")
    salida = _ejecutar(shell, "stats")
    assert "Progreso: 1/10" in salida
    assert "Intentos totales: 2" in salida


def test_crear_interactivo(shell):
    entradas = [
        "Sumar lista",
        "Suma todos los elementos.",
        "",
        "facil",
        "1",
        "Usa sum()",
        "def suma(ns):\n    return sum(ns)",
        "",
        "[1, 2]",
        "3",
    ]
    with patch("builtins.input", side_effect=entradas):
        salida = _ejecutar(shell, "crear")
    assert "Ejercicio creado: #11 Sumar lista" in salida
    assert "Sumar lista" in _ejecutar(shell, "ver 11")


def test_borrar(shell):
    salida = _ejecutar(shell, "borrar 1")
    assert "eliminado" in salida
    assert "Error" in _ejecutar(shell, "ver 1")


def test_borrar_inexistente(shell):
    salida = _ejecutar(shell, "borrar 999")
    assert "Error" in salida


def test_exit_termina(shell):
    assert shell.onecmd("exit") is True