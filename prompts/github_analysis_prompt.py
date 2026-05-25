from langchain_core.prompts import ChatPromptTemplate

github_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI developer. Given the name and description of an open-source AI repository, concisely explain what it does and why developers care (max 2-3 sentences). Explain its relevance to the AI ecosystem. Generate 2-4 topic tags. Keep it developer-focused, high-signal, and avoid repetitive phrasing.\n\nLONGITUDINAL ANALYSIS:\nIf historical context is provided, explicitly compare today's development to the past events in your 'Why it matters' section to demonstrate trend evolution.\n\nCRITICAL GROUNDING CONSTRAINTS:\nOnly summarize information explicitly present in the provided repository description. Do NOT:\n- invent unrelated topics,\n- combine multiple repositories,\n- infer unsupported features,\n- introduce external tools not present in the text."),
    ("human", "Repository: {title}\n\nDescription: {content}\n\nHistorical Context:\n{history}")
])
