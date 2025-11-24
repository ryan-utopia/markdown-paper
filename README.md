# md-paper

> English | [中文](./README_zh.md)

**md-paper** is a lightweight command-line tool to help you manage literature notes written in Markdown.  
It is inspired by [Mu Li](https://www.bilibili.com/video/BV1nA41157y4) and is a modified version of [autoLiterature](https://github.com/WilmerWang/autoLiterature), focusing on a smoother Markdown workflow.

Best practice: use it together with Typora and configure Typora to use **relative paths** for images and file links.

Finally, place your literature and Markdown notes in the same folder, and use LLMs and Agents like Copilot to read and summarize the literature for better results.

## Features

### 1. Start from Markdown notes: fetch metadata and PDFs

md-paper scans your Markdown file(s) and automatically recognizes paper IDs, then:

- updates the metadata of papers in your notes;
- optionally downloads the corresponding PDFs.

**Syntax rules:**

- Automatically recognizes list items like: `- {xxx}`.
- When a note line contains `- {paper_id}`, md-paper updates the paper metadata in the note, **without downloading PDF**.
- When a note line contains `- {{paper_id}}`, md-paper updates both the paper metadata **and downloads the PDF**.

Supported `paper_id` types:

- Published papers: `doi`
- Preprints: `arxiv_id`, `biorxiv_id`, `medrxiv_id` (note the spelling)

Basic usage:

```bash
md-paper -i <note-file-or-folder> [-o <output-folder>] [-p <proxy>]
```

- `-i` / `--input` : path to a single Markdown note file or a folder containing multiple notes.
- `-o` / `--output`: target folder to save downloaded PDFs and images (must be a folder).
- `-p` / `--proxy` : HTTP proxy, e.g. `127.0.0.1:7890`.

### 2. Start from PDFs: rename and write back metadata to Markdown

If some papers cannot be fetched directly (e.g. sci-hub unavailable, access behind authentication),  
you can download the PDFs manually, then let md-paper:

1. extract DOI from the first pages of each PDF;
2. query CrossRef for title / authors / venue / citation count;
3. rename the PDF to `Title.pdf`;
4. append or update the corresponding entry in your Markdown note.

Usage:

```bash
md-paper -i <note-file> -r <pdf-folder> [-p <proxy>]
```

- `-i` / `--input`  : Markdown file where entries will be added or updated.
- `-r` / `--rename` : folder containing PDFs to be processed.
- `-p` / `--proxy`  : HTTP proxy used for CrossRef.

If a PDF does not contain a detectable DOI, or CrossRef returns no result,  
md-paper logs a warning and **skips** renaming for that file.

## Installation

### 1. Install from PyPI

```bash
pip install markdown-paper
# or
pip3 install markdown-paper
```

### 2. Install from source

```bash
git clone https://github.com/ryan-utopia/markdown-paper.git
cd markdown-paper
python setup.py install
```

## Command-line options

```bash
md-paper

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The path to the note file or note file folder.
  -o OUTPUT, --output OUTPUT
                        The folder path to save paper pdfs and images. NOTE: MUST BE FOLDER
  -r RENAME, --rename RENAME
                        The folder path that contains pdfs to be renamed.
  -p PROXY, --proxy PROXY
                        The proxy. e.g. 127.0.0.1:7890
```

## License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.
