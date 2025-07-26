from fastapi import FastAPI
from pydantic import BaseModel
from utils.downloader import load_json_from_url
from utils.preprocessor import preprocessor
from utils.indexing_data import index_data, search_data
from loguru import logger
from dotenv import load_dotenv
from typing import Union, List

load_dotenv()
app = FastAPI(
    title="Indexing service",
    description="API for indexing data to database and search relevant chunks",
)


class UrlObject(BaseModel):
    """
    Модель данных для URL, используемая для валидации входных данных.
    Атрибуты:
        url: str - URL для индексации.
    """
    url : str


class Query(BaseModel):
    """
    Модель данных для запроса на поиск, используемая для валидации входных данных.
    Атрибуты:
        query: str - текст запроса пользователя.
    """
    query : str


class ApiResponse(BaseModel):
    """
    Модель данных для ответа API.
    Атрибуты:
        status: str - статус ответа (например, "success" или "error").
        message: str или List[str] - сообщение, содержащее результат операции.
        error: str - текст возникшей ошибки. Пустая, если статус "success"
    """
    status: str
    message: Union[str, List[str]] = ""
    error: str = ""


@app.post("/indexing/", response_model=ApiResponse)
def indexing(item : UrlObject):
    """
    Endpoint для индексации данных из указанного URL.
    Args:
        item: UrlObject, содержащий URL данных для индексации.
    Returns:
        ApiResponse: Объект, содержащий статус и сообщение об операции.
                     Возможные статусы:
                     - "success": Данные успешно проиндексированы.
                     - "error": Произошла ошибка во время загрузки, предобработки или индексации.
                     - "warning": Данные оказались пустыми после предобработки.
    """
    logger.info(f"Received indexing request for URL: {item.url}")
    try:
        data = load_json_from_url(item.url)
        logger.info(f"Successfully downloaded data from {item.url}")
        data = preprocessor(data)
        logger.info("Data preprocessing completed successfully.")
        index_data(data)
        logger.info("Data indexing completed successfully.")
        return ApiResponse(status="success", message="Data indexed successfully")
    except Exception as e:
        logger.error(f"Error during data indexing: {e}")
        return ApiResponse(
            status="error", 
            message="Indexing failed", 
            error=str(e)
        )


@app.post("/search/", response_model=ApiResponse)
async def search(item : Query):
    """
    Endpoint для поиска в базе данных по предоставленному запросу.
    Args:
        item: Query object, содержащий поисковый запрос.
    Returns:
        ApiResponse: Объект, содержащий статус (всегда "success" в этой версии) и
                     сообщение (результат поиска) об операции.
    """
    logger.info(f"Received request for query: '{item.query}'")
    try:
        result = search_data(query = item.query)
        return ApiResponse(status="success", message=result)
    except Exception as e:
            logger.error(f"Error during searching: {e}")
            return ApiResponse(
                status="error", 
                message="Searching failed", 
                error=str(e)
            )
