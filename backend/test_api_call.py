import requests
import json

url = 'http://localhost:5000/predict_filtered'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'changeme'
}
data = {
    'auth_key': 'changeme',
    'filters': {
        'metodologia': 'Scrum',
        'horas_invertidas_max': 553
    }
}

print("Llamando al API con:")
print(json.dumps(data, indent=2))
print("\n" + "=" * 60)

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
