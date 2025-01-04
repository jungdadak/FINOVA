# src/openai_client.py
import logging
from typing import List, Dict, Optional

import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from src.config import settings
from src.models import GPTResponse  # 기존 모델과의 호환성 유지
from src.prompts import Prompts
from src.schemas import AnswerResponse

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, model_name: str = settings.model_name):
        self.model = model_name
        openai.api_key = settings.openai_api_key
        logger.debug(f"OpenAIClient initialized with model_name: {self.model}")

    def get_response(
        self, question: str, options: List[str], data: Optional[Dict] = None
    ) -> GPTResponse:
        """
        질문에 대한 응답을 생성합니다.
        기존 GPTResponse 형식과의 호환성을 유지합니다.
        """
        logger.info("Starting OpenAI API request")
        prompt = Prompts.get_question_prompt(question, options, data)
        logger.debug(f"Constructed prompt:\n{prompt}")

        try:
            response = self._make_api_call(
                prompt=prompt,
            )
            logger.info("OpenAI API call successful")

            # AnswerResponse에서 GPTResponse로 변환
            structured_response = self._validate_and_parse_response(response)
            return GPTResponse(
                selected_answer=structured_response.selected_answer,
                reasoning=structured_response.reasoning,
            )

        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}", exc_info=True)
            raise ValueError(f"Error during OpenAI API call: {str(e)}")

    def _make_api_call(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> ChatCompletion:
        return openai.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": Prompts.SYSTEM_MESSAGE},
                {"role": "user", "content": prompt},
            ],
            response_format=AnswerResponse,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _validate_and_parse_response(self, response: ChatCompletion) -> AnswerResponse:
        message: ChatCompletionMessage = response.choices[0].message

        if message.refusal:
            refusal_msg = message.refusal
            logger.warning(f"Model refused to answer: {refusal_msg}")
            raise ValueError(f"Model refused to answer: {refusal_msg}")

        if response.choices[0].finish_reason == "length":
            logger.warning("Response truncated due to length limit")
            raise ValueError("Response was truncated due to length limit")

        if response.choices[0].finish_reason == "content_filter":
            logger.warning("Response filtered by content policy")
            raise ValueError("Response was filtered due to content policy")

        return message.parsed
