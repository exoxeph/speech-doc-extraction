from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OCRResult:
    lines: list[str]
    provider: str


class OCRProvider(Protocol):
    async def extract_text(self, document: bytes) -> OCRResult:
        ...
