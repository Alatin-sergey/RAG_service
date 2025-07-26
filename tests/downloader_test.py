import pytest
from unittest.mock import patch
from indexing_service.utils.downloader import load_json_from_url
import requests


@pytest.mark.unit
@patch("indexing_service.utils.downloader.requests.get")
def test_load_json_from_url_success(mock_get):
    """Тестирует успешную загрузку валидного JSON"""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "text": "Пример текста 1"},
        {"id": 2, "text": "Пример текста 2"}
    ]
    test_url = "http://example.com/data.json"
    result = load_json_from_url(test_url)
    mock_get.assert_called_once_with(test_url, timeout=10)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["text"] == "Пример текста 2"


@pytest.mark.unit
@patch("indexing_service.utils.downloader.requests.get")
def test_load_json_from_url_http_error(mock_get):
    """Тестирует обработку HTTP ошибки"""
    mock_response = mock_get.return_value
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    test_url = "http://example.com/not-found.json"
    result = load_json_from_url(test_url)
    mock_get.assert_called_once_with(test_url, timeout=10)
    assert result == []


@pytest.mark.unit
@patch("indexing_service.utils.downloader.requests.get")
def test_load_json_from_url_connection_error(mock_get):
    """Тестирует обработку ошибки соединения"""
    mock_get.side_effect = requests.exceptions.ConnectionError("Ошибка соединения")
    test_url = "http://example.com/unreachable.json"
    result = load_json_from_url(test_url)
    mock_get.assert_called_once_with(test_url, timeout=10)
    assert result == []


@pytest.mark.unit
@patch("indexing_service.utils.downloader.requests.get")
def test_load_json_from_url_timeout(mock_get):
    """Тестирует обработку таймаута"""
    mock_get.side_effect = requests.exceptions.Timeout("Время ожидания истекло")
    test_url = "http://example.com/slow.json"
    result = load_json_from_url(test_url)
    mock_get.assert_called_once_with(test_url, timeout=10)
    assert result == []


@pytest.mark.unit
@patch("indexing_service.utils.downloader.requests.get")
def test_load_json_from_url_invalid_json(mock_get):
    """Тестирует обработку невалидного JSON"""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    test_url = "http://example.com/invalid.json"
    result = load_json_from_url(test_url)
    mock_get.assert_called_once_with(test_url, timeout=10)
    assert result == []
