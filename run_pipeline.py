import os
import time
from agents.retriever import retrieve_articles
from agents.ranker import rank_articles
from agents.analyzer import analyze_articles
from agents.composer import compose_newsletter, save_newsletter
from agents.evaluator import evaluate_newsletter
from utils.logger import get_logger

logger = get_logger("orchestrator")

def main():
    start_time = time.time()
    logger.info("Starting AI Trend Intelligence Pipeline...")
    
    # Step 1: Retriever
    state = retrieve_articles()
    
    if state.metadata.total_articles_retrieved == 0:
        logger.warning("Pipeline stopped: No articles retrieved.")
        return

    # Step 2: Ranker
    state = rank_articles(state)

    # Step 3: Analyzer
    state = analyze_articles(state)
    
    # Step 4: Evaluator (Quality Control)
    state = evaluate_newsletter(state)
    
    # Finalize Metadata before Composer
    state.metadata.execution_time_seconds = round(time.time() - start_time, 2)
    
    # Step 5: Composer
    markdown_content = compose_newsletter(state)
    
    # Step 6: Save Output
    output_path = "output/newsletter.md"
    save_newsletter(markdown_content, output_path)
    logger.info(f"Pipeline completed successfully in {state.metadata.execution_time_seconds} seconds.")
    logger.info(f"Saved newsletter to {output_path}")

if __name__ == "__main__":
    main()
