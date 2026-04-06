"""
build_corpus.py — IMDB review corpus builder for LexiAI
=========================================================
Reads movie-review text from the local IMDB Dataset.csv (Kaggle-style),
cleans and tokenizes it, then saves corpus.json for corpus.py and gui_app.py.

No network required.

Run once:
    python build_corpus.py

Optional env:
  CORPUS_CSV_PATH       - path to CSV (default: ../IMDB Dataset.csv)
  CORPUS_MAX_REVIEWS    - cap number of reviews kept (default: none = whole file)
  CORPUS_MAX_WORDS      - cap total tokens (default: none = whole file)

Then run the app as normal:
    python gui_app.py

Requirements: Python 3.8+ (uses only standard library)
"""

import csv
import json
import re
import os
from collections import Counter

# ── Resource Limits
MAX_TEXT_LENGTH = 100000
MAX_ABSTRACT_STORE = MAX_TEXT_LENGTH  # validation upper bound (IMDB reviews can be long)
_LATEX_REGEX = re.compile(r'\\[a-z]+\{[^}]*?\}', re.DOTALL)
_MATH_REGEX = re.compile(r'\$[^$]*?\$', re.DOTALL)
_URL_REGEX = re.compile(r'https?://\S+')
_SPECIAL_REGEX = re.compile(r'[^a-z\s\'-]')
_HTML_TAG_REGEX = re.compile(r"<[^>]+>")

# ── Configuration ─────────────────────────────────────────────────────────────

OUTPUT_FILE     = "corpus.json"
MIN_REVIEW_CHARS = 100     # skip very short reviews (after HTML strip)
PROGRESS_EVERY   = 2000    # print progress every N CSV rows scanned

# Default CSV: repo root IMDB Dataset.csv (Kaggle "IMDB Dataset")


def _corpus_limits():
    """(max_reviews, max_words); None means no cap (use entire CSV)."""
    r = os.environ.get("CORPUS_MAX_REVIEWS", "").strip()
    w = os.environ.get("CORPUS_MAX_WORDS", "").strip()
    max_r = int(r) if r else None
    max_w = int(w) if w else None
    return max_r, max_w


def default_csv_path() -> str:
    env = os.environ.get("CORPUS_CSV_PATH", "").strip()
    if env:
        return os.path.normpath(env)
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "IMDB Dataset.csv")
    )


def strip_html(text: str) -> str:
    """Remove HTML tags (e.g. <br />) from review text."""
    if not text:
        return ""
    text = _HTML_TAG_REGEX.sub(" ", text)
    return " ".join(text.split())


# ── Text Cleaning ──────────────────────────────────────────────────────────────


def clean_text(text: str) -> str:
    """Normalise and clean raw text with bounded operations."""
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    text = text.lower()
    text = _LATEX_REGEX.sub(" ", text)
    text = _MATH_REGEX.sub(" ", text)
    text = _URL_REGEX.sub(" ", text)
    text = _SPECIAL_REGEX.sub(" ", text)
    text = " ".join(text.split())
    return text


def tokenize(text: str) -> list[str]:
    """Extract clean alpha tokens."""
    tokens = []
    for tok in text.split():
        tok = tok.strip("'-")
        if tok and len(tok) > 1 and re.match(r'^[a-z][a-z]*$', tok):
            tokens.append(tok)
    return tokens


# ── Build & Save ───────────────────────────────────────────────────────────────


def build_corpus():
    csv_path = default_csv_path()
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(
            f"IMDB CSV not found: {csv_path}\n"
            "Place IMDB Dataset.csv at the repository root, or set CORPUS_CSV_PATH.\n"
            "Download: https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"
        )

    print("=" * 60)
    print("  LexiAI - IMDB review corpus builder")
    print("=" * 60)
    print(f"  Source: {csv_path}")
    max_reviews, max_words = _corpus_limits()
    if max_reviews is not None or max_words is not None:
        print(
            f"  Caps: max_reviews={max_reviews}, max_words={max_words} "
            "(unset env vars for full dataset)\n"
        )
    else:
        print(
            "  Full dataset: all CSV rows (no caps). corpus.json will be large; "
            "first GUI load may take longer.\n"
        )

    all_papers = []
    all_tokens = []
    total_words = 0
    rows_scanned = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "review" not in reader.fieldnames:
            raise ValueError(
                f"CSV must have a 'review' column; got fields: {reader.fieldnames!r}"
            )

        for row in reader:
            if max_reviews is not None and len(all_papers) >= max_reviews:
                print(f"\nOK Reached review cap ({max_reviews}) - stopping early.")
                break
            if max_words is not None and total_words >= max_words:
                print(f"\nOK Reached word cap ({max_words:,}) - stopping early.")
                break

            rows_scanned += 1
            raw = (row.get("review") or "").strip()
            text = strip_html(raw)
            if len(text) < MIN_REVIEW_CHARS:
                continue

            doc_id = f"imdb-{rows_scanned}"

            paper = {
                "id": doc_id,
                "title": "review",
                "abstract": text[:MAX_ABSTRACT_STORE],
            }
            combined = paper["title"] + " " + paper["abstract"]
            cleaned = clean_text(combined)
            tokens = tokenize(cleaned)

            if len(tokens) < 20:
                continue

            all_papers.append(paper)
            all_tokens.extend(tokens)
            total_words += len(tokens)

            if rows_scanned % PROGRESS_EVERY == 0:
                print(
                    f"  ... {rows_scanned:,} rows scanned | "
                    f"{len(all_papers)} reviews kept | {total_words:,} words"
                )

    # ── Compute statistics ──
    print(f"\n{'-'*60}")
    print("  Building frequency tables...")

    word_freq = Counter(all_tokens)
    vocabulary = set(word_freq.keys())

    bigrams: Counter = Counter()
    for i in range(len(all_tokens) - 1):
        bigrams[(all_tokens[i], all_tokens[i + 1])] += 1

    top30 = word_freq.most_common(30)

    print(f"  Total tokens   : {len(all_tokens):,}")
    print(f"  Unique words   : {len(vocabulary):,}")
    print(f"  Unique bigrams : {len(bigrams):,}")
    print(f"  Reviews kept   : {len(all_papers)}")
    print(f"  CSV rows scanned: {rows_scanned:,}")
    print(f"\n  Top 20 words   : {[w for w, _ in top30[:20]]}")

    # ── Serialise ──
    def validate_paper(p: dict) -> bool:
        abstract = p.get("abstract", "")
        return (
            isinstance(p.get("id"), str)
            and isinstance(abstract, str)
            and isinstance(p.get("title"), str)
            and 0 < len(abstract) <= MAX_ABSTRACT_STORE
        )

    valid_papers = [p for p in all_papers if validate_paper(p)]
    if not valid_papers:
        raise ValueError(f"All {len(all_papers)} documents invalid (check CSV content)")

    bigram_dict = {f"{w1}|{w2}": count for (w1, w2), count in bigrams.items()}

    payload = {
        "meta": {
            "total_tokens": len(all_tokens),
            "unique_words": len(vocabulary),
            "total_bigrams": len(bigram_dict),
            "total_papers": len(valid_papers),
            "source": "IMDB Dataset.csv",
            "csv_path": os.path.basename(csv_path),
            "rows_scanned": rows_scanned,
            "reviews_kept": len(valid_papers),
        },
        "word_freq": dict(word_freq),
        "bigrams": bigram_dict,
        "vocabulary": list(vocabulary),
        "tokens": all_tokens,
        "papers": [
            {"id": p["id"], "title": p["title"], "abstract": p["abstract"][:300]}
            for p in valid_papers
        ],
    }

    out_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\n{'='*60}")
    print(f"  Saved -> {out_path}  ({size_kb:.0f} KB)")
    print("  Run: python gui_app.py  to launch the app")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    build_corpus()
