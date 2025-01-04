# src/processor.py
import json
import logging
from datetime import datetime
from typing import List, Dict

from tqdm import tqdm

from src.config import settings
from src.data_loader import DataLoader
from src.models import QuestionResult, ExamResult
from src.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, data_loader: DataLoader, openai_client: OpenAIClient):
        self.data_loader = data_loader
        self.openai_client = openai_client
        self.debug_dir = settings.output_dir / "debug"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Processor initialized")

    def process_exam(
        self, exam_name: str = None, start_num: int = None, end_num: int = None
    ) -> ExamResult:
        # 먼저 문제들을 로드
        questions = self.data_loader.load_questions(exam_name, start_num, end_num)

        # questions가 없을 때 None 대신 빈 ExamResult 객체 반환
        if not questions:
            return ExamResult(
                exam_name=exam_name,
                start_time=datetime.now(),
                end_time=datetime.now(),
                execution_time=0,
                questions_results=[],
                total_questions=0,
                correct_answers=0,
                accuracy=0,
            )

        questions_results = []
        debug_info = []
        logger.info(f"Processing {len(questions)} questions for exam '{exam_name}'")

        for idx, question in enumerate(
            tqdm(questions, desc=f"Processing {exam_name}", unit="question"), start=1
        ):
            logger.info(
                f"Processing question {idx}/{len(questions)} (ID: {question.id})"
            )
            try:
                # Record start time
                question_start_time = datetime.now()

                # Get GPT response
                gpt_response = self.openai_client.get_response(
                    question.question, question.options
                )

                # Record end time
                question_end_time = datetime.now()
                question_duration = (
                    question_end_time - question_start_time
                ).total_seconds()

                # Create question result
                is_correct = (
                    gpt_response.selected_answer.upper()
                    == question.correct_answer.upper()
                )
                question_result = QuestionResult(
                    question_id=question.id,
                    start_time=question_start_time,
                    end_time=question_end_time,
                    execution_time=question_duration,
                    selected_answer=gpt_response.selected_answer.upper(),
                    is_correct=is_correct,
                    reasoning=gpt_response.reasoning,
                )
                questions_results.append(question_result)

                # Create debug info
                debug_entry = {
                    "question_id": question.id,
                    "question_text": question.question,
                    "options": question.options,
                    "gpt_response": {
                        "selected_answer": gpt_response.selected_answer,
                        "reasoning": gpt_response.reasoning,
                    },
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "execution_time": question_duration,
                }
                debug_info.append(debug_entry)

                logger.info(
                    f"Question '{question.id}' processed: Correct={is_correct}, Time={question_duration:.2f}s"
                )

            except Exception as e:
                logger.error(
                    f"Error processing question '{question.id}': {e}", exc_info=True
                )
                # Add error info to debug
                debug_info.append(
                    {"question_id": question.id, "error": str(e), "status": "failed"}
                )

        # Calculate exam results
        exam_end_time = datetime.now()
        exam_duration = (exam_end_time - exam_start_time).total_seconds()
        correct_answers = sum(1 for result in questions_results if result.is_correct)

        exam_result = ExamResult(
            exam_name=exam_name,
            start_time=exam_start_time,
            end_time=exam_end_time,
            execution_time=exam_duration,
            questions_results=questions_results,
            total_questions=len(questions),
            correct_answers=correct_answers,
            accuracy=correct_answers / len(questions) if questions else 0,
        )

        # Save debug information
        self._save_debug_info(exam_name, debug_info)

        logger.info(
            f"Completed processing of exam '{exam_name}' with {len(questions_results)} results"
        )
        logger.info(
            f"Exam duration: {exam_duration:.2f}s, Accuracy: {exam_result.accuracy:.2%}"
        )

        return exam_result

    def process_all_exams(self) -> List[ExamResult]:
        """Process all available exams in the data directory."""
        results = []
        exams = self.data_loader.get_all_exams()

        logger.info(f"Starting to process {len(exams)} exams")
        for exam in exams:
            try:
                result = self.process_exam(exam)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Failed to process exam {exam}: {e}", exc_info=True)

        logger.info(
            f"Completed processing all exams. Processed {len(results)} exams successfully"
        )
        return results

    def _save_debug_info(self, exam_name: str, debug_info: List[Dict]):
        """Save detailed debug information for each question."""
        debug_file = self.debug_dir / f"{exam_name}_debug.json"
        try:
            with debug_file.open("w", encoding="utf-8") as f:
                json.dump(
                    debug_info, f, indent=2, ensure_ascii=False, default=str
                )  # default=str to handle datetime serialization
            logger.info(f"Debug information saved to {debug_file}")
        except Exception as e:
            logger.error(f"Failed to save debug information: {e}")
