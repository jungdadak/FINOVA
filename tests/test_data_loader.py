import unittest
from pathlib import Path
from src.data_loader import DataLoader
from src.models import Question
from src.config import settings


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        self.data_loader = DataLoader(data_dir=settings.data_dir)
        self.test_exam = "2023_1형"

    def test_load_questions_success(self):
        """Test if questions are successfully loaded"""
        questions = self.data_loader.load_questions(self.test_exam)
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
        self.assertIsInstance(questions[0], Question)

    def test_load_questions_invalid_path(self):
        """Test loading questions with an invalid path"""
        with self.assertRaises(FileNotFoundError):
            self.data_loader.load_questions("invalid_exam")

    def test_get_all_exams(self):
        """Test getting all exam names"""
        exams = self.data_loader.get_all_exams()
        self.assertIsInstance(exams, list)
        self.assertIn(self.test_exam, exams)


if __name__ == '__main__':
    unittest.main()
