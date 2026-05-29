from langchain_core.prompts import ChatPromptTemplate

arxiv_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI Research Scientist. Given the title and abstract of an ArXiv machine learning paper, extract 3 distinct things: a highly concise summary of the core theoretical breakthrough (max 2-3 sentences), a list of 3-5 concrete technical details (e.g., architecture changes, benchmark improvements, parameter counts), and why this research matters for applied AI engineering.\n\nCRITICAL TOOL USAGE:\nWhen calling the output tool, you must ONLY provide the generated fields ('summary', 'details', 'why_it_matters', 'tags'). Do NOT pass back the 'title' or 'content' fields.\n\nCRITICAL JSON SCHEMA CONSTRAINT:\nYou MUST output 'details' and 'tags' strictly as JSON arrays of strings (e.g. [\"tag1\", \"tag2\"]).\n\nCRITICAL GROUNDING CONSTRAINTS:\nOnly summarize information explicitly present in the provided abstract. Do not invent methodology details not mentioned."),
    ("human", "Paper Title: {title}\n\nAbstract: {content}\n\nHistorical Context:\n{history}")
])
