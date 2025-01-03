# src/openai_client.py
import openai
import logging
import re
import json
from typing import List, Dict, Any, Optional
from src.config import settings
from src.models import GPTResponse
from src.prompts import Prompts  # Add this import

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, model_name: str = settings.model_name):
        self.model = model_name
        openai.api_key = settings.openai_api_key
        logger.debug(f"OpenAIClient initialized with model_name: {self.model}")

    def get_response(self, question: str, options: List[str], data: Optional[Dict] = None) -> GPTResponse:
        logger.info("Starting OpenAI API request")
        prompt = Prompts.get_question_prompt(question, options, data)
        logger.debug(f"Constructed prompt:\n{prompt}")

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=500,
            )
            logger.info("OpenAI API call successful")
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}", exc_info=True)
            raise ValueError(f"Error during OpenAI API call: {e}")


        try:
            gpt_output = response.choices[0].message['content'].strip()
            logger.debug(f"Raw GPT response:\n{gpt_output}")
            gpt_output_dict = self._extract_json(gpt_output)
            logger.debug(f"Parsed GPT response:\n{gpt_output_dict}")
            parsed_response = GPTResponse.model_validate(gpt_output_dict)
            logger.info("GPT response successfully parsed")
        except Exception as e:
            logger.error(f"Failed to parse GPT response: {e}", exc_info=True)
            raise ValueError(f"Failed to parse GPT response: {e}")

        return parsed_response

    def _extract_json(self, content: str) -> Dict[str, Any]:
        # 전체 응답 로깅
        logger.debug(f"Raw response content:\n{content}")

        try:
            # 먼저 전체 내용을 JSON으로 파싱 시도
            return json.loads(content)
        except json.JSONDecodeError:
            # JSON 코드 블록 찾기
            json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    logger.debug("Failed to parse JSON in code block")

            # 중괄호로 둘러싸인 JSON 찾기
            json_match = re.findall(r"\{[\s\S]*?\}", content)
            for potential_json in json_match:
                try:
                    return json.loads(potential_json)
                except json.JSONDecodeError:
                    continue

            # JSON 문자열 정리 시도
            try:
                # 작은따옴표를 큰따옴표로 변환
                cleaned_content = content.replace("'", '"')
                # 주석 제거
                cleaned_content = re.sub(r"//.*?\n", "\n", cleaned_content)
                return json.loads(cleaned_content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON. Raw content:\n{content}")
                raise ValueError("No valid JSON found in the response")

    @staticmethod
    def construct_prompt(question: str, options: List[str]) -> str:
        options_formatted = "\n".join(options)
        prompt = (
            f"Please provide the correct answer and reasoning for each option in JSON format.\n\n"
            f"Question: {question}\n\n"
            f"Options:\n{options_formatted}\n\n"
            f"Response format:\n{{\n"
            f'  "selected_answer": "1",\n'
            f'  "reasoning": [\n'
            f'    "1. ...",\n'
            f'    "2. ...",\n'
            f'    "3. ...",\n'
            f'    "4. ...",\n'
            f'    "5. ..."\n'
            f'  ]\n'
            f"}}"
        )
        return prompt
