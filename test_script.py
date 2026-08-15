import requests
import json

url = "http://127.0.0.1:5000/predict"

# Define a few distinct applicant profiles to test sensitivity
test_applicants = [
    {
        "name": "Low-Risk Profile (Experienced, Zero Claims)",
        "data": {
            "ClaimNb": 0,
            "DrivAge": 45,
            "Region_R41": False
        }
    },
    {
        "name": "Moderate-Risk Profile (Younger Driver)",
        "data": {
            "ClaimNb": 0,
            "DrivAge": 19,
            "Region_R41": True
        }
    },
    {
        "name": "High-Risk Profile (Prior Claims & Young)",
        "data": {
            "ClaimNb": 2,
            "DrivAge": 21,
            "Region_R41": True
        }
    }
]

print("Sending test applicant payloads to the risk-scoring API...\n")

try:
    for applicant in test_applicants:
        print(f"--- Testing: {applicant['name']} ---")
        response = requests.post(url, json=applicant["data"])

        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Error {response.status_code}: {response.text}")
        print("\n")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect. Is your app.py Flask server running?")