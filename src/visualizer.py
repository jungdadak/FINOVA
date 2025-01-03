# src/visualizer.py
from pathlib import Path
import logging
from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.font_manager as fm
from src.config import settings
from src.models import ComparisonResult, ExamResult

logger = logging.getLogger(__name__)

plt.rcParams['font.family'] = 'AppleGothic'  # Mac의 경우
# plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우

class Visualizer:
    def __init__(self, output_dir: Path = settings.output_dir):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Visualizer initialized with output_dir: {self.output_dir}")

    def generate_exam_summary(self, results: List[ExamResult]):
        """Generate overall summary of exam results."""
        logger.info("Generating exam summary")

        summary_data = {
            'Exam Name': [],
            'Total Questions': [],
            'Correct Answers': [],
            'Accuracy': [],
            'Total Time (s)': [],
            'Average Time per Question (s)': []
        }

        for result in results:
            summary_data['Exam Name'].append(result.exam_name)
            summary_data['Total Questions'].append(result.total_questions)
            summary_data['Correct Answers'].append(result.correct_answers)
            summary_data['Accuracy'].append(result.accuracy)
            summary_data['Total Time (s)'].append(result.execution_time)
            summary_data['Average Time per Question (s)'].append(
                result.execution_time / result.total_questions if result.total_questions > 0 else 0
            )

        df = pd.DataFrame(summary_data)
        summary_path = self.output_dir / 'exam_summary.csv'
        df.to_csv(summary_path, index=False)
        logger.info(f"Exam summary saved to {summary_path}")

    def generate_timing_visualization(self, results: List[ExamResult]):
        """Generate visualizations for timing analysis."""
        logger.info("Generating timing visualizations")

        # Prepare data for plotting
        timing_data = {
            'Exam': [],
            'Question': [],
            'Time (s)': [],
            'Correct': []
        }

        for exam_result in results:
            for q_result in exam_result.questions_results:
                timing_data['Exam'].append(exam_result.exam_name)
                timing_data['Question'].append(q_result.question_id)
                timing_data['Time (s)'].append(q_result.execution_time)
                timing_data['Correct'].append(q_result.is_correct)

        df = pd.DataFrame(timing_data)

        # 1. Question timing distribution per exam
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='Exam', y='Time (s)')
        plt.xticks(rotation=45)
        plt.title('Question Timing Distribution by Exam')
        timing_boxplot_path = self.output_dir / 'timing_distribution.png'
        plt.tight_layout()
        plt.savefig(timing_boxplot_path)
        plt.close()

        # 2. Time vs Correctness
        plt.figure(figsize=(10, 6))
        sns.violinplot(data=df, x='Correct', y='Time (s)')
        plt.title('Time Distribution vs Correctness')
        timing_violin_path = self.output_dir / 'timing_vs_correctness.png'
        plt.tight_layout()
        plt.savefig(timing_violin_path)
        plt.close()

        # 3. Question timing heatmap
        plt.figure(figsize=(15, 8))
        timing_matrix = df.pivot_table(
            index='Exam',
            columns='Question',
            values='Time (s)',
            aggfunc='mean'
        )
        sns.heatmap(timing_matrix, annot=True, fmt='.1f', cmap='YlOrRd')
        plt.title('Question Timing Heatmap')
        timing_heatmap_path = self.output_dir / 'timing_heatmap.png'
        plt.tight_layout()
        plt.savefig(timing_heatmap_path)
        plt.close()

        logger.info(f"Timing visualizations saved to {self.output_dir}")

    def generate_score_visualization(self, results: List[ExamResult]):
        """Generate score distribution visualization."""
        logger.info("Generating score visualizations")

        for exam_result in results:
            correct_count = exam_result.correct_answers
            total = exam_result.total_questions
            incorrect = total - correct_count

            labels = ["Correct", "Incorrect"]
            sizes = [correct_count, incorrect]
            colors = ["#4CAF50", "#F44336"]
            explode = (0.1, 0)

            plt.figure(figsize=(8, 8))
            plt.pie(
                sizes,
                explode=explode,
                labels=labels,
                colors=colors,
                autopct="%1.1f%%",
                shadow=True,
                startangle=140,
            )
            plt.title(f"Score Distribution for {exam_result.exam_name}")
            plt.axis("equal")

            pie_chart_path = self.output_dir / f"{exam_result.exam_name}_score_pie_chart.png"
            plt.savefig(pie_chart_path)
            plt.close()

        logger.info("Score visualizations completed")

    def generate_corrections_table(self, results: List[ExamResult]):
        """Generate corrections table for incorrect answers."""
        logger.info("Generating corrections table")

        for exam_result in results:
            corrections = [
                {
                    "Question ID": result.question_id,
                    "Selected Answer": result.selected_answer,
                    "Time Taken (s)": result.execution_time,
                    "Reasoning": " | ".join(result.reasoning),
                }
                for result in exam_result.questions_results if not result.is_correct
            ]

            if corrections:
                df = pd.DataFrame(corrections)
                corrections_path = self.output_dir / f"{exam_result.exam_name}_corrections.csv"
                df.to_csv(corrections_path, index=False)
                logger.info(f"Corrections table saved at: {corrections_path}")
            else:
                logger.info(f"No corrections needed for exam: {exam_result.exam_name}")