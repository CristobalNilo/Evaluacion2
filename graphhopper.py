import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GRAPHHOPPER_API_KEY")
geocode_url = "https://graphhopper.com/api/1/geocode"
route_url = "https://graphhopper.com/api/1/route"


def geocoding(ubicacion):
    parametros = {
        "q": ubicacion,
        "limit": 1,
        "key": key,
        "locale": "es"
    }

    respuesta = requests.get(
        geocode_url, params=parametros, timeout=20
    )
    respuesta.raise_for_status()

    datos = respuesta.json()
    resultados = datos.get("hits", [])

    if not resultados:
        print("No se encontró la ubicación.")
        return None

    lugar = resultados[0]
    latitud = lugar["point"]["lat"]
    longitud = lugar["point"]["lng"]
    nombre = lugar.get("name", ubicacion)

    return latitud, longitud, nombre


def calcular_ruta(origen, destino):
    parametros = {
        "point": [
            f"{origen[0]},{origen[1]}",
            f"{destino[0]},{destino[1]}"
        ],
        "profile": "car",
        "locale": "es",
        "instructions": "true",
        "calc_points": "true",
        "key": key
    }

    respuesta = requests.get(
        route_url, params=parametros, timeout=30
    )
    respuesta.raise_for_status()

    datos = respuesta.json()
    rutas = datos.get("paths", [])

    if not rutas:
        print("No se encontró una ruta disponible.")
        return

    ruta = rutas[0]

    distancia_km = ruta["distance"] / 1000
    distancia_millas = distancia_km / 1.609344
    tiempo_minutos = ruta["time"] / 60000

    print("\n====================================")
    print("RESULTADO DEL RECORRIDO")
    print("====================================")
    print(f"Origen: {origen[2]}")
    print(f"Destino: {destino[2]}")
    print(f"Distancia: {distancia_km:.2f} km")
    print(f"Distancia: {distancia_millas:.2f} millas")
    print(f"Duración estimada: {tiempo_minutos:.2f} minutos")

    print("\nINSTRUCCIONES DEL VIAJE")
    print("------------------------------------")

    for numero, instruccion in enumerate(
        ruta.get("instructions", []), start=1
    ):
        texto = instruccion["text"]
        distancia = instruccion["distance"] / 1000

        print(f"{numero}. {texto}")
        print(f"   Distancia: {distancia:.2f} km")

    print("====================================\n")


def salir(texto):
    return texto.strip().lower() in ("s", "salir")


def main():
    if not key:
        print("Error: No se encontró la API Key.")
        print("Revisa el archivo .env")
        return

    print("====================================")
    print("SISTEMA DE GEOLOCALIZACIÓN")
    print("====================================")
    print("Escribe 's' o 'salir' para terminar.")

    while True:
        origen_texto = input(
            "\nIngrese la ubicación de origen: "
        ).strip()

        if salir(origen_texto):
            break

        if not origen_texto:
            print("Debe ingresar una ubicación.")
            continue

        destino_texto = input(
            "Ingrese la ubicación de destino: "
        ).strip()

        if salir(destino_texto):
            break

        if not destino_texto:
            print("Debe ingresar un destino.")
            continue

        try:
            origen = geocoding(origen_texto)
            destino = geocoding(destino_texto)

            if origen and destino:
                calcular_ruta(origen, destino)

        except requests.exceptions.RequestException as error:
            print(f"Error al consultar GraphHopper: {error}")

    print("\nPrograma finalizado correctamente.")


if __name__ == "__main__":
    main()