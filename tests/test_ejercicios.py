def test_listar_ejercicios(client):
    respuesta = client.get("/ejercicios")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["total"] == 10
    assert all("solucion" not in item for item in datos["items"])


def test_filtro_por_dificultad(client):
    respuesta = client.get("/ejercicios", params={"dificultad": "facil"})
    assert respuesta.status_code == 200
    assert respuesta.json()["total"] == 5


def test_filtro_por_categoria(client):
    respuesta = client.get("/ejercicios", params={"categoria_id": 1})
    assert respuesta.status_code == 200
    assert all(item["categoria_id"] == 1 for item in respuesta.json()["items"])


def test_busqueda_por_titulo(client):
    respuesta = client.get("/ejercicios", params={"q": "Fizz"})
    assert respuesta.status_code == 200
    assert respuesta.json()["total"] == 1
    assert respuesta.json()["items"][0]["titulo"] == "FizzBuzz"


def test_paginacion(client):
    respuesta = client.get("/ejercicios", params={"limite": 3, "offset": 0})
    assert respuesta.status_code == 200
    assert len(respuesta.json()["items"]) == 3
    assert respuesta.json()["total"] == 10


def test_dificultad_invalida_en_filtro(client):
    assert client.get("/ejercicios", params={"dificultad": "imposible"}).status_code == 422


def test_crear_ejercicio(client):
    datos = {
        "titulo": "Ordenar lista",
        "enunciado": "Ordena una lista de números.",
        "dificultad": "media",
        "categoria_id": 1,
        "solucion": "sorted(ns)",
        "ejemplo_entrada": "[3, 1, 2]",
        "ejemplo_salida": "[1, 2, 3]",
    }
    respuesta = client.post("/ejercicios", json=datos)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["titulo"] == "Ordenar lista"
    assert cuerpo["id"] == 11


def test_crear_ejercicio_categoria_inexistente(client):
    datos = {
        "titulo": "Sin categoría",
        "enunciado": "No debe crearse.",
        "categoria_id": 999,
        "solucion": "pass",
    }
    assert client.post("/ejercicios", json=datos).status_code == 404


def test_crear_ejercicio_dificultad_invalida(client):
    datos = {
        "titulo": "Mal",
        "enunciado": "No debe crearse.",
        "dificultad": "extremo",
        "categoria_id": 1,
        "solucion": "pass",
    }
    assert client.post("/ejercicios", json=datos).status_code == 422


def test_crear_ejercicio_sin_solucion(client):
    datos = {
        "titulo": "Sin solución",
        "enunciado": "No debe crearse.",
        "categoria_id": 1,
    }
    assert client.post("/ejercicios", json=datos).status_code == 422


def test_obtener_ejercicio(client):
    respuesta = client.get("/ejercicios/1")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["titulo"] == "FizzBuzz"
    assert "solucion" in cuerpo


def test_obtener_ejercicio_inexistente(client):
    assert client.get("/ejercicios/999").status_code == 404


def test_actualizar_ejercicio_parcial(client):
    respuesta = client.put("/ejercicios/1", json={"pista": "Pista nueva"})
    assert respuesta.status_code == 200
    assert respuesta.json()["pista"] == "Pista nueva"
    assert respuesta.json()["titulo"] == "FizzBuzz"


def test_eliminar_ejercicio(client):
    assert client.delete("/ejercicios/1").status_code == 204
    assert client.get("/ejercicios/1").status_code == 404
    assert client.get("/ejercicios").json()["total"] == 9