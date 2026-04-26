# LexiAI — Movie Domain-Specific Spelling Corrector
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
├── build_corpus.py   ← Builds corpus.json from ../IMDB Dataset.csv (no network)
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

### Setup Virtual Enrivonment

```
py -m venv venv
```

```
venv/Scripts/Activate
```

### Build the corpus

Place **IMDB Dataset.csv** at the **repository root** (same folder as `README.md` / `requirements.txt`).  
Optional: [Kaggle IMDB dataset](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews).  
Override path: set environment variable `CORPUS_CSV_PATH` to your CSV file.

By default the builder uses **the whole CSV** (all ~50k reviews) so vocabulary and bigrams are as rich as possible. `corpus.json` can be **tens of MB** and the GUI may take longer to start the first time.

For a **smaller quick build**, set caps before running (PowerShell example):

```
$env:CORPUS_MAX_REVIEWS="800"; $env:CORPUS_MAX_WORDS="120000"; python .\build_corpus.py
```

```
cd part_a_section1_spelling_corrector
```

```
python .\build_corpus.py
```

This reads reviews locally and writes `corpus.json` next to `build_corpus.py` (no arXiv / no API).

### Run the code (Windows)
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

## Building the corpus from IMDB reviews

Run the corpus builder **once** before launching the app (no internet):

```
python build_corpus.py
```

This will:
1. Read `../IMDB Dataset.csv` (Kaggle-style columns: `review`, `sentiment`)
2. Strip HTML tags, clean, and tokenize review text
3. Save `corpus.json` (stops at `TARGET_WORDS` or `MAX_TOTAL_PAPERS` in `build_corpus.py`)
4. The app loads `corpus.json` automatically on next launch

**Result:** 100k+ tokens of movie-review English instead of the built-in seed text.

> Uses only the Python standard library (`csv`). Optional: `CORPUS_CSV_PATH` to point at another CSV with a `review` column.
