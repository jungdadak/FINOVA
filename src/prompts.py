# src/prompts.py
from typing import List, Dict, Optional
import json


class Prompts:
    SYSTEM_MESSAGE = """특별한 언급이 없는 한 기업의 보고기간(회계기간)은
매년 1월 1일부터 12월 31일까지이다. 자료에서 제시한 것 외의
사항은 고려하지 않고 답한다. 예를 들어, 법인세에 대한 언급이
없으면 법인세효과는 고려하지 않는다. 또한 기업은 주권상장법인으로
계속해서 한국채택국제회계기준(K-IFRS)을 적용"""

    @staticmethod
    def get_question_prompt(question: str, options: List[str], data: Optional[Dict] = None) -> str:
        # Base question and options
        prompt = f"Please analyze the following multiple choice question and provide your answer with reasoning.\n\n"
        prompt += f"Question: {question}\n\n"

        # Add table/data if present
        if data:
            prompt += "Additional Data:\n"
            prompt += json.dumps(data, ensure_ascii=False, indent=2) + "\n\n"

        prompt += "Options:\n" + "\n".join(f"{idx + 1}. {opt}" for idx, opt in enumerate(options)) + "\n\n"

        # Response format instruction
        prompt += (
            "아래의 JSON 형식으로 대답을 제공하세요\n"
            "{\n"
            '  "selected_answer": "1",  // The number (1-5) of your chosen option\n'
            '  "reasoning": [\n'
            '    "1.1번 보기가 왜 정확한지 또는 틀린지",\n'
            '    "2. 2번 보기가 왜 정확한지 또는 틀린지",\n'
            '    "3. 3번 보기가 왜 정확한지 또는 틀린지",\n'
            '    "4. 4번 보기가 왜 정확한지 또는 틀린지",\n'
            '    "5. 5번 보기가 왜 정확한지 또는 틀린지"\n'
            "  ]\n"
            "}"
        )
        return prompt
