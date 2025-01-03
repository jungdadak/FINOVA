# main.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from src.data_loader import DataLoader
from src.openai_client import OpenAIClient
from src.processor import Processor
from src.visualizer import Visualizer


def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"app_{timestamp}.log"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10 ** 6, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def process_single_exam(exam_name: str = None, start_num: int = None, end_num: int = None):
    logger = logging.getLogger(__name__)

    data_loader = DataLoader()
    openai_client = OpenAIClient()
    processor = Processor(data_loader, openai_client)
    visualizer = Visualizer()

    try:
        # Process exam
        result = processor.process_exam(exam_name, start_num, end_num)
        if result:
            results = [result]  # Wrap single result in list for visualizer

            # Generate visualizations
            visualizer.generate_exam_summary(results)
            visualizer.generate_timing_visualization(results)
            visualizer.generate_score_visualization(results)
            visualizer.generate_corrections_table(results)

            logger.info(f"Processing complete for exam '{exam_name}'")
            logger.info(f"Accuracy: {result.accuracy:.2%}")
            logger.info(f"Total time: {result.execution_time:.2f} seconds")
            logger.info(f"Output directory: '{visualizer.output_dir}'")
    except Exception as e:
        logger.error(f"An error occurred during exam processing: {e}", exc_info=True)


def process_all_exams():
    logger = logging.getLogger(__name__)

    data_loader = DataLoader()
    openai_client = OpenAIClient()
    processor = Processor(data_loader, openai_client)
    visualizer = Visualizer()

    try:
        # Process all exams
        results = processor.process_all_exams()

        # Generate visualizations
        visualizer.generate_exam_summary(results)
        visualizer.generate_timing_visualization(results)
        visualizer.generate_score_visualization(results)
        visualizer.generate_corrections_table(results)

        logger.info(f"Processing complete for all exams")
        logger.info(f"Total exams processed: {len(results)}")
        logger.info(f"Output directory: '{visualizer.output_dir}'")
    except Exception as e:
        logger.error(f"An error occurred during exam processing: {e}", exc_info=True)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Program started")

    # 모든 시험을 처리하려면:
    # process_all_exams()

    # 특정 시험만 처리하려면:
    process_single_exam(
        exam_name="2023_1형",
        start_num=1,  # Optional: 시작 문제 번호
        end_num=10  # Optional: 끝 문제 번호
    )

    logger.info("Program completed")


if __name__ == "__main__":
    main()