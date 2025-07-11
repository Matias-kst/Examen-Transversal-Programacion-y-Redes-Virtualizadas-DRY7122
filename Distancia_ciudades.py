import requests
from geopy.geocoders import Nominatim
import time

# Configuración de OpenRouteService
ORS_API_KEY = "5b3ce3597851110001cf62489508a2931d7343a4b917c59d9c6f591a"  
ORS_ENDPOINT = "https://api.openrouteservice.org/v2/directions/"

def geocodificar_ciudad(nombre_ciudad, pais):
    """Obtiene coordenadas usando Nominatim con reintentos"""
    geolocator = Nominatim(user_agent="ors_distance_calculator")
    for _ in range(3):  # 3 intentos
        try:
            location = geolocator.geocode(f"{nombre_ciudad}, {pais}")
            if location:
                return [location.longitude, location.latitude]
            time.sleep(1)
        except Exception:
            time.sleep(2)
    raise ValueError(f"No se pudo geocodificar: {nombre_ciudad}, {pais}")

def calcular_ruta_ors(origen_coord, destino_coord, perfil):
    """Calcula ruta usando OpenRouteService"""
    headers = {
        "Authorization": ORS_API_KEY,
        "Accept": "application/json, application/geo+json"
    }
    
    body = {
        "coordinates": [origen_coord, destino_coord],
        "instructions": "true",
        "language": "es"
    }
    
    try:
        response = requests.post(
            f"{ORS_ENDPOINT}{perfil}", 
            json=body, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", "Error desconocido")
            raise Exception(f"Error ORS: {error_msg}")
            
        return response.json()
    except Exception as e:
        raise Exception(f"Error al calcular ruta: {str(e)}")

def mostrar_resultados(resultado, ciudad_origen, ciudad_destino, perfil):
    """Muestra los resultados de forma clara"""
    if not resultado.get("routes"):
        raise Exception("No se encontraron rutas")
    
    ruta = resultado["routes"][0]
    distancia = ruta["summary"]["distance"] / 1000  # metros a km
    duracion = ruta["summary"]["duration"] / 3600  # segundos a horas
    
    print(f"\n{' RESULTADOS ':=^50}")
    print(f"🗺️ Ruta: {ciudad_origen} → {ciudad_destino}")
    print(f"🚗 Perfil: {perfil}")
    print(f"📏 Distancia: {distancia:.1f} km")
    print(f"⏱ Duración: {duracion:.1f} horas")
    
    if "segments" in ruta:
        print("\nIndicaciones clave:")
        for segmento in ruta["segments"]:
            for paso in segmento["steps"][:5]:  # Mostrar solo 5 pasos
                print(f"→ {paso['instruction']} ({paso['distance']/1000:.1f} km)")

def main():
    print("\n=== CALCULADORA DE RUTAS CHILE-ARGENTINA ===")
    print("Usando OpenRouteService (más preciso para rutas internacionales)")
    
    while True:
        print("\nOpciones:")
        print("1. Calcular nueva ruta")
        print("2. Salir")
        opcion = input("Seleccione: ").strip()
        
        if opcion == "2":
            print("¡Hasta luego!")
            break
            
        if opcion == "1":
            try:
                # Entrada de datos
                print("\nEjemplos válidos:")
                print("Chile: Santiago, Valparaíso, Concepción")
                print("Argentina: Buenos Aires, Mendoza, Córdoba\n")
                
                ciudad_origen = input("Ciudad en Chile: ").strip()
                ciudad_destino = input("Ciudad en Argentina: ").strip()
                
                print("\nPerfiles disponibles:")
                print("driving-car - Auto")
                print("driving-hgv - Camión")
                print("cycling-regular - Bicicleta")
                print("foot-walking - A pie")
                
                perfil = input("Seleccione perfil: ").strip()
                
                # Geocodificación
                print("\n📍 Obteniendo coordenadas...")
                coord_origen = geocodificar_ciudad(ciudad_origen, "Chile")
                coord_destino = geocodificar_ciudad(ciudad_destino, "Argentina")
                print(f"Coordenadas obtenidas: {coord_origen} → {coord_destino}")
                
                # Cálculo de ruta
                print("🛣️ Calculando mejor ruta...")
                resultado = calcular_ruta_ors(coord_origen, coord_destino, perfil)
                
                # Mostrar resultados
                mostrar_resultados(resultado, ciudad_origen, ciudad_destino, perfil)
                
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("🔧 Soluciones:")
                print("- Use nombres oficiales completos")
                print("- Verifique conexión a internet")
                print("- Pruebe con ciudades más grandes")
                print("- Espere 1 minuto y reintente")
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()