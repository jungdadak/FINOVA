# src/models.py
from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel


# 기존 모델들은 유지
class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: str
    data: Optional[Dict] = None


class GPTResponse(BaseModel):
    selected_answer: str
    reasoning: List[str]


class ComparisonResult(BaseModel):
    question_id: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    reasoning: List[str]


class QuestionResult(BaseModel):
    question_id: str
    start_time: datetime
    end_time: datetime
    execution_time: float
    selected_answer: str
    is_correct: bool
    reasoning: List[str]


class ExamResult(BaseModel):
    exam_name: str
    start_time: datetime
    end_time: datetime
    execution_time: float
    questions_results: List[QuestionResult]
    total_questions: int
    correct_answers: int
    accuracy: float
