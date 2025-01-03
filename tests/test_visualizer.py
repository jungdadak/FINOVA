import unittest
from pathlib import Path
from src.visualizer import Visualizer
from src.models import ComparisonResult
from src.config import settings


class TestVisualizer(unittest.TestCase):
    def setUp(self):
        """Setup before each test"""
        self.visualizer = Visualizer(output_dir=settings.output_dir)
        self.sample_results = [
            ComparisonResult(
                question_id="Q1",
                selected_answer="3",
                correct_answer="3",
                is_correct=True,
                reasoning=[
                    "1. Earth is not the largest planet.",
                    "2. Mars is smaller than Earth.",
                    "3. Jupiter is the largest planet.",
                    "4. Venus is smaller than Earth.",
                    "5. Saturn is large but smaller than Jupiter.",
                ],
            )
        ]
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def test_generate_score_visualization(self):
        """Test score visualization generation"""
        self.visualizer.generate_score_visualization(self.sample_results, "2023_1형")
        chart_path = self.output_dir / "test_exam_score_pie_chart.png"
        self.assertTrue(chart_path.exists())

    def test_generate_corrections_table(self):
        """Test corrections table generation"""
        self.visualizer.generate_corrections_table(self.sample_results, "2023_1형")
        corrections_path = self.output_dir / "test_exam_corrections.csv"
        self.assertTrue(corrections_path.exists())


if __name__ == '__main__':
    unittest.main()
