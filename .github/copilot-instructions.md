# LexiAI NLP Assignment — Workspace Instructions

This document provides essential guidance for working with the **LexiAI NLP Assignment** project, which consists of two major components: a movie domain-specific spelling corrector and sentiment analysis classification.

## 🏗️ Project Architecture

### Part A Section 1: Spelling Corrector (`part_a_section1_spelling_corrector/`)
**Tkinter GUI application for NLP-domain spelling correction**

- **Technology:** Python 3.8+, tkinter (standard library), no external dependencies
- **Architecture:** Modular design with separation of concerns
  - `gui_app.py` — User interface (run this to start)
  - `corrector.py` — NLP engine: MED (Minimum Edit Distance) + Bigram Language Model
  - `corpus.py` — Corpus building and preprocessing
  - `build_corpus.py` — Utility to fetch real arXiv data

**How to Run:**
```bash
python gui_app.py
```

**Key Features:**
- Non-word error detection (vocabulary lookup)
- Real-word error detection (bigram probability)
- Edit-1 & edit-2 candidate generation with keyboard proximity awareness
- Context-aware ranking using weighted Levenshtein distance

**Error Types:**
- 🔴 **Non-word errors** — word not in vocabulary (e.g., `tokinization` → `tokenization`)
- 🟠 **Real-word errors** — valid word in wrong context, detected by low bigram probability

### Part A Section 2: Sentiment Analysis (`part_a_section2_sentiment/`)
**Jupyter notebook-based sentiment classification using IMDB dataset**

- **Main File:** `sentiment_classification.ipynb` (run this notebook)
- **Deployment:** `sentiment_deployment.html` — Static HTML version
- **Model Artifacts:** `model_weights.json` — Serialized trained weights
- **Visualizations:** `*_results.png`, `eda_*.png` (plots and charts)

**Dataset:** Shared `IMDB Dataset.csv` in project root

---

## 📁 Project Structure

```
NLP-Assignment/
├── IMDB Dataset.csv              ← Shared dataset for sentiment analysis
├── requirements.txt              ← Python dependencies (empty—no external deps)
├── README.md                     ← Main project overview
│
├── part_a_section1_spelling_corrector/
│   ├── gui_app.py               ← **Entry point: Run this**
│   ├── corrector.py             ← NLP Engine (MED + Bigram LM)
│   ├── corpus.py                ← Corpus builder & preprocessor
│   ├── build_corpus.py          ← Fetch real arXiv data
│   ├── model_weights.json       ← Learned vocabulary & bigram counts
│   └── README.md
│
└── part_a_section2_sentiment/
    ├── sentiment_classification.ipynb    ← **Entry point: Run this notebook**
    ├── sentiment_deployment.html         ← Static HTML export
    ├── model_weights.json               ← Trained model parameters
    ├── eda_overview.png                 ← Exploratory Data Analysis
    ├── eda_top_words.png
    ├── lr_results.png                   ← Model performance charts
    ├── nb_results.png
    ├── model_comparison.png
```

---

## 🛠️ Development Guidelines

### Environment Setup
- **Python Version:** 3.8+
- **Virtual Environment:** Already configured (`.venv/`)
- **Activation:** `. .venv/Scripts/activate` (Windows PowerShell)
- **No External Dependencies:** Both components use standard library only

### Running Components

**Spelling Corrector:**
```bash
cd part_a_section1_spelling_corrector
python gui_app.py
```
- Opens a Tkinter GUI with 4 tabs: Spell Checker, Min Edit Distance, Corpus Dictionary, About
- Supports AI/NLP text (up to 500 chars)
- Interactive error correction with ranked suggestions

**Sentiment Analysis:**
```bash
cd part_a_section2_sentiment
jupyter notebook sentiment_classification.ipynb
```
- Train/evaluate classification models on IMDB dataset
- Generates visualizations and weights
- Export to HTML for sharing

### Code Conventions

**Spelling Corrector:**
- Function names: `snake_case`
- Class names: `PascalCase`
- Docstrings: Include purpose, parameters, and return types
- Comments: Explain non-obvious algorithmic steps (e.g., DP matrix logic)
- Modularity: Keep corpus, language model, and GUI logic separate

**Sentiment Analysis:**
- Use markdown cells for documentation and sections
- Include visualizations with clear titles and labels
- Store final model weights in JSON for reproducibility
- Comment complex preprocessing or feature engineering steps

### Key Design Decisions

1. **Spelling Corrector—No External Dependencies:**
   - Pure Python implementation (no NLTK, spaCy, etc.)
   - Allows tkinter GUI to work standalone on any Python 3.8+ install
   - Keyboard proximity awareness baked into candidate generation

2. **Cost Weights in MED:**
   - Insertion: 1, Deletion: 1, Substitution: 2, Transposition: 1
   - Weighted toward substitutions to prefer single-character fixes
   - Transposition cost = 1 (cheap) to catch common typos (e.g., `teh` → `the`)

3. **Bigram Language Model:**
   - Laplace smoothing to handle unseen bigrams
   - Detects real-word errors by finding contextually unlikely word pairs
   - Movie Domain-specific corpus improves accuracy for NLP/AI text

### Common Development Environment Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'tkinter'` | Linux only: `sudo apt-get install python3-tk` |
| `ImportError: cannot import name 'CorpusBuilder'` | Ensure all `.py` files are in same folder |
| Corpus shows "Loading…" forever | Restart app; corpus builds in background thread (~1 sec) |
| Sentiment notebook slow to run | IMDB dataset is large; first cell loads & preprocesses data |
| Mismatched model weights | Ensure `model_weights.json` is from same training run |

---

## 🎯 Common Tasks

### Modify Spelling Corrector Algorithm
- **Edit costs:** `corrector.py` → `MinEditDistance.__init__()`
- **Keyboard proximity:** `corrector.py` → `KEYBOARD_NEIGHBORS` dict
- **Bigram smoothing:** `corrector.py` → `BigramLanguageModel.laplace_smoothing()`

### Train/Evaluate Sentiment Model
- **Preprocessing:** First cells of `sentiment_classification.ipynb`
- **Feature engineering:** Mid-section cells
- **Model comparison:** See `model_comparison.png` and notebook output
- **Export weights:** Notebook automatically saves to `model_weights.json`

### Add New Corpus
- **Edit:** `part_a_section1_spelling_corrector/build_corpus.py`
- **Run:** `python build_corpus.py` to fetch and build new corpus
- **Reimport:** Restart `gui_app.py` to reload weights

---

## 📚 Documentation Links

- [README.md](README.md) — Project overview
- [part_a_section1_spelling_corrector/README.md](part_a_section1_spelling_corrector/README.md) — Spelling corrector detailed guide
- [CODE_REVIEW.md](CODE_REVIEW.md) — 📋 Comprehensive code quality & security analysis (38+ issues with fixes)
- Correction Algorithm Details — See docstrings in `corrector.py`
- IMDB Dataset Documentation — First cell of `sentiment_classification.ipynb`

---

## 💡 Tips for AI Assistant Interactions

When asking for help with this project:
- **Specify the component:** "Spelling corrector" vs "Sentiment analysis"
- **Describe the issue:** Error message, unexpected behavior, or feature request
- **Provide context:** Which file, what you're trying to do, what you've tried
- **For algorithm changes:** Explain the goal (e.g., "reduce false positives", "improve speed")
- **For analysis tasks:** Share sample input/output or link to notebook cells

### ⚠️ Known Issues & Fixes
See [CODE_REVIEW.md](CODE_REVIEW.md) for detailed analysis. Critical areas:
- **Thread safety:** Corpus loading race condition (HIGH priority)
- **Input validation:** No bounds checks on text length (HIGH priority)
- **Network operations:** Missing timeouts and rate limiting (CRITICAL)
- **Error handling:** Silent failures in file/API operations

Start with Phase 1 fixes listed in CODE_REVIEW.md.

---

## 🧪 Testing

Comprehensive test suite with 90+ tests covering all critical components:
- **Unit tests:** Individual functions and classes
- **Integration tests:** End-to-end workflows
- **Edge cases:** Unicode, empty text, special characters
- **Performance tests:** Algorithm efficiency

**Quick Start:**
```bash
pytest -v                  # Run all tests
pytest -m "not slow"       # Fast run (unit tests only)
pytest -m critical         # Critical tests only
pytest --cov=part_a_section1_spelling_corrector  # With coverage
```

See [tests/README.md](tests/README.md) and [TESTING_SUITE_SUMMARY.md](TESTING_SUITE_SUMMARY.md) for details.

---

## 🚀 Next Steps

1. Run `python gui_app.py` to test the spelling corrector
2. Open `sentiment_classification.ipynb` to explore the sentiment analysis workflow
3. Check `part_a_section1_spelling_corrector/README.md` for deeper technical details
4. Run `pytest -v` to verify testing suite works
5. Review [CODE_REVIEW.md](CODE_REVIEW.md) for critical fixes
6. Refer to this doc when making modifications to either component
