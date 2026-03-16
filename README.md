# NLP Assignment — Spelling Correction & Sentiment Analysis

A two-part NLP system built for CT052-3-M-NLP covering probabilistic 
spelling correction and supervised text classification.

---

## Part 1 — Domain-Specific Spelling Corrector (LexiAI)

A spelling correction system trained on real AI/NLP research papers 
fetched from the arXiv API. Detects both non-word errors (words that 
don't exist) and real-word errors (valid words used in the wrong context).

**Techniques used:**
- Bigram Language Model with Laplace smoothing for real-word error detection
- Weighted Damerau-Levenshtein (Minimum Edit Distance) for candidate ranking
- Edit-1 / Edit-2 candidate generation with keyboard-proximity substitutions
- TF-IDF style corpus weighting for domain term prioritisation

**Two interfaces:**
- `gui_app.py` — desktop GUI built with tkinter
- `LexiAI_SpellChecker.html` — standalone browser app, no install needed

---

## Part 2 — Sentiment Analysis Classifier (SentiAI)

A supervised binary text classifier trained on 50,000 IMDB movie reviews 
to predict positive or negative sentiment.

**Models built:**
- Logistic Regression + TF-IDF (unigrams + bigrams)
- Multinomial Naive Bayes + TF-IDF

**Pipeline:**
- Text cleaning, stopword removal, TF-IDF vectorisation (50k features)
- GridSearchCV hyperparameter tuning with 5-fold cross-validation
- ~89% accuracy, ~0.96 ROC-AUC on held-out test set

**Deployment:** `sentiment_deployment.html` — a standalone webpage that 
runs full TF-IDF + Logistic Regression inference in pure JavaScript. 
No server required.

---

## Project Structure
```
NLP_Assignment/
├── part_a_section1_spelling_corrector/
│   ├── build_corpus.py          # fetches arXiv papers (run first)
│   ├── corpus.py                # corpus builder + bigram LM
│   ├── corrector.py             # MED engine + spell checker
│   ├── gui_app.py               # desktop GUI
│   └── LexiAI_SpellChecker.html # browser GUI
│
└── part_a_section2_sentiment/
    ├── sentiment_classification.ipynb  # full ML pipeline
    └── sentiment_deployment.html       # standalone deployment page
```

---

## Setup & Usage

### Spelling Corrector
```bash
# Step 1 — fetch real arXiv corpus (requires internet, ~2-3 mins)
python build_corpus.py

# Step 2 — launch the desktop app
python gui_app.py

# OR just open LexiAI_SpellChecker.html in any browser
```

### Sentiment Classifier
```bash
pip install scikit-learn pandas numpy matplotlib seaborn
```
1. Download [IMDB Dataset.csv](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) and place it in the sentiment folder
2. Run all cells in `sentiment_classification.ipynb`
3. Open the generated `sentiment_deployment.html` in any browser

---

## Requirements

| Component | Requirements |
|---|---|
| Spelling corrector | Python 3.8+, tkinter (stdlib) |
| Sentiment notebook | Python 3.8+, scikit-learn, pandas, numpy, matplotlib, seaborn |
| Both HTML apps | Any modern browser — no install needed |

---

## Built With
Python · scikit-learn · tkinter · Vanilla JS · arXiv API · IMDB Dataset
```

---

And for the **short one-line GitHub repo description** (the bit that goes under the repo name):
```
Domain-specific spelling corrector (arXiv corpus + Bigram LM + MED) and IMDB sentiment classifier (Logistic Regression + TF-IDF) — CT052-3-M-NLP Assignment
