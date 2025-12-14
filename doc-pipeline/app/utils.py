from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def clean_text(s: str) -> str:
    s = (s or "").strip()
    return " ".join(s.split())  # collapse whitespace


def get_doc_items(ch: dict) -> list[dict]:
    return (ch.get("meta") or {}).get("doc_items") or []


def get_labels(ch: dict) -> list[str]:
    return [
        it.get("label") for it in get_doc_items(ch) if isinstance(it.get("label"), str)
    ]


def is_table_chunk_local(ch: dict) -> bool:
    return "table" in get_labels(ch)


def table_ref(ch: dict) -> str | None:
    for it in get_doc_items(ch):
        ref = it.get("self_ref")
        if isinstance(ref, str) and ref.startswith("#/tables/"):
            return ref
    return None


def clean_table_text(md: str) -> str:
    return md.strip()


def doc_id_from_chunk(ch: dict) -> str:
    origin = (ch.get("meta") or {}).get("origin") or {}
    return origin.get("filename") or "unknown_document"


def page_nos_from_chunk(ch: dict) -> list[int]:
    pages = set()
    doc_items = (ch.get("meta") or {}).get("doc_items") or []
    for it in doc_items:
        for prov in it.get("prov") or []:
            pn = prov.get("page_no")
            if isinstance(pn, int):
                pages.add(pn)
    return sorted(pages)
