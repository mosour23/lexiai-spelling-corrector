# LexiAI — Domain-Specific Spelling Corrector
### NLP Research Tool | Python 3.8+ | No external dependencies

---

## Quick Start

```
python gui_app.py
```

That's it. No pip install needed.

---

## Files

```
├── gui_app.py        ← Main GUI application (run this)
├── build_corpus.py   ← Corpus fetcher from arXiv
├── corpus.py         ← Corpus builder & preprocessor
├── corrector.py      ← NLP engine: MED + Bigram LM
└── README.md         ← This file
```

---

## Requirements

- **Python 3.8 or higher**
- **tkinter** — included with standard Python on Windows and macOS.
  - On Linux (Ubuntu/Debian), install it with:
    ```
    sudo apt-get install python3-tk
    ```

---

## How to Run

### Windows
Double-click `gui_app.py`, or open a terminal and run:
```
python gui_app.py
```

### macOS
```
python3 gui_app.py
```

### Linux
```
python3 gui_app.py
```

---

## Features

| Tab | What it does |
|-----|-------------|
| **Spell Checker** | Paste up to 500 chars of AI/NLP text. Errors highlighted in red (non-word) or orange (real-word). Click an error to see ranked suggestions with MED score and bigram probability. Click a suggestion to apply it. |
| **Min Edit Distance** | Type any two words to see the full dynamic programming matrix and edit cost computed live. |
| **Corpus Dictionary** | Browse, search, and sort the 945+ word domain vocabulary. |
| **About** | System architecture and objectives. |

---

## Error Types

- 🔴 **Non-word error** — word not found in vocabulary (e.g. `tokinization` → `tokenization`)
- 🟠 **Real-word error** — valid word used in wrong context, detected by low bigram probability (e.g. `base` instead of `bias`)

---

## Correction Algorithm

1. **Candidate generation** — edit-1 and edit-2 operations (insert, delete, substitute, transpose) + keyboard-proximity substitutions
2. **Ranking** — combined score of:
   - Weighted Levenshtein distance (ins=1, del=1, sub=2, transpose=1)
   - Laplace-smoothed Bigram Language Model probability

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'tkinter'`**
→ Install tkinter: `sudo apt-get install python3-tk` (Linux only)

**`ImportError: cannot import name 'CorpusBuilder'`**
→ Make sure all three `.py` files are in the same folder.

**App opens but corpus shows "Loading…" forever**
→ Restart the app. The corpus builds in a background thread and usually loads in under 1 second.

---

## Fetching Real arXiv Data

Run the corpus builder **once** before launching the app:

```
python build_corpus.py
```

This will:
1. Query the arXiv API across 20 NLP/AI search topics
2. Download ~200 paper abstracts (cs.CL, cs.AI, cs.LG)
3. Clean, tokenize, and save everything to `corpus.json`
4. The app loads `corpus.json` automatically on next launch

**What gets fetched (~2–3 minutes):**
- Large language models, transformers, BERT, GPT
- Tokenization, embeddings, attention mechanisms
- RAG, fine-tuning, RLHF, prompt engineering
- NER, parsing, machine translation, summarization
- And 15 more NLP topic areas

**Result:** 100,000+ tokens from real research papers instead of the built-in seed text.

> Requires internet connection. Uses only Python standard library (urllib).
> Respects arXiv's API rate limit with 1.5s delay between requests.
