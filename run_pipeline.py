import os
import time
from models.state import PipelineState
from graphs.newsletter_graph import create_newsletter_graph
from agents.composer import save_newsletter
from utils.logger import get_logger
from utils.user_loader import load_user_profile

logger = get_logger("orchestrator")

def main():
    start_time = time.time()
    logger.info("Starting AI Trend Intelligence Pipeline via LangGraph...")
    
    # Load user profile for personalization
    user_id = "manav"
    user_profile = load_user_profile(user_id)
    
    # Initialize the compiled LangGraph
    graph = create_newsletter_graph()
    initial_state = PipelineState(user_profile=user_profile)
    
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
        logger.info(f"Pipeline completed in {final_state.metadata.execution_time_seconds} seconds.")
        logger.info(f"Recovery Attempts Triggered: {final_state.metadata.recovery_attempts}")
        logger.info(f"Conditional Routes Traversed: {final_state.metadata.conditional_routes_triggered}")
        logger.info(f"Total Articles Rejected: {final_state.metadata.total_articles_rejected}")
        logger.info(f"Prompt Tokens: {final_state.metadata.total_prompt_tokens}")
        logger.info(f"Completion Tokens: {final_state.metadata.total_completion_tokens}")
        
        # Print personalization stats
        if final_state.metadata.generated_for_user:
            logger.info(f"Personalization Stats:")
            logger.info(f"  - Generated for User: {final_state.metadata.generated_for_user}")
            logger.info(f"  - Personalization Boosts/Penalties Applied: {final_state.metadata.personalization_boosts_applied}")
            
        logger.info(f"Saved newsletter to {output_path}")
    else:
        logger.error("Pipeline finished but no final newsletter was generated.")

if __name__ == "__main__":
    main()

