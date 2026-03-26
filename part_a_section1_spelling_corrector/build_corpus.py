"""
build_corpus.py — arXiv Corpus Builder for LexiAI
===================================================
Fetches real NLP/AI research paper abstracts from the arXiv API,
cleans and tokenizes them, then saves a corpus.json file that
corpus.py and gui_app.py will automatically load instead of the
embedded seed text.

Run once:
    python build_corpus.py

Then run the app as normal:
    python gui_app.py

Requirements: Python 3.8+ (uses only standard library)
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import os
import time
from collections import Counter

# ── Configuration ─────────────────────────────────────────────────────────────

# arXiv API search queries — covers NLP, LLMs, transformers, etc.
SEARCH_QUERIES = [
    "large language models transformer NLP",
    "tokenization subword embedding neural",
    "attention mechanism self-attention BERT GPT",
    "semantic retrieval dense vector embedding",
    "fine-tuning pre-training language model",
    "named entity recognition dependency parsing",
    "machine translation sequence to sequence",
    "reinforcement learning human feedback alignment",
    "prompt engineering in-context learning",
    "hallucination grounding factual accuracy",
    "knowledge graph relation extraction",
    "text classification sentiment analysis",
    "summarization abstractive extractive",
    "speech recognition natural language generation",
    "federated learning differential privacy NLP",
    "explainability interpretability attention visualization",
    "low rank adaptation quantization distillation",
    "retrieval augmented generation RAG",
    "chain of thought reasoning commonsense",
    "multilingual cross-lingual zero-shot transfer",
]

PAPERS_PER_QUERY = 15       # papers fetched per query
MAX_TOTAL_PAPERS = 200      # hard cap
TARGET_WORDS    = 120_000   # stop early if we exceed this
OUTPUT_FILE     = "corpus.json"
DELAY_SECONDS   = 1.5       # polite delay between API calls

# arXiv categories to restrict to (cs.CL = Computation & Language)
CATEGORIES = ["cs.CL", "cs.AI", "cs.LG"]

# ── arXiv API ─────────────────────────────────────────────────────────────────

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom"}


def fetch_papers(query: str, max_results: int = 15) -> list[dict]:
    """Fetch paper metadata from arXiv API for a given query."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"    ⚠ Network error: {e}")
        return []

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"    ⚠ XML parse error: {e}")
        return []

    papers = []
    for entry in root.findall("atom:entry", NS):
        title_el   = entry.find("atom:title", NS)
        summary_el = entry.find("atom:summary", NS)
        id_el      = entry.find("atom:id", NS)

        if title_el is None or summary_el is None:
            continue

        title   = (title_el.text or "").strip().replace("\n", " ")
        summary = (summary_el.text or "").strip().replace("\n", " ")
        arxiv_id = (id_el.text or "").strip() if id_el is not None else ""

        if len(summary) < 100:
            continue  # skip very short abstracts

        papers.append({
            "id":      arxiv_id,
            "title":   title,
            "abstract": summary,
        })

    return papers


# ── Text Cleaning ──────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalise and clean raw abstract text."""
    text = text.lower()
    # Remove LaTeX commands
    text = re.sub(r"\\[a-z]+\{[^}]*\}", " ", text)
    text = re.sub(r"\$[^$]*\$", " ", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", " ", text)
    # Remove non-alpha except spaces
    text = re.sub(r"[^a-z\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
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
    print("=" * 60)
    print("  LexiAI — arXiv Corpus Builder")
    print("=" * 60)

    seen_ids   = set()
    all_papers = []
    all_tokens = []
    total_words = 0

    for qi, query in enumerate(SEARCH_QUERIES):
        if len(all_papers) >= MAX_TOTAL_PAPERS:
            print(f"\n✓ Reached {MAX_TOTAL_PAPERS} papers — stopping early.")
            break
        if total_words >= TARGET_WORDS:
            print(f"\n✓ Reached {total_words:,} words — stopping early.")
            break

        print(f"\n[{qi+1}/{len(SEARCH_QUERIES)}] Query: \"{query}\"")
        papers = fetch_papers(query, max_results=PAPERS_PER_QUERY)
        new_count = 0

        for paper in papers:
            if paper["id"] in seen_ids:
                continue
            seen_ids.add(paper["id"])

            text = paper["title"] + " " + paper["abstract"]
            cleaned = clean_text(text)
            tokens  = tokenize(cleaned)

            if len(tokens) < 20:
                continue

            all_papers.append(paper)
            all_tokens.extend(tokens)
            total_words += len(tokens)
            new_count += 1

        print(f"    → {new_count} new papers | total: {len(all_papers)} papers, {total_words:,} words")

        if qi < len(SEARCH_QUERIES) - 1:
            time.sleep(DELAY_SECONDS)

    # ── Compute statistics ──
    print(f"\n{'─'*60}")
    print(f"  Building frequency tables…")

    word_freq = Counter(all_tokens)
    vocabulary = set(word_freq.keys())

    bigrams: Counter = Counter()
    for i in range(len(all_tokens) - 1):
        bigrams[(all_tokens[i], all_tokens[i+1])] += 1

    # Top 30 most frequent words
    top30 = word_freq.most_common(30)

    print(f"  Total tokens   : {len(all_tokens):,}")
    print(f"  Unique words   : {len(vocabulary):,}")
    print(f"  Unique bigrams : {len(bigrams):,}")
    print(f"  Papers fetched : {len(all_papers)}")
    print(f"\n  Top 20 words   : {[w for w,_ in top30[:20]]}")

    # ── Serialise ──
    # Convert Counter keys (tuples) to strings for JSON
    bigram_dict = {f"{w1}|{w2}": count for (w1, w2), count in bigrams.items()}

    payload = {
        "meta": {
            "total_tokens":  len(all_tokens),
            "unique_words":  len(vocabulary),
            "total_bigrams": len(bigram_dict),
            "total_papers":  len(all_papers),
            "queries_used":  SEARCH_QUERIES,
        },
        "word_freq":  dict(word_freq),
        "bigrams":    bigram_dict,
        "vocabulary": list(vocabulary),
        "tokens":     all_tokens,
        "papers": [
            {"id": p["id"], "title": p["title"], "abstract": p["abstract"][:300]}
            for p in all_papers
        ],
    }

    out_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\n{'='*60}")
    print(f"  ✓ Saved → {out_path}  ({size_kb:.0f} KB)")
    print(f"  Run  →  python gui_app.py  to launch the app")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    build_corpus()
