# src/types.py
from typing import TypedDict, List


class AnswerResponseDict(TypedDict):
    selected_answer: str
    reasoning: List[str]
