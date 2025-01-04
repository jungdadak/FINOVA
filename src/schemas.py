# src/schemas.py
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class AnswerResponse(BaseModel):
    """OpenAI Structured Output을 위한 응답 스키마"""

    selected_answer: str = Field(description="선택한 답변 번호", pattern="^[1-5]$")
    reasoning: List[str] = Field(
        description="각 보기에 대한 reasoning", min_length=5, max_length=5
    )

    # class Config 대신 model_config 사용
    model_config = ConfigDict(
        extra="forbid",  # 추가 필드 금지
        validate_assignment=True,  # 할당 시에도 검증
        frozen=True,  # 불변 객체로 만들기
    )
