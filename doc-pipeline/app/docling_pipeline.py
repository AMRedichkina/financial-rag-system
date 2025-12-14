import json
import logging
from pathlib import Path
from typing import List, Tuple

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hierarchical_chunker import (
    ChunkingDocSerializer, ChunkingSerializerProvider)
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import \
    HuggingFaceTokenizer
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer
from transformers import AutoTokenizer

log = logging.getLogger(__name__)


def build_docling_converter_and_chunker(
    embed_model_id: str,
) -> Tuple[DocumentConverter, HybridChunker]:
    opts = PdfPipelineOptions()
    opts.do_ocr = False
    opts.do_table_structure = True
    opts.table_structure_options.do_cell_matching = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )

    class MDTableSerializerProvider(ChunkingSerializerProvider):
        def get_serializer(self, doc):
            return ChunkingDocSerializer(
                doc=doc,
                table_serializer=MarkdownTableSerializer(),
            )

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(embed_model_id)
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        serializer_provider=MDTableSerializerProvider(),
    )
    return converter, chunker


def pdf_to_chunks_json(
    pdf_path: str | Path,
    converter,
    chunker,
    overwrite: bool = False,
    out_dir: Path | None = None,
) -> Path:
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (pdf_path.stem + ".chunks_md_tables.json")
    else:
        out_path = pdf_path.with_suffix(".chunks_md_tables.json")

    if out_path.exists() and not overwrite:
        log.info("Skip (exists): %s", out_path.name)
        return out_path

    dl_doc = converter.convert(str(pdf_path)).document

    chunks = []
    for ch in chunker.chunk(dl_doc=dl_doc):
        text = chunker.contextualize(chunk=ch)  # tables -> Markdown
        meta = ch.meta.model_dump() if hasattr(ch, "meta") else None
        chunks.append({"text": text, "meta": meta})

    out_path.write_text(
        json.dumps({"chunks": chunks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info("Wrote: %s", out_path)
    return out_path


def build_json_for_all_pdfs(
    data_root: Path,
    embed_model_id: str,
    overwrite: bool = False,
    out_dir: Path | None = None,
):
    pdf_files = sorted(data_root.rglob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found under: {data_root}")

    converter, chunker = build_docling_converter_and_chunker(embed_model_id)
    outs: List[Path] = []
    for pdf in pdf_files:
        try:
            outs.append(
                pdf_to_chunks_json(
                    pdf, converter, chunker, overwrite=overwrite, out_dir=out_dir
                )
            )
        except Exception as e:
            log.exception("ERROR processing %s: %s", pdf, e)
    return outs
