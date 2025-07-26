import requests
from requests import HTTPError
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()


def request_in_base(request: str) -> str:
        """
        Эта функция отправляет POST-запрос к эндпоинту "/search/" сервиса индексации,
        передавая поисковый запрос в теле запроса. Она обрабатывает возможные ошибки
        соединения и другие исключения, возвращая релевантный фрагмент текста в случае успеха.
        Args:
            request: str - поисковый запрос, который нужно отправить в сервис индексации.
        Returns:
            text: str - релевантный фрагмент текста, полученный от сервиса индексации.
        """
        try:
            response = requests.post(
                url=f"http://{os.getenv('INDEXING_SERVICE')}:{os.getenv('INDEXING_PORT')}/search/",
                json={"query": request},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            text = response.json()["message"]
            logger.info("Relevant chunk returned success")
            return text
        except HTTPError as e:
            logger.error(f"HTTPError {e}")
            raise HTTPError(f"HTTPError {e}")
        except Exception as e:
            logger.error(f"Relevant chunk didn't return {e}")
            raise ValueError(f"Relevant chunk didn't return {e}")
