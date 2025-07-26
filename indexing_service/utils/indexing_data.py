from typing import List, Dict
import os
from dotenv import load_dotenv
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct
from utils.emb_local_llm import CustomEmbLLM

load_dotenv()
collection_name = os.getenv("COLLECT_NAME", "my_collection")
model = CustomEmbLLM(model_name=os.getenv("EMB_MODEL"))
client = QdrantClient(
    url=f"http://{os.getenv('DB_SERVICE', 'database')}:{os.getenv('DB_PORT', '6333')}", # noqa E501
)


def index_data(data: List[Dict]) -> None:
    """
    Индексирует список словарей, создавая векторные представления текстов и загружая их в коллекцию Qdrant.
    Args:
        data: Список словарей, где каждый словарь должен содержать текстовые данные для индексации.
              Ожидается, что каждый словарь содержит ключ "text" (текст для индексации) и может
              содержать опциональные ключи "uid" (уникальный идентификатор) и "ru_wiki_pageid"
              (идентификатор страницы RuWiki).

    Exceptions:
        ValueError: Если не удается подключиться к Qdrant, создать коллекцию или выполнить индексацию,
                    функция поднимает исключение ValueError с описанием ошибки.
    """
    try:
        client.get_collections()
        logger.info("Successfully connected to Qdrant.")
        if not client.collection_exists(collection_name=collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=int(os.getenv("EMB_SIZE", "512")), 
                    distance=Distance.COSINE,
                ),
            )
        points = []
        for item in data[:int(os.getenv("MAX_CHUNKS")) if os.getenv("MAX_CHUNKS") else len(data)]: # noqa E501
            text = item["text"]
            uid = item["uid"]
            ru_wiki_pageid = item["ru_wiki_pageid"]
            vector = model.generate_embedding(text)
            point = PointStruct(
                id=uid,
                vector=vector,
                payload={
                    "text": text,
                    "ru_wiki_pageid": ru_wiki_pageid,
                },
            )
            points.append(point)
        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True
        )
        logger.info(f"Successfully indexed {len(points)} items to Qdrant collection '{collection_name}'.") # noqa E501
    except ConnectionError as e:
        logger.error(f"Error creating/checking collection: {e}")
        raise ConnectionError(f"Error creating/checking collection: {e}")
    except ValueError as e:
        logger.error(f"Indexing error: {e}")
        raise ValueError(f"Indexing error: {e}")


def search_data(query: str) -> str:
    """
    Выполняет поиск релевантного чанка в коллекции Qdrant на основе заданного запроса.
    Args:
        query: str, представляющая поисковый запрос.

    Returns:
        str: Текст, связанный с наиболее релевантным результатом поиска в Qdrant.

    Exception:
        ValueError:  Если не удается подключиться к Qdrant или выполнить поиск, функция поднимает 
                     исключение ValueError с описанием ошибки.
    """
    try:
        client.get_collections()
        logger.info("Successfully connected to Qdrant.")
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
    vector = model.generate_embedding(query)
    response = client.search(
      collection_name=collection_name,
      query_vector=vector,
      limit=int(os.getenv("NUMBER_CHUNKS", "1")),
    )
    logger.info("Successfully taking embeddings from Qdrant.")
    text = []
    for point in response:
        text.append(point.payload["text"])
    text = " ".join(text)
    return text
