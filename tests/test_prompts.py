# tests/test_prompts.py
import unittest
from src.prompts import Prompts

class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.sample_question = "What is X?"
        self.sample_options = ["1. A", "2. B", "3. C"]
        self.sample_data = {
            "table": [
                ["Header1", "Header2"],
                ["Value1", "Value2"]
            ]
        }

    def test_get_question_prompt_no_data(self):
        prompt = Prompts.get_question_prompt(self.sample_question, self.sample_options)
        self.assertIn(self.sample_question, prompt)
        self.assertIn("Options:", prompt)
        self.assertIn("JSON format", prompt)

    def test_get_question_prompt_with_data(self):
        prompt = Prompts.get_question_prompt(
            self.sample_question,
            self.sample_options,
            self.sample_data
        )
        self.assertIn("Additional Data:", prompt)
        self.assertIn("Header1", prompt)