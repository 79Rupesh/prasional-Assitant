from dataclasses import dataclass


@dataclass
class ResponseResult:
    response: str
    needs_llm: bool = False