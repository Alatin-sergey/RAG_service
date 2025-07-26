from fastapi import FastAPI
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List, Union

load_dotenv()
app = FastAPI(
    title="Backend service",
    description="API for routing requests between services",
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
def add_to_base(data_url: UrlObject):
    """
    Отправляет URL для индексации в сервис индексирования.
    Эта функция обрабатывает POST-запросы к endpoint "/indexing/". Она извлекает URL из тела запроса,
    отправляет его в сервис индексирования и возвращает ответ от этого сервиса.
    Args:
        data_url: Объект UrlObject, содержащий URL для индексации. Этот объект создается с помощью
                  валидации Pydantic.
    Returns:
        ApiResponse:   Объект ApiResponse, содержащий статус и сообщение ответа от сервиса индексирования.
                       В случае успеха, статус будет "success", а сообщение будет содержать результат
                       индексации. В случае ошибки, функция поднимает исключение HTTPException.
    Exceptions:
        HTTPException: Если запрос к сервису индексирования завершается с ошибкой (например,
                       из-за недоступности сервиса или проблем с сетью), функция поднимает
                       исключение HTTPException с соответствующим кодом состояния и
                       деталями ошибки.
    """
    response = requests.post(
        url=f"http://{os.getenv('INDEXING_SERVICE')}:{os.getenv('INDEXING_PORT')}/indexing/",
        json={"url": data_url.url},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    res = response.json()["message"]
    return ApiResponse(status="success", message=res)


@app.post("/search/", response_model=ApiResponse)
def add_to_base(query: Query):
    """
    Отправляет поисковый запрос в сервис поиска.
    Эта функция обрабатывает POST-запросы к endpoint "/search/". Она извлекает поисковый запрос
    из тела запроса, отправляет его в сервис поиска и возвращает ответ от этого сервиса.
    Args:
        query: Объект Query, содержащий поисковый запрос. Этот объект создается с помощью
               валидации Pydantic.
    Returns:
        ApiResponse: Объект ApiResponse, содержащий статус и сообщение ответа от сервиса поиска.
                     В случае успеха, статус будет "success", а сообщение будет содержать
                     результаты поиска. В случае ошибки, функция поднимает исключение HTTPException.
    Exception:
        HTTPException: Если запрос к сервису поиска завершается с ошибкой (например,
                       из-за недоступности сервиса или проблем с сетью), функция поднимает
                       исключение HTTPException с соответствующим кодом состояния и
                       деталями ошибки.
    """
    response = requests.post(
        url=f"http://{os.getenv('QUERY_SERVICE')}:{os.getenv('QUERY_PORT')}/search/",
        json={"query": query.query},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    res = response.json()["message"]
    return ApiResponse(status="success", message=res)
