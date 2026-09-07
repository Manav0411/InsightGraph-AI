import time
import os
import re
import asyncio
from typing import Tuple
from langchain_groq import ChatGroq
from config.models import FAST_MODEL
from models.state import PipelineState, Article
from utils.logger import get_logger

logger = get_logger("validator")

# gpt-oss models on Groq are unreliable with tool-calling / structured output for
# a trivial boolean (they emit a differently-cased tool name that Groq rejects).
# A plain YES/NO text prompt is robust and much cheaper.

_YES = re.compile(r"\byes\b", re.IGNORECASE)
_NO = re.compile(r"\bno\b", re.IGNORECASE)


def _build_prompt(article: Article) -> str:
    if article.source == "hacker_news":
        return (
            "You are a strict content moderator. Is the following Hacker News post genuinely "
            "about Artificial Intelligence, Machine Learning, or LLMs?\n\n"
            f"Title: {article.title}\n\n"
            "Answer with exactly one word: YES or NO."
        )
    return (
        "You are a strict content moderator. Does the article content below genuinely match "
        "its title, or is it clickbait / unrelated noise?\n\n"
        f"Title: {article.title}\n"
        f"Content snippet (first 300 chars): {article.content[:300]}\n\n"
        "Answer with exactly one word: YES (content is relevant and on-topic) or NO."
    )


def _parse_relevance(text: str) -> bool:
    """Lenient parse: default to keeping the article unless the model clearly says NO."""
    if not text:
        return True
    head = text.strip()[:20]
    if _NO.search(head) and not _YES.search(head):
        return False
    return True


async def _validate_single_article(llm: ChatGroq, article: Article, sem: asyncio.Semaphore) -> Tuple[Article, bool]:
    # Editorial sources are pre-vetted; skip the LLM call entirely.
    if article.source in ["arxiv", "rss"]:
        return article, True

    prompt = _build_prompt(article)

    # Validation is a cheap best-effort firewall. It must not burn rate-limit
    # budget the analyzer needs, so on ANY rate limit we fail open immediately
    # (one short retry only if the API hands back a small explicit wait).
    async with sem:
        for attempt in range(2):
            try:
                response = await llm.ainvoke(prompt)
                return article, _parse_relevance(getattr(response, "content", "") or "")
            except Exception as e:
                err_msg = str(e)
                is_rate_limit = "429" in err_msg or "rate_limit" in err_msg
                wait_match = re.search(r"try again in (\d+\.?\d*)s", err_msg)
                if is_rate_limit and attempt == 0 and wait_match and float(wait_match.group(1)) <= 5:
                    await asyncio.sleep(float(wait_match.group(1)) + 0.5)
                    continue
                if not is_rate_limit:
                    logger.warning(f"[Validator] Check failed for '{article.title}', keeping it: {e}")
                return article, True

        return article, True


async def validate_articles(state: PipelineState) -> PipelineState:
    """
    Filters out noisy or off-topic articles using a fast YES/NO LLM check run in parallel.
    Fails open: an article is only dropped on an explicit NO.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "validation"
    logger.info("Validating retrieved articles for grounding using FAST_MODEL...")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("No GROQ_API_KEY found, bypassing LLM validation.")
        return state

    llm = ChatGroq(model=FAST_MODEL, temperature=0.0, max_tokens=8, api_key=api_key)

    sem = asyncio.Semaphore(2)
    tasks = [_validate_single_article(llm, article, sem) for article in state.articles]
    results = await asyncio.gather(*tasks)

    valid_articles = []
    for article, is_relevant in results:
        if is_relevant:
            article.grounding_verified = True
            valid_articles.append(article)
        else:
            logger.warning(f"[Validator] Rejected article due to low title-content relevance: '{article.title}'")
            state.metadata.total_articles_rejected += 1
            state.metadata.validation_failures += 1

    total_articles = len(state.articles)
    state.articles = valid_articles

    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["validator"] = elapsed_time

    logger.info(f"[Validator] Validated {len(valid_articles)}/{total_articles} articles.")
    logger.info(f"[Validator] Completed in {elapsed_time}s")

    return state
