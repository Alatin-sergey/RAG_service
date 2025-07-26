from transformers import AutoModel, AutoTokenizer, AutoConfig
from typing import List
from loguru import logger
import torch


class CustomEmbLLM():
    """
    Класс, реализующий генерацию эмбеддингов на основе модели SentenceTransformer.
    """
    def __init__(
            self,
            model_name: str,
    ) -> None:
        """
        Инициализирует экземпляр CustomEmbLLM.
        Args:
            model_name: str - имя модели SentenceTransformer, которую нужно использовать
                        (например, "all-MiniLM-L6-v2").
        Exceptions:
            ValueError: Если не удается загрузить указанную модель SentenceTransformer,
                        поднимается исключение ValueError с сообщением об ошибке.
        """
        self.model_name = model_name
        try:
            self.config = AutoConfig.from_pretrained(self.model_name)
            self.embed_model = AutoModel.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, padding_side='left')
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise ValueError(f"Error loading model {self.model_name}: {e}") from e
    def generate_embedding(self, text: str) -> List[float]:
        """
        Генерирует векторное представление (эмбеддинг) заданного текста.
        Args:
            text: str - текст, для которого нужно сгенерировать эмбеддинг.
        Returns:
            List[float]: Список чисел с плавающей запятой, представляющий
                         векторное представление (эмбеддинг) текста.
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.embed_model(**inputs)
            embeddings = outputs.last_hidden_state[:, -1].tolist()[0]
        return embeddings
