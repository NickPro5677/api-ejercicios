def test_listar_categorias_seed(client):
    respuesta = client.get("/categorias")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 4
    nombres = {categoria["nombre"] for categoria in datos}
    assert nombres == {"Arreglos", "Strings", "Recursión", "Lógica"}


def test_crear_categoria(client):
    respuesta = client.post(
        "/categorias", json={"nombre": "Grafos", "descripcion": "Teoría de grafos"}
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Grafos"


def test_crear_categoria_duplicada(client):
    respuesta = client.post("/categorias", json={"nombre": "Arreglos"})
    assert respuesta.status_code == 409


def test_crear_categoria_nombre_vacio(client):
    respuesta = client.post("/categorias", json={"nombre": ""})
    assert respuesta.status_code == 422


def test_obtener_categoria_inexistente(client):
    assert client.get("/categorias/999").status_code == 404


def test_actualizar_categoria(client):
    respuesta = client.put("/categorias/1", json={"descripcion": "Nueva descripción"})
    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] == "Nueva descripción"


def test_eliminar_categoria_con_ejercicios(client):
    assert client.delete("/categorias/1").status_code == 409


def test_eliminar_categoria_sin_ejercicios(client):
    client.post("/categorias", json={"nombre": "Vacía"})
    assert client.delete("/categorias/5").status_code == 204
    assert client.get("/categorias/5").status_code == 404