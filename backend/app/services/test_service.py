from typing import List, Dict, Any
from app.schemas.test import TestResult, TestResultDetail


class TestGradingService:
    
    def grade_test(
        self,
        user_answers: List[Dict[str, Any]],
        correct_answers: List[Dict[str, Any]],
        passing_threshold: float = 0.7
    ) -> TestResult:
        """Grade test submission and return detailed results"""
        score = 0
        max_score = len(correct_answers)
        detailed_results = []
        
        # Create answer lookup dict
        correct_lookup = {
            ans["question_id"]: ans["correct_answer"] 
            for ans in correct_answers
        }
        
        for user_answer in user_answers:
            question_id = user_answer["question_id"]
            user_response = user_answer["answer"]
            correct_response = correct_lookup.get(question_id)
            
            is_correct = self._compare_answers(user_response, correct_response)
            
            if is_correct:
                score += 1
            
            detailed_results.append(TestResultDetail(
                question_id=question_id,
                correct=is_correct,
                user_answer=user_response,
                correct_answer=correct_response if not is_correct else None
            ))
        
        percentage = int((score / max_score) * 100)
        passed = (score / max_score) >= passing_threshold
        
        return TestResult(
            score=score,
            max_score=max_score,
            percentage=percentage,
            passed=passed,
            detailed_results=detailed_results
        )
    
    def _compare_answers(self, user_answer: Any, correct_answer: Any) -> bool:
        """Compare user answer with correct answer"""
        if correct_answer is None:
            return False
        
        if isinstance(correct_answer, list):
            # Multiple choice - compare sorted lists
            if not isinstance(user_answer, list):
                return False
            return sorted(user_answer) == sorted(correct_answer)
        elif isinstance(correct_answer, str):
            # Single choice or text input - case insensitive comparison
            if not isinstance(user_answer, str):
                user_answer = str(user_answer)
            return user_answer.strip().lower() == correct_answer.strip().lower()
        else:
            return user_answer == correct_answer


