import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class TextStats:
    total_chars: int
    chars_no_space: int
    korean_chars: int
    english_chars: int
    numbers: int
    spaces: int
    lines: int
    words: int


class TextComparator:
    def __init__(self, file1_path: str, file2_path: str):
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.file1_content = self._read_file(file1_path)
        self.file2_content = self._read_file(file2_path)

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_text_stats(self, text: str) -> TextStats:
        return TextStats(
            total_chars=len(text),
            chars_no_space=len(
                text.replace(" ", "").replace("\n", "").replace("\t", "")
            ),
            korean_chars=len(re.findall("[가-힣]", text)),
            english_chars=len(re.findall("[a-zA-Z]", text)),
            numbers=len(re.findall("[0-9]", text)),
            spaces=len(re.findall("[\s]", text)),
            lines=len(text.splitlines()),
            words=len(re.findall(r"\S+", text)),
        )

    def compare_files(self) -> Dict:
        stats1 = self.get_text_stats(self.file1_content)
        stats2 = self.get_text_stats(self.file2_content)

        d = difflib.Differ()
        diff = list(
            d.compare(self.file1_content.splitlines(), self.file2_content.splitlines())
        )

        changes = {
            "added": len([line for line in diff if line.startswith("+ ")]),
            "removed": len([line for line in diff if line.startswith("- ")]),
            "changed": len([line for line in diff if line.startswith("? ")]),
        }

        return {
            "file1_name": Path(self.file1_path).name,
            "file2_name": Path(self.file2_path).name,
            "file1_stats": stats1,
            "file2_stats": stats2,
            "changes": changes,
        }


def format_simple_comparison(comparison: Dict) -> str:
    result = []
    for i, (file_name, stats) in enumerate(
        [
            (comparison["file1_name"], comparison["file1_stats"]),
            (comparison["file2_name"], comparison["file2_stats"]),
        ],
        1,
    ):
        result.append(f"File {i}: {file_name}")
        result.append(f"Lines: {stats.lines}")
        result.append(f"Total chars: {stats.total_chars}")
        result.append(f"Chars without spaces: {stats.chars_no_space}")
        result.append("")

    result.append(f"Added lines: {comparison['changes']['added']}")
    result.append(f"Removed lines: {comparison['changes']['removed']}")
    result.append(f"Changed lines: {comparison['changes']['changed']}")

    return "\n".join(result)


if __name__ == "__main__":
    file1_path = "RAG/재무보고를위한개념체계.txt"
    file2_path = "RAG/processed_재무보고를위한개념체계.txt"

    comparator = TextComparator(file1_path, file2_path)
    comparison = comparator.compare_files()
    print(format_simple_comparison(comparison))
