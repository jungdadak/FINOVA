import re


def clean_text_file(input_path, output_path):
    # 파일 읽기
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    # '-number-' 형식 제거
    cleaned_text = re.sub(r"- \d+ -", "", text)

    # 정제된 텍스트 저장
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(cleaned_text)

    print(f"텍스트 정제 완료. '{output_path}'에 저장되었습니다.")


# 파일 경로
input_path = "RAG/processed_재무보고를위한개념체계.txt"
output_path = (
    "../data/RAG/processed_재무보고를위한개념체계.txt"  # 새로운 파일명으로 저장
)

clean_text_file(input_path, output_path)
