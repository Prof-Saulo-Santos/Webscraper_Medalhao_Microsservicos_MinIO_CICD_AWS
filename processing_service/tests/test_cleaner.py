# tests/test_cleaner.py
from app.infrastructure.regex_cleaner import RegexCleaner


def test_cleaner_removes_stopwords_and_special_chars():
    cleaner = RegexCleaner()
    raw_text = "The AI is great! It's 100% efficient."
    # Esperado: remove 'the', 'is', 'it', '!', '100%', ' efficient' -> 'great efficient'
    # Nota: nossa regex remove numeros e palavras < 3 chars
    result = cleaner.clean_text(raw_text)
    assert "great" in result
    assert "efficient" in result
    assert "100" not in result
    assert "!" not in result


def test_cleaner_edge_cases():
    cleaner = RegexCleaner()
    # Caso vazio
    assert cleaner.clean_text("") == ""
    # Caso apenas stopwords
    assert cleaner.clean_text("the and of") == ""
    # Caso caracteres menores que 3
    assert cleaner.clean_text("ab cd") == ""
