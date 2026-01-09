import re
from app.domain.ports import CleanerProtocol


class RegexCleaner(CleanerProtocol):
    def __init__(self):
        # Stopwords mínimas hardcoded para evitar dependência externa
        # Stopwords mínimas hardcoded para evitar dependência externa
        self.stop_words = {
            # Artigos e conjunções
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            # Preposições
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "as",
            "by",
            "from",
            "into",
            "about",
            "between",
            "during",
            "via",
            # Verbos auxiliares comuns
            "is",
            "are",
            "was",
            "were",
            "can",
            "could",
            "may",
            "might",
            "should",
            "would",
            # Pronomes
            "it",
            "we",
            "our",
            "this",
            "these",
            "those",
            "each",
            "both",
            "which",
            # Palavras genéricas em artigos científicos
            "that",
            "such",
            "other",
            "another",
            "also",
            "using",
            "used",
            "based",
            "than",
            "however",
            "although",
            "while",
            "thus",
            "hence",
        }

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        # 1. Lowercase
        text = text.lower()

        # 2. Remove caracteres especiais (mantém letras e espaços)
        # OBS: Remove acentos e números. Para suporte multi-idioma, ajustar regex.
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        # 3. Tokenização simples (split por espaço)
        tokens = text.split()

        # 4. Remove stopwords
        filtered_tokens = [w for w in tokens if w not in self.stop_words and len(w) > 2]

        return " ".join(filtered_tokens)
