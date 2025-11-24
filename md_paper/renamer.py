import logging
import os
import re
from typing import List, Optional

from pypdf import PdfReader

from .crossref import crossrefInfo

logger = logging.getLogger("Renamer")
logger.setLevel(logging.INFO)

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
INVALID_FILENAME_CHARS = re.compile(r"[<>:\"/\\|?*\n\r\x00-\x1F\x7F']")


def normalize_doi(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return raw.rstrip(").,;").lower()


def extract_doi_from_pdf(pdf_path: str, max_pages: int = 5) -> Optional[str]:
    """Read up to ``max_pages`` pages from ``pdf_path`` and return the first DOI."""
    try:
        reader = PdfReader(pdf_path)
    except Exception as exc:
        logger.warning("Failed to read PDF %s: %s", pdf_path, exc)
        return None

    text_chunks: List[str] = []
    for page_index, page in enumerate(reader.pages[:max_pages]):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            logger.debug("Failed to extract text from page %s: %s", page_index, exc)
            text = ""
        text_chunks.append(text)

    if not text_chunks:
        return None

    content = "\n".join(text_chunks)
    match = DOI_PATTERN.search(content)
    if not match:
        return None

    return normalize_doi(match.group(0))


def sanitize_title_for_filename(title: str) -> str:
    provisional = "_".join(title.split()) or "paper"
    sanitized = INVALID_FILENAME_CHARS.sub("_", provisional)
    return sanitized or "paper"


def ensure_unique_path(path: str) -> str:
    base, ext = os.path.splitext(path)
    counter = 1
    candidate = path
    while os.path.exists(candidate):
        candidate = f"{base}_{counter}{ext}"
        counter += 1
    return candidate


def rename_pdfs_in_directory(pdf_dir: str, note_file: str, proxy: Optional[str] = None) -> None:
    if not os.path.isdir(pdf_dir):
        logger.error("PDF directory does not exist: %s", pdf_dir)
        return

    if os.path.isdir(note_file):
        logger.error("Provided Markdown path points to a directory: %s", note_file)
        return

    if not os.path.exists(note_file):
        note_parent = os.path.dirname(note_file)
        if note_parent and not os.path.isdir(note_parent):
            try:
                os.makedirs(note_parent, exist_ok=True)
            except Exception as exc:
                logger.error("Failed to create Markdown directory %s: %s", note_parent, exc)
                return
        try:
            with open(note_file, "w") as handle:
                handle.write("")
            logger.info("Created new Markdown file: %s", note_file)
        except Exception as exc:
            logger.error("Failed to create Markdown file %s: %s", note_file, exc)
            return

    client = crossrefInfo()
    if proxy:
        client.set_proxy(proxy)

    renamed_entries = []

    for name in sorted(os.listdir(pdf_dir)):
        if not name.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(pdf_dir, name)
        if not os.path.isfile(pdf_path):
            continue

        doi = extract_doi_from_pdf(pdf_path)
        if not doi:
            logger.warning("No DOI detected in %s", pdf_path)
            continue

        bib = client.get_info_by_doi(doi)
        if not bib:
            logger.warning("CrossRef returned no info for %s", doi)
            continue

        bib["doi"] = normalize_doi(doi)

        new_filename = sanitize_title_for_filename(bib["title"]) + ".pdf"
        new_path = ensure_unique_path(os.path.join(pdf_dir, new_filename))

        if new_filename == name:
            logger.info("File %s already matches naming convention, skipping", name)
            renamed_entries.append((bib, pdf_path))
            continue

        try:
            os.rename(pdf_path, new_path)
        except Exception as exc:
            logger.error("Failed to rename %s -> %s: %s", pdf_path, new_path, exc)
            continue

        renamed_entries.append((bib, new_path))
        logger.info("Renamed %s -> %s", os.path.basename(pdf_path), os.path.basename(new_path))

    if renamed_entries:
        append_metadata_to_note(note_file, renamed_entries)
    else:
        logger.info("No PDFs renamed, Markdown unchanged")


def append_metadata_to_note(note_file: str, entries: List[tuple]) -> None:
    note_dir = os.path.dirname(os.path.abspath(note_file)) or "."
    try:
        with open(note_file, "r") as handle:
            note_lines = handle.read().splitlines()
    except Exception as exc:
        logger.error("Failed to read Markdown file %s: %s", note_file, exc)
        return

    doi_index_map = {}
    for idx, line in enumerate(note_lines):
        match = DOI_PATTERN.search(line)
        if match:
            doi_in_note = normalize_doi(match.group(0))
            if doi_in_note:
                doi_index_map[doi_in_note] = idx

    appended_lines: List[str] = []
    replacements = 0

    for bib, pdf_path in entries:
        rel_path = os.path.relpath(pdf_path, note_dir)
        first_author = bib["author"].split(" and ")[0]
        venue = bib.get("venue_short") or bib.get("journal") or "Unknown venue"
        cited_count = bib.get("cited_count")
        citation_suffix = f" (citations: {cited_count})" if cited_count is not None else ""
        line = (
            f"- **{bib['title']}**. {first_author} et.al. **{venue}**, **{bib['year']}** "
            f"([pdf]({rel_path}))([link]({bib['url']})).{citation_suffix}"
        )

        doi_str = normalize_doi(bib.get("doi"))
        if not doi_str and bib.get("url"):
            match = DOI_PATTERN.search(bib["url"])
            if match:
                doi_str = normalize_doi(match.group(0))

        if doi_str and doi_str in doi_index_map:
            target_idx = doi_index_map[doi_str]
            note_lines[target_idx] = line
            replacements += 1
        else:
            appended_lines.append(line)

    if not replacements and not appended_lines:
        logger.info("No Markdown update needed, all entries already exist")
        return

    if appended_lines:
        if note_lines and note_lines[-1].strip():
            note_lines.append("")
        note_lines.extend(appended_lines)

    with open(note_file, "w") as handle:
        handle.write("\n".join(note_lines) + "\n")

    logger.info(
        "Markdown updated: replaced %s entries, appended %s entries",
        replacements,
        len(appended_lines),
    )
