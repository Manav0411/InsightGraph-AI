import os
from agents.retriever import retrieve_articles
from agents.analyzer import analyze_articles
from agents.composer import compose_newsletter, save_newsletter
from agents.evaluator import evaluate_newsletter

def main():
    print("Starting AI Trend Intelligence Pipeline...\n")
    
    # Step 1: Retriever
    retrieved_data = retrieve_articles()
    num_articles = len(retrieved_data.get("articles", []))
    print(f"✓ Retrieved {num_articles} articles\n")
    
    if num_articles == 0:
        print("Pipeline stopped: No articles retrieved.")
        return

    # Step 2: Analyzer
    analyzed_data = analyze_articles(retrieved_data)
    print("\n✓ Generated summaries\n")
    
    # Step 3: Evaluator (Basic validation step)
    evaluate_newsletter(analyzed_data)
    
    # Step 4: Composer
    markdown_content = compose_newsletter(analyzed_data)
    print("\n✓ Created newsletter\n")
    
    # Step 5: Save Output
    output_path = "output/newsletter.md"
    save_newsletter(markdown_content, output_path)
    print(f"✓ Saved newsletter to {output_path}\n")

if __name__ == "__main__":
    main()
