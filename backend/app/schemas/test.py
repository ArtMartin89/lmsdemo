from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID


class AnswerSubmission(BaseModel):
    question_id: str
    answer: Any


class TestSubmission(BaseModel):
    answers: List[AnswerSubmission]


class TestResultDetail(BaseModel):
    question_id: str
    correct: bool
    user_answer: Any
    correct_answer: Optional[Any] = None


class TestResult(BaseModel):
    score: int
    max_score: int
    percentage: int
    passed: bool
    detailed_results: List[TestResultDetail]


class TestResultResponse(BaseModel):
    status: str
    result_id: UUID
    score: int
    max_score: int
    percentage: int
    passed: bool
    detailed_results: List[TestResultDetail]
    attempt_number: int
    next_module_unlocked: Optional[str] = None


