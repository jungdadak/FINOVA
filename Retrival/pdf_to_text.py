import fitz  # PyMuPDF의 모듈명은 'fitz'입니다.


def extract_text_from_pdf(pdf_path, output_txt_path):
    # PDF 파일 열기
    pdf_document = fitz.open(pdf_path)
    all_text = ""

    # 각 페이지 순회하며 텍스트 추출
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        all_text += text

    # 추출한 텍스트를 텍스트 파일로 저장
    with open(output_txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(all_text)

    print(f"텍스트 추출 완료. '{output_txt_path}'에 저장되었습니다.")


pdf_path = "/Users/junghyeon/Downloads/시행중_K-IFRS_재무보고를_위한_개념체계(2018_개정_2019_타기준서_개정_수정목록_24-1_2020_구성양식_변경_반영).pdf"  # PDF 파일 경로
output_txt_path = "RAG/재무보고를위한개념체계.txt"

extract_text_from_pdf(pdf_path, output_txt_path)
