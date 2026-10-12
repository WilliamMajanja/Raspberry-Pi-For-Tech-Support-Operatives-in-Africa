# Download the book

- [PDF edition](Raspberry-Pi-for-Technical-Support-Operatives-in-Africa.pdf) — print-friendly A4 pages with a linked contents list.
- [EPUB edition](Raspberry-Pi-for-Technical-Support-Operatives-in-Africa.epub) — reflowable text with navigation for e-readers.
- [Cover artwork](cover.png) — the Coffee Pot Snake ASCII illustration and book title.

Both files are generated from the Markdown pages linked by `SUMMARY.md`; unreviewed legacy article files are not included as chapters. Cross-references between included pages are retained as links.

## Rebuild

Reading the source book requires no software beyond a Markdown-capable viewer. To regenerate the downloadable editions, install Python 3.10 or newer, Pandoc, and Chromium, then run from the repository root:

```bash
python3 tools/build_books.py
```

Pandoc creates the EPUB and HTML. Chromium prints the HTML to PDF. The optional build tooling does not add dependencies to the book itself.
