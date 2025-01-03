import unittest
from unittest.mock import MagicMock
from src.processor import Processor
from src.models import ComparisonResult, Question
from src.data_loader import DataLoader
from src.openai_client import OpenAIClient


class TestProcessor(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        self.mock_data_loader = MagicMock(spec=DataLoader)
        self.mock_openai_client = MagicMock(spec=OpenAIClient)
        self.processor = Processor(self.mock_data_loader, self.mock_openai_client)
        self.sample_questions = [
            Question(
                id="Q1",
                question="What is the largest planet?",
                options=["1. Earth", "2. Mars", "3. Jupiter", "4. Venus", "5. Saturn"],
                correct_answer="3",
            )
        ]

    def test_process_exam_success(self):
        """Test successful exam processing"""
        self.mock_data_loader.load_questions.return_value = self.sample_questions
        self.mock_openai_client.get_response.return_value = MagicMock(
            selected_answer="3",
            reasoning=[
                "1. Earth is not the largest planet.",
                "2. Mars is smaller than Earth.",
                "3. Jupiter is the largest planet.",
                "4. Venus is smaller than Earth.",
                "5. Saturn is large but smaller than Jupiter.",
            ],
        )

        results = self.processor.process_exam("2023_1형")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], ComparisonResult)
        self.assertTrue(results[0].is_correct)

    def test_process_exam_no_questions(self):
        """Test processing with no questions"""
        self.mock_data_loader.load_questions.return_value = []
        results = self.processor.process_exam("empty_exam")
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
