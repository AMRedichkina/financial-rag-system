import logging
from pathlib import Path
from typing import Any, Dict

import ijson

from .llm_utils import describe_table, embed_text
from .neo4j_io import upsert_table_chunk, upsert_text_chunk
from .utils import (clean_table_text, clean_text, doc_id_from_chunk,
                    is_table_chunk_local, page_nos_from_chunk, table_ref)

log = logging.getLogger(__name__)


def process_text_chunk(
    ch: Dict[str, Any],
    doc_id: str,
    text_counter: int,
    *,
    client,
    embed_model: str,
    driver,
) -> None:
    text = clean_text(ch.get("text", ""))
    if not text:
        return
    meta = {
        "doc_id": doc_id,
        "chunk_id": f"{doc_id}::text::{text_counter}",
        "page_nos": page_nos_from_chunk(ch),
    }
    emb = embed_text(text, client=client, model=embed_model)
    upsert_text_chunk(
        driver=driver,
        doc_id=meta["doc_id"],
        chunk_id=meta["chunk_id"],
        text=text,
        embedding=emb,
        page_nos=meta.get("page_nos"),
    )


def process_table_block(
    parts,
    combined_md: str,
    *,
    client,
    chat_model: str,
    embed_model: str,
    driver,
) -> None:
    # parts[0]
    ref = table_ref(parts[0])
    all_pages = set()
    for p in parts:
        all_pages.update(page_nos_from_chunk(p))
    doc_id = doc_id_from_chunk(parts[0])
    meta = {
        "doc_id": doc_id,
        "chunk_id": f"{doc_id}::table::{ref.replace('#/tables/', '')}",
        "table_ref": ref,
        "page_nos": sorted(all_pages),
    }

    desc = describe_table(combined_md, client=client, model=chat_model)
    emb = embed_text(desc, client=client, model=embed_model)

    upsert_table_chunk(
        driver=driver,
        doc_id=meta["doc_id"],
        chunk_id=meta["chunk_id"],
        table_ref=meta["table_ref"],
        table_markdown=combined_md,
        table_description=desc,
        embedding=emb,
        page_nos=meta.get("page_nos"),
    )
    log.info("Saved table chunk %s (pages=%s)", meta["chunk_id"], meta.get("page_nos"))


def process_json_file(
    json_path: Path,
    *,
    client,
    chat_model: str,
    embed_model: str,
    driver,
) -> None:
    log.info("=== Processing: %s ===", json_path.name)
    with json_path.open("rb") as f:
        it = iter(ijson.items(f, "chunks.item"))
        text_counter = 0
        ch = next(it, None)
        while ch is not None:
            if is_table_chunk_local(ch):
                ref = table_ref(ch)
                parts = []
                texts = []
                while (
                    ch is not None and is_table_chunk_local(ch) and table_ref(ch) == ref
                ):
                    parts.append(ch)
                    texts.append(ch.get("text", "") or "")
                    ch = next(it, None)

                combined_table = clean_table_text(
                    "\n\n".join(t for t in texts if t.strip())
                )
                if combined_table and parts:
                    process_table_block(
                        parts,
                        combined_table,
                        client=client,
                        chat_model=chat_model,
                        embed_model=embed_model,
                        driver=driver,
                    )
                continue

            text_counter += 1
            doc_id = doc_id_from_chunk(ch)
            process_text_chunk(
                ch,
                doc_id,
                text_counter,
                client=client,
                embed_model=embed_model,
                driver=driver,
            )
            ch = next(it, None)

    log.info("=== Done: %s ===", json_path.name)


def process_all_jsons(
    data_root: Path,
    *,
    client,
    chat_model: str,
    embed_model: str,
    driver,
) -> None:
    json_files = sorted(data_root.rglob("*.chunks_md_tables.json"))
    if not json_files:
        raise FileNotFoundError(f"No *.chunks_md_tables.json found under: {data_root}")

    for p in json_files:
        process_json_file(
            p,
            client=client,
            chat_model=chat_model,
            embed_model=embed_model,
            driver=driver,
        )
