import requests

url = "http://127.0.0.1:5000/predict_input"   

data = {
    "cpu_usage": 50,
    "memory_usage": 30,"energy_kwh": 50,
    "disk_usage": 40
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Raw Response:", response.text)