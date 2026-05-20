from langchain_core.prompts import ChatPromptTemplate

github_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI developer. Given the name and description of an open-source AI repository, concisely explain what it does and why developers care (max 2-3 sentences). Explain its relevance to the AI ecosystem. Generate 2-4 topic tags. Keep it developer-focused, high-signal, and avoid repetitive phrasing."),
    ("human", "Repository: {title}\n\nDescription: {content}")
])
