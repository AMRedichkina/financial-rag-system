import argparse
import logging
from pathlib import Path

from openai import OpenAI

from .config import settings
from .docling_pipeline import build_json_for_all_pdfs
from .indexes import create_vector_indexes
from .logging_conf import setup_logging
from .neo4j_io import ensure_constraints, make_driver
from .process_json import process_all_jsons


def main():
    setup_logging(logging.INFO)
    parser = argparse.ArgumentParser(
        prog="doc-pipeline",
        description="PDF -> chunks JSON -> embeddings -> Neo4j with vector indexes",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1) convert PDFs to chunks json
    p_convert = sub.add_parser(
        "convert", help="Convert all PDFs under --pdf-dir to *.chunks_md_tables.json"
    )
    p_convert.add_argument(
        "--pdf-dir", type=Path, required=True, help="Root directory with PDFs"
    )
    p_convert.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing *.json"
    )
    p_convert.add_argument(
        "--out-dir", type=Path, default=None, help="Directory to store JSON chunks"
    )

    # 2) ingest (JSON -> Neo4j)
    p_ingest = sub.add_parser(
        "ingest", help="Process all *.chunks_md_tables.json and write to Neo4j"
    )
    p_ingest.add_argument(
        "--json-dir",
        type=Path,
        required=True,
        help="Root directory with *.chunks_md_tables.json",
    )

    # 3) full (convert + ingest)
    p_full = sub.add_parser("full", help="Run convert + ingest")
    p_full.add_argument("--pdf-dir", type=Path, required=True)
    p_full.add_argument("--overwrite", action="store_true")

    # 4) indexes
    p_index = sub.add_parser("indexes", help="Create vector indexes and tag brands")

    args = parser.parse_args()

    # clients
    client = OpenAI(api_key=settings.openai_api_key)
    driver = make_driver(
        settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
    )
    ensure_constraints(driver)

    if args.cmd == "convert":
        build_json_for_all_pdfs(
            data_root=args.pdf_dir,
            embed_model_id=settings.doc_embed_tokenizer,
            overwrite=args.overwrite,
            out_dir=args.out_dir,
        )

    elif args.cmd == "ingest":
        process_all_jsons(
            args.json_dir,
            client=client,
            chat_model=settings.chat_model,
            embed_model=settings.embed_model,
            driver=driver,
        )

    elif args.cmd == "full":
        build_json_for_all_pdfs(
            args.pdf_dir, settings.doc_embed_tokenizer, overwrite=args.overwrite
        )
        process_all_jsons(
            args.pdf_dir,
            client=client,
            chat_model=settings.chat_model,
            embed_model=settings.embed_model,
            driver=driver,
        )

    elif args.cmd == "indexes":
        create_vector_indexes(driver)

    driver.close()


if __name__ == "__main__":
    main()
