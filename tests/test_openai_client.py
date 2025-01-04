from unittest.mock import Mock, patch

import pytest
from openai import APIError  # APIError import 수정
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage

from src.models import GPTResponse
from src.openai_client import OpenAIClient
from src.schemas import AnswerResponse


@pytest.fixture
def mock_openai_response():
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.parsed = AnswerResponse(
        selected_answer="1",
        reasoning=["이유 1번", "이유 2번", "이유 3번", "이유 4번", "이유 5번"],
    )
    mock_message.refusal = None

    mock_choice = Mock(spec=Choice)
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_completion = Mock(spec=ChatCompletion)
    mock_completion.choices = [mock_choice]

    return mock_completion


@pytest.fixture
def client():
    return OpenAIClient(model_name="gpt-4o")


def test_successful_response(client, mock_openai_response):
    """정상적인 API 응답 처리 테스트"""
    with patch("openai.beta.chat.completions.parse", return_value=mock_openai_response):
        response = client.get_response(
            question="테스트 질문입니다.",
            options=["보기1", "보기2", "보기3", "보기4", "보기5"],
        )

        assert isinstance(response, GPTResponse)
        assert response.selected_answer == "1"
        assert len(response.reasoning) == 5


def test_model_refusal(client):
    """모델이 응답을 거부하는 경우 테스트"""
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.refusal = "모델이 응답을 거부했습니다."
    mock_message.parsed = None

    mock_choice = Mock(spec=Choice)
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_completion = Mock(spec=ChatCompletion)
    mock_completion.choices = [mock_choice]

    with patch("openai.beta.chat.completions.parse", return_value=mock_completion):
        with pytest.raises(ValueError, match="Model refused to answer"):
            client.get_response(
                question="부적절한 질문",
                options=["보기1", "보기2", "보기3", "보기4", "보기5"],
            )


def test_length_limit_exceeded(client):
    """응답이 길이 제한을 초과하는 경우 테스트"""
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.parsed = None
    mock_message.refusal = None

    mock_choice = Mock(spec=Choice)
    mock_choice.message = mock_message
    mock_choice.finish_reason = "length"

    mock_completion = Mock(spec=ChatCompletion)
    mock_completion.choices = [mock_choice]

    with patch("openai.beta.chat.completions.parse", return_value=mock_completion):
        with pytest.raises(
            ValueError, match="Response was truncated due to length limit"
        ):
            client.get_response(
                question="매우 긴 질문",
                options=["보기1", "보기2", "보기3", "보기4", "보기5"],
            )


def test_content_filter(client):
    """콘텐츠 필터링이 발생하는 경우 테스트"""
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.parsed = None
    mock_message.refusal = None

    mock_choice = Mock(spec=Choice)
    mock_choice.message = mock_message
    mock_choice.finish_reason = "content_filter"

    mock_completion = Mock(spec=ChatCompletion)
    mock_completion.choices = [mock_choice]

    with patch("openai.beta.chat.completions.parse", return_value=mock_completion):
        with pytest.raises(
            ValueError, match="Response was filtered due to content policy"
        ):
            client.get_response(
                question="부적절한 내용의 질문",
                options=["보기1", "보기2", "보기3", "보기4", "보기5"],
            )


def test_api_error(client):
    """API 에러가 발생하는 경우 테스트"""
    mock_request = Mock()  # request 객체 모킹
    mock_request.method = "POST"
    mock_request.url = "https://api.openai.com/v1/chat/completions"
    mock_request.headers = {}
    mock_request.body = {}

    mock_body = {
        "error": {"message": "API 에러", "type": "api_error", "code": "error_code"}
    }

    with patch(
        "openai.beta.chat.completions.parse",
        side_effect=APIError(message="API 에러", request=mock_request, body=mock_body),
    ):
        with pytest.raises(ValueError, match="Error during OpenAI API call"):
            client.get_response(
                question="테스트 질문",
                options=["보기1", "보기2", "보기3", "보기4", "보기5"],
            )


def test_with_additional_data(client, mock_openai_response):
    """추가 데이터가 있는 경우 테스트"""
    additional_data = {"context": "추가 컨텍스트", "metadata": {"key": "value"}}

    with patch("openai.beta.chat.completions.parse", return_value=mock_openai_response):
        response = client.get_response(
            question="테스트 질문",
            options=["보기1", "보기2", "보기3", "보기4", "보기5"],
            data=additional_data,
        )

        assert isinstance(response, GPTResponse)
        assert response.selected_answer == "1"
        assert len(response.reasoning) == 5
