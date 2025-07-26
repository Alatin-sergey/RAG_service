import requests
from typing import List, Dict
import json
from loguru import logger


def load_json_from_url(url: str) -> List[Dict]:
    """
    Загружает JSON из URL, преобразует в словарь и возвращает список Document.
    Args:
        url: URL JSON-файла.
    Returns:
        Список Document или пустой список в случае ошибки.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.info(f"Ошибка при запросе URL: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.info(f"Ошибка при парсинге JSON: {e}")
        return []
    except Exception as e:
        logger.info(f"Неизвестная ошибка: {e}")
        return []
