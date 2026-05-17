"""
Centralized Configuration for LLM Models.

Why centralized configuration is important:
1. Prevents hardcoding model names in multiple agent files, solving deprecation issues.
2. Future-proofs the architecture: makes it simple to switch to future providers (like OpenRouter, Gemini, Together AI) without modifying agent logic.
3. Allows different agents to route to different models based on their task (e.g., using a FAST_MODEL for simple extraction, and a REASONING_MODEL for complex analysis or evaluation).
"""

# Using the standard model IDs supported by Groq. 
# (If using OpenRouter later, you might prepend "meta-llama/")
FAST_MODEL = "llama-3.1-8b-instant"
REASONING_MODEL = "llama-3.3-70b-versatile"
