import requests

API_BASE_URL = "http://127.0.0.1:5000/api"

def setup_availability():
    # Ustawienie środy jako dnia pracy od 10:00 do 12:00
    payload = {
        "day_of_week": 2,  # Środa
        "start_time": "10:00",
        "end_time": "12:00"
    }
    try:
        response = requests.post(f"{API_BASE_URL}/availability", json=payload)
        response.raise_for_status()
        print("Harmonogram pracy został pomyślnie ustawiony.")
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas ustawiania harmonogramu: {e}")

if __name__ == "__main__":
    setup_availability()
