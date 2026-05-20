import os
import time
from models.state import PipelineState
from graphs.newsletter_graph import create_newsletter_graph
from agents.composer import save_newsletter
from utils.logger import get_logger

logger = get_logger("orchestrator")

def main():
    start_time = time.time()
    logger.info("Starting AI Trend Intelligence Pipeline via LangGraph...")
    
    # Initialize the compiled LangGraph
    graph = create_newsletter_graph()
    initial_state = PipelineState()
    
    # Export Graph Visualization
    try:
        os.makedirs("artifacts", exist_ok=True)
        # Save raw Mermaid file
        with open("artifacts/graph.mmd", "w") as f:
            f.write(graph.get_graph().draw_mermaid())
        logger.info("Saved LangGraph Mermaid diagram to artifacts/graph.mmd")
        
        # Save PNG file if supported
        try:
            png_data = graph.get_graph().draw_mermaid_png()
            with open("artifacts/graph.png", "wb") as f:
                f.write(png_data)
            logger.info("Saved LangGraph PNG diagram to artifacts/graph.png")
        except Exception as png_e:
            logger.warning(f"Mermaid PNG export not supported or failed: {png_e}")
            
    except Exception as e:
        logger.warning(f"Could not generate graph visualization: {e}")
        
    # Execute the entire workflow automatically with a custom LangSmith trace name
    final_state_dict = graph.invoke(
        initial_state,
        config={"run_name": "AI Newsletter Agent"}
    )
    
    # Re-wrap into Pydantic model if LangGraph returns a raw dictionary
    if isinstance(final_state_dict, dict):
        final_state = PipelineState(**final_state_dict)
    else:
        final_state = final_state_dict
        
    final_state.metadata.execution_time_seconds = round(time.time() - start_time, 2)
    
    if final_state.final_newsletter:
        output_path = "output/newsletter.md"
        save_newsletter(final_state.final_newsletter, output_path)
        
        # Log final observability metrics
        logger.info(f"Pipeline completed successfully in {final_state.metadata.execution_time_seconds} seconds.")
        logger.info(f"Prompt Tokens: {final_state.metadata.total_prompt_tokens}")
        logger.info(f"Completion Tokens: {final_state.metadata.total_completion_tokens}")
        logger.info(f"Saved newsletter to {output_path}")
    else:
        logger.error("Pipeline finished but no final newsletter was generated.")

if __name__ == "__main__":
    main()
