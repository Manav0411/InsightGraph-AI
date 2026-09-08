# Pipeline tuning constants.

# --- Retrieval ---
MAX_ARTICLES_PER_SOURCE = 10
TAVILY_DAYS_BACK = 7
HACKER_NEWS_DAYS_BACK = 3
ARXIV_MAX_RESULTS = 10
RSS_MAX_RESULTS_PER_FEED = 3

# --- Ranking / selection ---
# Analyze only slightly more than we ship so we don't burn LLM calls on articles
# the evaluator will trim away.
MAX_ARTICLES_TO_ANALYZE = 12
TARGET_FINAL_ARTICLES = 10
# Only trigger a (costly) retrieval+re-analysis recovery lap if the briefing
# would otherwise be genuinely thin. A run with 6-9 solid articles just ships.
MIN_VIABLE_ARTICLES = 6
MIN_TREND_SCORE = 1.0

# --- Analyzer ---
MAX_CONTENT_LENGTH = 1500
MAX_OUTPUT_TOKENS = 1024
RETRY_DELAY_SECONDS = 8
MAX_RETRIES = 5
# gpt-oss models have far higher request-rate limits than the old Llama free
# tier, so the per-article pause can be short.
ANALYSIS_THROTTLE_SECONDS = 1

# --- Evaluator ---
MIN_SUMMARY_WORDS = 10
