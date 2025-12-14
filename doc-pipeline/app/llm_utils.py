import logging
import time
from typing import List

from openai import OpenAI

log = logging.getLogger(__name__)

TABLE_SYSTEM_PROMPT = (
    "You are a precise data-extraction assistant.\n"
    "You will receive a table in Markdown.\n"
    "Return a CLEAN, COMPACT, EMBEDDING-READY description in plain text.\n"
    "Absolutely NO markdown, NO bullet characters, NO pipes, NO table formatting.\n\n"
    "Grounding rules:\n"
    "- Only describe facts present in the table. Do NOT invent.\n"
    "- Preserve all numbers EXACTLY as written (including commas/decimals/signs).\n"
    "- Preserve units/currency exactly (€, %, million, etc.).\n"
    "- If something is unclear, write: 'Not specified in the table'.\n\n"
    "Formatting rules:\n"
    "- Output 1–6 short paragraphs of plain text.\n"
    "- Prefer semicolon-separated statements, e.g. 'Metric: value (year); ...'.\n"
    "- Do NOT include list markers like '-', '*', '•'.\n"
    "- Keep it compact.\n\n"
    "Content structure:\n"
    "1) What the table shows (topic + time period/years)\n"
    "2) Columns/years present\n"
    "3) Key rows/metrics with their values\n"
    "4) Any footnotes/notes found (verbatim, plain text)\n"
)


def _retry(fn, *, retries: int = 3, backoff: float = 1.5):
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            if i == retries - 1:
                raise
            sleep_s = backoff**i
            log.warning("LLM call failed (%s). Retrying in %.1fs...", e, sleep_s)
            time.sleep(sleep_s)


def describe_table(
    table_markdown: str, client: OpenAI, model: str, max_chars: int = 12000
) -> str:
    table_markdown = (table_markdown or "").strip()
    if not table_markdown:
        raise ValueError("describe_table: empty table")

    if len(table_markdown) > max_chars:
        table_markdown = table_markdown[:max_chars] + "\n\n[TRUNCATED]"

    def _call():
        resp = client.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": TABLE_SYSTEM_PROMPT},
                {"role": "user", "content": f"TABLE (Markdown):\n{table_markdown}"},
            ],
        )
        return resp.choices[0].message.content.strip()

    return _retry(_call)


def embed_text(text: str, client: OpenAI, model: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        raise ValueError("embed_text: empty text")

    def _call():
        resp = client.embeddings.create(
            model=model,
            input=text,
        )
        return resp.data[0].embedding

    return _retry(_call)
