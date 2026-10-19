from dataclasses import dataclass


@dataclass
class Permission:
    action: str
    allowed: bool = False