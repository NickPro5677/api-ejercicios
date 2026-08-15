def test_registrar_intento_resuelto(client):
    respuesta = client.post("/ejercicios/1/intentos", json={"resuelto": True})
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["ejercicio_id"] == 1
    assert cuerpo["resuelto"] is True


def test_registrar_intento_ejercicio_inexistente(client):
    respuesta = client.post("/ejercicios/999/intentos", json={"resuelto": True})
    assert respuesta.status_code == 404


def test_estadisticas_iniciales(client):
    respuesta = client.get("/estadisticas")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["total_ejercicios"] == 10
    assert datos["total_intentos"] == 0
    assert datos["intentos_exitosos"] == 0


def test_estadisticas_despues_de_intentos(client):
    client.post("/ejercicios/1/intentos", json={"resuelto": True})
    client.post("/ejercicios/2/intentos", json={"resuelto": False})
    datos = client.get("/estadisticas").json()
    assert datos["total_intentos"] == 2
    assert datos["intentos_exitosos"] == 1
    logica = next(cat for cat in datos["por_categoria"] if cat["categoria_id"] == 4)
    assert logica["resueltos"] == 1
    assert logica["porcentaje"] == 50.0