import unicodedata
from loguru import logger
from llama_index.core.text_splitter import TokenTextSplitter 
from typing import List, Dict, Any


def clean_and_normalize_text(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Очищает текст непосредственно в словарях списка data от лишних HTML-символов и нормализует текст.
    Args:
        data: Список словарей, где каждый словарь имеет ключ "text".
    Returns:
        Список словарей с очищенным текстом (измененный исходный список).
    """
    total_bad_char_count = 0
    for item in data:
        text = item["text"]
        cleaned_text = ""
        bad_char_count = 0
        for char in text:
            try:
                if unicodedata.category(char) in ['Cc', 'Cf', 'Cs', 'Co', 'Cn']:
                    bad_char_count += 1
                    continue
                else:
                    cleaned_text += char
            except ValueError:
                bad_char_count += 1
                continue
        item["text"] = unicodedata.normalize('NFKC', cleaned_text)
        total_bad_char_count += bad_char_count
    logger.info(f"Bad chars deleted: {total_bad_char_count}")
    return data


def chunker(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Разбивает список словарей, содержащих тексты из Википедии, на более мелкие фрагменты (chunks)
    для последующей обработки, группируя тексты по ru_wiki_pageid и используя TokenTextSplitter.
    Args:
        data: Список словарей, где каждый словарь представляет собой документ из Википедии и
              должен содержать ключи "ru_wiki_pageid" и "text".
    Returns:
        Список словарей, где каждый словарь представляет собой фрагмент текста.
    """
    wiki_pages = {}
    for doc in data:
        if doc["ru_wiki_pageid"] not in wiki_pages.keys():
            wiki_pages[doc["ru_wiki_pageid"]] = [doc["text"]]
        else:
            wiki_pages[doc["ru_wiki_pageid"]].append(doc["text"])

    for key, pages in wiki_pages.items():
        wiki_pages[key] = " ".join(pages)
    splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=100)
    final_chunks = []
    i = 0
    for key, page in wiki_pages.items():
        for text in splitter.split_text(page):
            final_chunks.append({
                "uid": i,
                "ru_wiki_pageid": key,
                "text": text,
            })
            i += 1
    return final_chunks


def preprocessor(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Выполняет предобработку списка словарей, содержащих тексты. Собирает 
    существующие функции.
    Args:
        data: Список словарей, где каждый словарь представляет собой документ и содержит
              текстовые данные.
    Returns:
        Список словарей, где каждый словарь представляет собой фрагмент текста после
        очистки, нормализации и разбиения на фрагменты.
    """
    data = clean_and_normalize_text(data)
    data = chunker(data)
    return data
