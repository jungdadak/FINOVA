import unittest
import json
from unittest.mock import patch, MagicMock
from src.openai_client import OpenAIClient
from src.models import GPTResponse


class TestOpenAIClient(unittest.TestCase):
    def setUp(self):
        self.client = OpenAIClient()
        self.sample_question = "What is the largest planet in the solar system?"
        self.sample_options = [
            "1. Earth",
            "2. Mars",
            "3. Jupiter",
            "4. Venus",
            "5. Saturn"
        ]

    @patch('openai.ChatCompletion.create')
    def test_get_response_success(self, mock_create):
        valid_json = {
            "selected_answer": "3",
            "reasoning": [
                "1. Earth is not the largest.",
                "2. Mars is not the largest.",
                "3. Jupiter is the largest planet.",
                "4. Venus is not the largest.",
                "5. Saturn is smaller than Jupiter."
            ]
        }
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message={"content": json.dumps(valid_json)})]
        )

        response = self.client.get_response(self.sample_question, self.sample_options)
        self.assertEqual(response.selected_answer, "3")
        self.assertEqual(len(response.reasoning), 5)

    @patch('openai.ChatCompletion.create')
    def test_get_response_parsing_error(self, mock_create):
        invalid_json_response = "Invalid JSON"
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message={"content": invalid_json_response})]
        )

        with self.assertRaises(ValueError) as context:
            self.client.get_response(self.sample_question, self.sample_options)

        self.assertIn("Failed to parse GPT response", str(context.exception))


if __name__ == '__main__':
    unittest.main()