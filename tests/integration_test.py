import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.append
def test_indexing_endpoint_integration():
    """
    Проверяет работу /indexing/ endpoint после запуска docker-compose up.
    """
    url = f"http://localhost:{os.getenv("BACKEND_PORT", "localhost")}/indexing/"
    test_query = {"url": os.getenv("DATA_URL", None)}

    try:
        response = requests.post(url, json=test_query)
        print("\n=== RESPONSE HEADERS ===")
        print(response.headers)
        print("=== RESPONSE TEXT ===")
        print(response.text)
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Ошибка соединения: {e}")
    except AssertionError as e:
        pytest.fail(f"Ошибка проверки: {e}")
    except Exception as e:
        pytest.fail(f"Непредвиденная ошибка: {e}")


@pytest.mark.search
def test_search_endpoint_integration():
    """
    Проверяет работу /search/ endpoint после запуска docker-compose up.
    """
    url = f"http://localhost:{os.getenv("BACKEND_PORT", "localhost")}/search/"
    test_query = {"query": "Есть ли базе информация о Беларуссии? Верни ответ 'да' или 'нет'."}
    try:
        response = requests.post(url, json=test_query)

        print("\n=== RESPONSE HEADERS ===")
        print(response.headers)
        print("=== RESPONSE TEXT ===")
        print(response.text)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        assert "message" in response_data
        assert isinstance(response_data["message"], str)
        assert len(response_data["message"]) > 0
        assert "да" in response_data["message"]

        print("Интеграционный тест пройден успешно!")
        print(f"Вопрос: {test_query['query']}")
        print(f"Ответ: {response_data['message']}")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Ошибка соединения: {e}")
    except AssertionError as e:
        pytest.fail(f"Ошибка проверки: {e}")
    except Exception as e:
        pytest.fail(f"Непредвиденная ошибка: {e}")
