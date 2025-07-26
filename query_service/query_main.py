from dotenv import load_dotenv
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, List
from loguru import logger
from utils.request_to_db import request_in_base
from utils.local_llm import CustomQueryLLM
from prompts import system_prompt


load_dotenv()
model = CustomQueryLLM(
    os.getenv("QUERY_MODEL"),
    system_prompt=system_prompt,
)
app = FastAPI(
    title="RAG Query Service",
    description="API for question answering with RAG pipeline",
)


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


@app.post("/search/", response_model=ApiResponse)
def search(query: Query):
    """
    Обрабатывает поисковый запрос, выполняя поиск релевантного фрагмента текста и
    генерируя ответ с использованием языковой модели (LLM).
    Функция обрабатывает POST-запросы к эндпоинту "/search/".  Она выполняет следующие шаги:
    Args:
        query: Объект Query, содержащий поисковый запрос. Этот объект создается с помощью
               валидации Pydantic.
    Returns:
        ApiResponse: Объект ApiResponse, содержащий статус и сообщение ответа.
                     В случае успеха, статус будет "success", а сообщение будет содержать
                     сгенерированный ответ от LLM.  В случае ошибки, статус будет "error",
                     а сообщение будет содержать сообщение об ошибке, а также, опционально,
                     сообщение об ошибке в поле error.
    Exceptions:
        Функция обрабатывает исключения внутри себя и возвращает соответствующие ответы с ошибками.
        Исключения, которые не обрабатываются внутри функции, будут обработаны FastAPI.
    """
    logger.info(f"User query: {query.query}")
    try:
        text = request_in_base(query.query)
        logger.info("Relevant chunk successfully retrieved.")
        response = model.generate(text=text, prompt=query.query)
        logger.error(f"Generation is success")
        return ApiResponse(status="success", message=response)
    except Exception as e:
        logger.error(f"Error during LLM generation: {e}")
        return ApiResponse(status="error", message="LLM generation failed", error=str(e))
