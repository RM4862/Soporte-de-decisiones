"""
test_rayleigh_api.py
-------------------
Script de prueba para verificar el funcionamiento del API Rayleigh
adaptado para usar etapas como tiempo.
"""
import requests
import json

# Configuración del API
API_URL = "http://localhost:5000"
AUTH_KEY = "changeme"  # Mismo que RESP_KEY en rayleigh_api.py

def test_predict():
    """Prueba el endpoint /predict (modelo pre-entrenado)"""
    print("\n=== Test 1: Predicción con modelo entrenado ===")
    
    response = requests.post(
        f"{API_URL}/predict",
        json={"auth_key": AUTH_KEY, "round": 2},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_predict_filtered():
    """Prueba el endpoint /predict_filtered con filtros"""
    print("\n=== Test 2: Predicción filtrada ===")
    
    # Sin filtros
    response = requests.post(
        f"{API_URL}/predict_filtered",
        json={
            "auth_key": AUTH_KEY,
            "filters": {}
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Con filtros de etapa
    print("\n--- Test 2b: Filtrado por etapas específicas ---")
    response2 = requests.post(
        f"{API_URL}/predict_filtered",
        json={
            "auth_key": AUTH_KEY,
            "filters": {
                "etapas": ["Ejecución", "Monitoreo y Control"]
            }
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response2.status_code}")
    print(f"Response:\n{json.dumps(response2.json(), indent=2)}")
    
    return response.status_code == 200


def test_unauthorized():
    """Prueba el rechazo de requests sin autenticación"""
    print("\n=== Test 3: Sin autenticación (debe fallar) ===")
    
    response = requests.post(
        f"{API_URL}/predict",
        json={},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code} (esperado: 401)")
    return response.status_code == 401


if __name__ == '__main__':
    print("=" * 60)
    print("PRUEBAS DEL API RAYLEIGH")
    print("=" * 60)
    print("\nNota: Asegúrate de que el API esté corriendo:")
    print("  python rayleigh_api.py")
    print("\nPresiona Enter para continuar...")
    input()
    
    try:
        test1 = test_predict()
        test2 = test_predict_filtered()
        test3 = test_unauthorized()
        
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        print(f"✓ Test 1 (Predict): {'PASSED' if test1 else 'FAILED'}")
        print(f"✓ Test 2 (Predict Filtered): {'PASSED' if test2 else 'FAILED'}")
        print(f"✓ Test 3 (Unauthorized): {'PASSED' if test3 else 'FAILED'}")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: No se pudo conectar al API.")
        print("  Asegúrate de que el servidor esté corriendo:")
        print("  python rayleigh_api.py")
