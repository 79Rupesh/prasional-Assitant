from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    name: str
    data: Any = None