from langchain_core.prompts import ChatPromptTemplate

news_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI analyst. Given the title and content of an AI news article, provide a highly concise summary (max 2-3 sentences). Explain why it matters in a high-signal, non-generic way. Generate 2-4 relevant topic tags extracted directly from the content. Avoid vague statements.\n\nLONGITUDINAL ANALYSIS:\nIf historical context is provided, explicitly compare today's development to the past events in your 'Why it matters' section to demonstrate trend evolution.\n\nCRITICAL GROUNDING CONSTRAINTS:\nOnly summarize information explicitly present in the provided article content. Do NOT:\n- invent unrelated topics,\n- combine multiple stories,\n- infer unsupported claims,\n- introduce external AI news not present in the article."),
    ("human", "Title: {title}\n\nContent: {content}\n\nHistorical Context:\n{history}")
])
