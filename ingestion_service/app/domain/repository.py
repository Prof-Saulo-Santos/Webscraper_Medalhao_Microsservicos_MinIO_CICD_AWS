from typing import Protocol, Dict, Any


class RepositoryProtocol(Protocol):
    async def save_json(self, key: str, data: Dict[str, Any]) -> None:
        """Salva um dicionário como JSON no repositório."""
        ...
