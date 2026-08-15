import cmd
import random
import shlex
import sys

import httpx

BASE_URL = "http://127.0.0.1:8000"

_VERDE = "\033[32m"
_AMARILLO = "\033[33m"
_ROJO = "\033[31m"
_CYAN = "\033[36m"
_GRIS = "\033[90m"
_NEGRITA = "\033[1m"
_RESET = "\033[0m"

_DIFICULTADES = ("facil", "media", "dificil")

_COLORES = {
    "facil": "\033[32m",
    "media": "\033[33m",
    "dificil": "\033[31m",
}


def _pintar(texto, color):
    if not sys.stdout.isatty():
        return texto
    return f"{color}{texto}{_RESET}"


class ApiShell(cmd.Cmd):
    prompt = _pintar("api> ", _CYAN)

    def __init__(self, client=None, base_url=BASE_URL):
        super().__init__()
        self.client = client or httpx.Client(base_url=base_url, timeout=5)

    def _pedir(self, ruta: str, **params):
        try:
            return self.client.get(ruta, params=params)
        except httpx.ConnectError:
            print(
                _pintar(
                    "No hay servidor activo. Arranca la API con:\n"
                    "  .venv/bin/uvicorn app.main:app --reload",
                    _ROJO,
                )
            )
            return None

    def _detalle_error(self, respuesta):
        try:
            cuerpo = respuesta.json()
            return cuerpo.get("detail", respuesta.status_code)
        except Exception:
            return respuesta.text or respuesta.status_code

    def _mostrar_ejercicio(self, ejercicio, detalle=True):
        cat = self.client.get(f"/categorias/{ejercicio['categoria_id']}").json()
        dificultad = _pintar(
            ejercicio["dificultad"], _COLORES[ejercicio["dificultad"]]
        )
        print(f"{_NEGRITA}#{ejercicio['id']} {ejercicio['titulo']}{_RESET}")
        print(f"  categoría: {cat['nombre']}  dificultad: {dificultad}")
        if detalle:
            print(f"  enunciado: {ejercicio['enunciado']}")
            if ejercicio.get("ejemplo_entrada"):
                print(f"  ejemplo entrada: {ejercicio['ejemplo_entrada']}")
            if ejercicio.get("ejemplo_salida"):
                print(f"  ejemplo salida: {ejercicio['ejemplo_salida']}")
            pista = ejercicio.get("pista") or "(sin pista)"
            print(f"  {_pintar(f'pista: {pista}', _AMARILLO)}")

    def do_help(self, linea):
        self.do_help_manual(None)

    def do_help_manual(self, linea):
        help(self)

    def do_lista(self, linea):
        """lista [dificultad] [categoria N] [q TEXTO] [limite N]\nMuestra ejercicios con filtros opcionales."""
        args = shlex.split(linea)
        params = {}
        i = 0
        while i < len(args):
            clave = args[i]
            if clave == "dificultad" and i + 1 < len(args):
                params["dificultad"] = args[i + 1]
                i += 2
            elif clave == "categoria" and i + 1 < len(args):
                params["categoria_id"] = int(args[i + 1])
                i += 2
            elif clave == "q" and i + 1 < len(args):
                params["q"] = args[i + 1]
                i += 2
            elif clave == "limite" and i + 1 < len(args):
                params["limite"] = int(args[i + 1])
                i += 2
            else:
                i += 1
        respuesta = self._pedir("/ejercicios", **params)
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        datos = respuesta.json()
        print(
            f"{len(datos['items'])} de {datos['total']} ejercicios "
            f"(usa 'ver N' para ver detalles y 'pista N' / 'solucion N')"
        )
        for item in datos["items"]:
            self._mostrar_ejercicio(item, detalle=False)

    def do_cat(self, linea):
        """cat\nLista las categorías."""
        respuesta = self._pedir("/categorias")
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        for categoria in respuesta.json():
            print(f"  {categoria['id']}: {categoria['nombre']} — {categoria['descripcion']}")

    def do_cat_nueva(self, linea):
        """cat_nueva NOMBRE [DESCRIPCION]\nCrea una categoría."""
        args = shlex.split(linea)
        if not args:
            print("Uso: cat_nueva NOMBRE [DESCRIPCION]")
            return
        nombre = args[0]
        descripcion = " ".join(args[1:]) if len(args) > 1 else ""
        respuesta = self.client.post(
            "/categorias", json={"nombre": nombre, "descripcion": descripcion}
        )
        if respuesta.status_code == 201:
            print(_pintar(f"Categoría creada: #{respuesta.json()['id']} {nombre}", _VERDE))
        else:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))

    def do_cat_borrar(self, linea):
        """cat_borrar N\nElimina la categoría N (solo si no tiene ejercicios)."""
        args = shlex.split(linea)
        if not args:
            print("Uso: cat_borrar N")
            return
        respuesta = self.client.delete(f"/categorias/{args[0]}")
        if respuesta.status_code == 204:
            print(_pintar(f"Categoría {args[0]} eliminada", _VERDE))
        else:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))

    def do_ver(self, linea):
        """ver N\nMuestra el ejercicio N completo (enunciado, pista, solución)."""
        args = shlex.split(linea)
        if not args:
            print("Uso: ver N")
            return
        respuesta = self._pedir(f"/ejercicios/{args[0]}")
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        self._mostrar_ejercicio(respuesta.json())
        print(f"  {_pintar('solución:', _VERDE)}\n{respuesta.json()['solucion']}")

    def do_pista(self, linea):
        """pista N\nMuestra solo la pista del ejercicio N."""
        args = shlex.split(linea)
        if not args:
            print("Uso: pista N")
            return
        respuesta = self._pedir(f"/ejercicios/{args[0]}")
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        ejercicio = respuesta.json()
        print(_pintar(ejercicio["pista"] or "(sin pista)", _AMARILLO))

    def do_solucion(self, linea):
        """solucion N\nMuestra solo la solución del ejercicio N."""
        args = shlex.split(linea)
        if not args:
            print("Uso: solucion N")
            return
        respuesta = self._pedir(f"/ejercicios/{args[0]}")
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        print(respuesta.json()["solucion"])

    def do_aleatorio(self, linea):
        """aleatorio [dificultad]\nReto al azar para practicar. Ej.: aleatorio facil"""
        args = shlex.split(linea)
        dificultad = args[0] if args else None
        params = {"limite": 100}
        if dificultad:
            if dificultad not in _DIFICULTADES:
                print(f"Dificultades válidas: {', '.join(_DIFICULTADES)}")
                return
            params["dificultad"] = dificultad
        respuesta = self._pedir("/ejercicios", **params)
        if respuesta is None:
            return
        items = respuesta.json()["items"]
        if not items:
            print("No hay ejercicios con esos filtros.")
            return
        elegido = random.choice(items)
        print(_pintar(f"RETO #{elegido['id']}: {elegido['titulo']}", _NEGRITA))
        print("Intenta resolverlo antes de mirar:  pista N / solucion N")
        print(f"Al terminar registra el resultado:  intento {elegido['id']} si|no")

    def do_intento(self, linea):
        """intento N si|no\nRegistra si resolviste el ejercicio N."""
        args = shlex.split(linea)
        if len(args) < 2 or args[1] not in ("si", "no"):
            print("Uso: intento N si|no")
            return
        resuelto = args[1] == "si"
        respuesta = self.client.post(
            f"/ejercicios/{args[0]}/intentos", json={"resuelto": resuelto}
        )
        if respuesta.status_code == 201:
            estado = "RESUELTO" if resuelto else "pendiente"
            print(_pintar(f"Intento registrado: {estado}", _VERDE))
        else:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))

    def do_stats(self, linea):
        """stats\nMuestra tu progreso global y por categoría."""
        respuesta = self._pedir("/estadisticas")
        if respuesta is None:
            return
        if respuesta.status_code != 200:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))
            return
        datos = respuesta.json()
        total = datos["total_ejercicios"] or 1
        barra = _barra(datos["intentos_exitosos"] / total)
        print(f"Progreso: {datos['intentos_exitosos']}/{datos['total_ejercicios']} {barra}")
        print(f"Intentos totales: {datos['total_intentos']}")
        for categoria in datos["por_categoria"]:
            if categoria["total_ejercicios"] == 0:
                continue
            barra_cat = _barra(categoria["porcentaje"] / 100)
            print(
                f"  {categoria['nombre']:<10} {categoria['resueltos']:>2}/"
                f"{categoria['total_ejercicios']} {barra_cat}"
            )

    def do_crear(self, linea):
        """crear\nTe guía para añadir un ejercicio nuevo a la API."""
        titulo = input("Título: ").strip()
        if not titulo:
            print("Abortado: título vacío.")
            return
        print("Enunciado (termina con línea vacía):")
        lineas = []
        while True:
            linea_texto = input("  > ")
            if not linea_texto:
                break
            lineas.append(linea_texto)
        if not lineas:
            print("Abortado: enunciado vacío.")
            return
        enunciado = "\n".join(lineas)
        dificultad = input(f"Dificultad ({'/'.join(_DIFICULTADES)}): ").strip()
        while dificultad not in _DIFICULTADES:
            dificultad = input(f"Dificultad inválida ({'/'.join(_DIFICULTADES)}): ").strip()
        self.do_cat("")
        categoria_id = input("Id de categoría: ").strip()
        try:
            categoria_id = int(categoria_id)
        except ValueError:
            print("Abortado: categoría inválida.")
            return
        pista = input("Pista: ").strip()
        print("Solución (termina con línea vacía):")
        lineas = []
        while True:
            linea_texto = input("  > ")
            if not linea_texto:
                break
            lineas.append(linea_texto)
        if not lineas:
            print("Abortado: solución vacía.")
            return
        solucion = "\n".join(lineas)
        ejemplo_entrada = input("Ejemplo de entrada: ").strip()
        ejemplo_salida = input("Ejemplo de salida: ").strip()
        datos = {
            "titulo": titulo,
            "enunciado": enunciado,
            "dificultad": dificultad,
            "categoria_id": categoria_id,
            "pista": pista,
            "solucion": solucion,
            "ejemplo_entrada": ejemplo_entrada,
            "ejemplo_salida": ejemplo_salida,
        }
        respuesta = self.client.post("/ejercicios", json=datos)
        if respuesta.status_code == 201:
            nuevo = respuesta.json()
            print(_pintar(f"Ejercicio creado: #{nuevo['id']} {nuevo['titulo']}", _VERDE))
        else:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))

    def do_borrar(self, linea):
        """borrar N\nElimina el ejercicio N (y sus intentos)."""
        args = shlex.split(linea)
        if not args:
            print("Uso: borrar N")
            return
        respuesta = self.client.delete(f"/ejercicios/{args[0]}")
        if respuesta.status_code == 204:
            print(_pintar(f"Ejercicio {args[0]} eliminado", _VERDE))
        else:
            print(_pintar(f"Error: {self._detalle_error(respuesta)}", _ROJO))

    def do_exit(self, linea):
        """exit\nSale del shell."""
        print("¡Suerte en el examen!")
        return True

    do_quit = do_exit
    do_salir = do_exit

    def do_EOF(self, linea):
        print()
        return True


def _barra(fraccion: float) -> str:
    ancho = 20
    llenos = round(max(0.0, min(1.0, fraccion)) * ancho)
    return _pintar("█" * llenos + "░" * (ancho - llenos), _VERDE)


def main():
    print(_pintar("API Ejercicios — shell de práctica", _NEGRITA))
    print("Escribe 'help' para ver los comandos disponibles.")
    ApiShell().cmdloop()


if __name__ == "__main__":
    main()