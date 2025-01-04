import json
import re
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer


class KIFRSVectorizer:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def parse_toc(self, toc_text: str) -> Dict[str, List[str]]:
        """목차 텍스트를 파싱하여 챕터와 섹션 정보를 추출"""
        chapters = {}
        current_chapter = None

        # 목차 라인별 처리
        for line in toc_text.strip().split("\n"):
            if not line.strip():
                continue

            # 새로운 챕터 시작
            if line.startswith("제"):
                chapter_match = re.match(r"제(\d+)장\s+(.+)", line)
                if chapter_match:
                    current_chapter = line
                    chapters[current_chapter] = []
            # 섹션 처리
            elif current_chapter and re.match(r"\d+\.\d+", line):
                chapters[current_chapter].append(line)

        return chapters

    def create_section_mapping(self, chapters: Dict[str, List[str]]) -> Dict[str, str]:
        """섹션 번호와 전체 경로를 매핑"""
        section_mapping = {}

        for chapter, sections in chapters.items():
            for section in sections:
                section_num = re.match(r"(\d+\.\d+)", section).group(1)
                section_title = (
                    section[section.find(" ") + 1 :] if " " in section else section
                )
                full_path = f"{chapter} > {section_title}"
                section_mapping[section_num] = full_path

        return section_mapping

    def vectorize_sections(
        self, section_mapping: Dict[str, str]
    ) -> Dict[str, np.ndarray]:
        """섹션 텍스트를 벡터화"""
        vectors = {}
        for section_num, full_path in section_mapping.items():
            vectors[section_num] = self.model.encode(full_path)
        return vectors

    def process_content(self, content_path: str) -> Dict[str, str]:
        """문단 내용을 처리하여 문단번호-내용 매핑 생성"""
        with open(content_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 문단 패턴 매칭 (예: "1.1", "4.26" 등)
        pattern = r"(\d+\.\d+)\n(.*?)(?=\d+\.\d+\n|$)"
        matches = re.finditer(pattern, content, re.DOTALL)

        content_mapping = {}
        for match in matches:
            section_num = match.group(1)
            content_text = match.group(2).strip()
            content_mapping[section_num] = content_text

        return content_mapping

    def vectorize_content(
        self, content_mapping: Dict[str, str]
    ) -> Dict[str, np.ndarray]:
        """문단 내용을 벡터화"""
        vectors = {}
        for section_num, content in content_mapping.items():
            vectors[section_num] = self.model.encode(content)
        return vectors

    def save_vectors(
        self,
        section_vectors: Dict[str, np.ndarray],
        content_vectors: Dict[str, np.ndarray],
        section_mapping: Dict[str, str],
        output_dir: str = "vectors/",
    ):
        """벡터와 매핑 정보를 저장"""
        import os

        os.makedirs(output_dir, exist_ok=True)

        # 벡터 저장
        np.save(
            f"{output_dir}section_vectors.npy",
            {k: v.tolist() for k, v in section_vectors.items()},
        )
        np.save(
            f"{output_dir}content_vectors.npy",
            {k: v.tolist() for k, v in content_vectors.items()},
        )

        # 매핑 정보 저장
        with open(f"{output_dir}section_mapping.json", "w", encoding="utf-8") as f:
            json.dump(section_mapping, f, ensure_ascii=False, indent=2)


def main():
    # 초기화
    vectorizer = KIFRSVectorizer()

    # 목차 처리
    with open("RAG/label.txt", "r", encoding="utf-8") as f:
        toc_text = f.read()

    chapters = vectorizer.parse_toc(toc_text)
    section_mapping = vectorizer.create_section_mapping(chapters)
    section_vectors = vectorizer.vectorize_sections(section_mapping)

    # 문단 내용 처리
    content_mapping = vectorizer.process_content(
        "RAG/processed_재무보고를위한개념체계.txt"
    )
    content_vectors = vectorizer.vectorize_content(content_mapping)

    # 저장
    vectorizer.save_vectors(section_vectors, content_vectors, section_mapping)


if __name__ == "__main__":
    main()
