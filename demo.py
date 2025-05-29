import requests
import time
import json

BASE_URL = "http://localhost:83"

def test_api():
    print("=== Демонстрация Movie Reviews Similarity API ===\n")
    
    print("1. Проверка состояния сервиса...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Статус: {response.json()}\n")
    
    print("2. Добавление нового отзыва...")
    review_data = {
        "text": "This movie was great.",
        "sentiment": 1
    }
    response = requests.post(f"{BASE_URL}/add_review", json=review_data)
    print(response.json())
    add_task_id = response.json()["task_id"]
    print(f"Задача создана: {add_task_id}")
    
    time.sleep(3)
    
    status_response = requests.get(f"{BASE_URL}/status/{add_task_id}")
    print(f"Результат добавления: {status_response.json()}\n")
    
    print("3. Поиск похожих отзывов...")
    similarity_data = {
        "text": "This movie was amazing"
    }
    response = requests.post(f"{BASE_URL}/find_similar", json=similarity_data)
    search_task_id = response.json()["task_id"]
    print(f"Задача поиска создана: {search_task_id}")
    
    time.sleep(5)
    
    status_response = requests.get(f"{BASE_URL}/status/{search_task_id}")
    result = status_response.json()
    print(f"Результат поиска:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n4. Повторный поиск (должен использовать кэш)...")
    response = requests.post(f"{BASE_URL}/find_similar", json=similarity_data)
    cached_task_id = response.json()["task_id"]
    
    time.sleep(2)
    
    status_response = requests.get(f"{BASE_URL}/status/{cached_task_id}")
    cached_result = status_response.json()
    print(f"Кэшированный результат:")
    print(json.dumps(cached_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к API. Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"Ошибка: {e}") 