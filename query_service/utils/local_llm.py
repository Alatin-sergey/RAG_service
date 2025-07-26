from transformers import AutoModelForCausalLM, AutoTokenizer
from dotenv import load_dotenv
from loguru import logger
import torch

load_dotenv()


class CustomQueryLLM():
    """
    Класс, реализующий генерацию текста на основе запроса с использованием
    указанной языковой модели (LLM) из библиотеки Transformers.

    Этот класс использует модель AutoModelForCausalLM
    из библиотеки `transformers` для создания текста.
    """
    def __init__(
        self, 
        model_name: str,
        system_prompt: str,
        torch_dtype = "FLOAT16",
    ) -> None:
        """
        Инициализирует экземпляр CustomQueryLLM.
        Args:
            model_name: str - имя модели, которую нужно использовать. Используются только модели
                        свободного доступа.
            system_prompt: str - системный промпт, который используется для
                           задания контекста и инструкций для языковой модели.
                           В строке должен присутствовать `{text}`, который будет заменен
                           на входящий чанк текста.
            torch_dtype: str - тип данных torch, который нужно использовать для
                         загрузки модели. Может быть "FLOAT32" или "FLOAT16".
                         По умолчанию используется "FLOAT16".
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.torch_dtype = torch
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32 if torch_dtype=="FLOAT32" else torch.float16, # noqa E501
            device_map="auto",
        )
        self.system_prompt = system_prompt

    def generate(self, text: str, prompt: str) -> str:
        """
        Генерирует текст на основе предоставленного текста и запроса, используя LLM.
        Этот метод формирует запрос для языковой модели, объединяя системный промпт,
        контекстный текст и запрос пользователя, а затем генерирует ответ с
        помощью языковой модели.
        Args:
            text: str - контекстный текст, который используется в качестве
                  основы для генерации ответа.
            prompt: str - запрос пользователя, который определяет, какой
                    ответ должна сгенерировать модель.
        Returns:
            str: Сгенерированный текст, основанный на предоставленном контексте и запросе.
        """
        logger.info(f"Returned chunk: {text}")
        messages = [
            {"role": "system", "content": self.system_prompt.format(text=text)},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )
        logger.info(f"Final prompt: {text}")
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device) # noqa E501
        response_ids = self.model.generate(**model_inputs, max_new_tokens=32768)[0][len(model_inputs.input_ids[0]):].tolist() # noqa E501
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True) # noqa E501
        logger.info(f"Model answer: {response}")
        return response
