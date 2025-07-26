import pytest
from unittest.mock import patch, MagicMock
from query_service.utils.local_llm import CustomQueryLLM


@pytest.fixture
def mock_model():
    """
    Создание моки для модели из класса CustomQueryLLM
    """
    with patch('transformers.AutoModelForCausalLM.from_pretrained') as mock:
        mock_model = MagicMock()
        mock.return_value = mock_model
        mock_model.device = 'cpu'
        yield mock_model


@pytest.fixture
def mock_tokenizer():
    """
    Создание моки для токенизера из класса CustomQueryLLM
    """
    with patch('transformers.AutoTokenizer.from_pretrained') as mock:
        mock_tokenizer = MagicMock()
        mock.return_value = mock_tokenizer
        def mock_apply_chat_template(messages, **kwargs):
            system_msg = messages[0]['content']
            user_msg = messages[1]['content']
            return f"<s>{system_msg}\n{user_msg}</s>"
        mock_tokenizer.apply_chat_template.side_effect = mock_apply_chat_template
        mock_tokenizer.decode.return_value = "Mocked LLM response"
        yield mock_tokenizer

@pytest.mark.unit
def test_prompt_generation(mock_model, mock_tokenizer):
    """
    Тест корретности формирования промпта
    """
    system_prompt = "Ты - AI-ассистент. Информация: {text}"
    llm = CustomQueryLLM(
        model_name="test-model",
        system_prompt=system_prompt,
        torch_dtype="FLOAT16"
    )
    context = "Пример контекста из базы данных"
    user_query = "Какой-то вопрос пользователя"
    response = llm.generate(text=context, prompt=user_query)
    expected_system_content = system_prompt.format(text=context)
    mock_tokenizer.apply_chat_template.assert_called_once()
    args, kwargs = mock_tokenizer.apply_chat_template.call_args
    messages = args[0]
    
    assert messages[0]['role'] == 'system'
    assert messages[0]['content'] == expected_system_content
    assert messages[1]['role'] == 'user'
    assert messages[1]['content'] == user_query
    assert response == "Mocked LLM response"
