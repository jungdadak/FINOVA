# src/data_loader.py
from pathlib import Path
import json
from typing import List
from src.config import settings
from src.models import Question
import logging

logger = logging.getLogger(__name__)


# src/data_loader.py
class DataLoader:
    def __init__(self, data_dir: Path = settings.data_dir):
        self.data_dir = data_dir
        logger.debug(f"DataLoader initialized with data_dir: {self.data_dir}")

    def load_questions(self, exam_name: str, start_num: int = None, end_num: int = None) -> List[Question]:
        """
        Load questions from specified exam and question range

        Args:
            exam_name (str): Name of the exam folder
            start_num (int, optional): Starting question number
            end_num (int, optional): Ending question number
        """
        exam_path = self.data_dir / exam_name
        if not exam_path.exists() or not exam_path.is_dir():
            logger.error(f"Exam folder '{exam_name}' does not exist at path: {exam_path}")
            raise FileNotFoundError(f"Exam folder '{exam_name}' does not exist at path: {exam_path}")

        questions = []

        # Get all json files and sort them by question number
        json_files = sorted(
            exam_path.glob("*.json"),
            key=lambda x: int(x.stem)  # Assumes filename is the question number
        )

        # Filter files based on range if specified
        if start_num is not None:
            json_files = [f for f in json_files if int(f.stem) >= start_num]
        if end_num is not None:
            json_files = [f for f in json_files if int(f.stem) <= end_num]

        for file_path in json_files:
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    question = Question(**data)
                    questions.append(question)
                logger.debug(f"Loaded question ID: {question.id} from {file_path.name}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in file {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error loading question from file {file_path}: {e}")

        logger.info(f"Loaded {len(questions)} questions from {exam_name}")
        return questions