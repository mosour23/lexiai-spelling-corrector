"""
gui_app.py — LexiAI Spell Checker · Local Tkinter GUI
Run: python gui_app.py
Requires: Python 3.8+ (tkinter is included in standard Python installs)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
import math

# ── Import NLP engine ────────────────────────────────────────────────────────
try:
    from corpus import CorpusBuilder
    from corrector import SpellChecker
except ImportError as e:
    import sys
    print(f"ERROR: Could not import NLP modules: {e}")
    print("Make sure corpus.py and corrector.py are in the same folder as gui_app.py")
    sys.exit(1)

# ── Colour Palette ────────────────────────────────────────────────────────────
BG         = "#0a0c10"
SURFACE    = "#111318"
SURFACE2   = "#181c24"
SURFACE3   = "#1e2330"
BORDER     = "#242a38"
ACCENT     = "#4fffb0"
ACCENT2    = "#3dd8ff"
ACCENT3    = "#ff6b6b"
WARN       = "#ffa94d"
TEXT       = "#e4e8f0"
MUTED      = "#6b7492"
ERR_NW_BG  = "#2a1a1a"
ERR_RW_BG  = "#2a1f0f"


# ═══════════════════════════════════════════════════════════════════════════════
class LexiAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LexiAI — Domain Spelling Corrector")
        self.geometry("1100x740")
        self.minsize(900, 600)
        self.configure(bg=BG)

        # State
        self.current_errors = []
        self.selected_err_idx = -1
        self.corpus = None
        self.checker = None
        
        # Thread synchronization for async corpus loading
        self._corpus_ready = threading.Event()
        self._corpus_lock = threading.Lock()

        self._build_ui()
        self._load_corpus_async()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._apply_styles()

        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(hdr, text="Lexi", font=("Helvetica", 22, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="AI", font=("Helvetica", 22, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="  Domain-Specific Spelling Corrector · NLP Research Tool",
                 font=("Helvetica", 10), bg=BG, fg=MUTED).pack(side="left", pady=(8, 0))

        self.status_lbl = tk.Label(hdr, text="⏳ Loading corpus…",
                                   font=("Courier", 9), bg=BG, fg=MUTED)
        self.status_lbl.pack(side="right", pady=(8, 0))

        sep = tk.Frame(self, height=1, bg=BORDER)
        sep.pack(fill="x", padx=24, pady=(12, 0))

        # Notebook tabs
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=16, pady=12)

        self.tab_checker = tk.Frame(self.nb, bg=BG)
        self.tab_med     = tk.Frame(self.nb, bg=BG)
        self.tab_corpus  = tk.Frame(self.nb, bg=BG)
        self.tab_about   = tk.Frame(self.nb, bg=BG)

        self.nb.add(self.tab_checker, text="  ⬡  Spell Checker  ")
        self.nb.add(self.tab_med,     text="  ⬡  Min Edit Distance  ")
        self.nb.add(self.tab_corpus,  text="  ⬡  Corpus Dictionary  ")
        self.nb.add(self.tab_about,   text="  ⬡  About  ")

        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self._build_checker_tab()
        self._build_med_tab()
        self._build_corpus_tab()
        self._build_about_tab()

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=SURFACE, foreground=MUTED,
                        padding=[12, 6], font=("Helvetica", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE3)],
                  foreground=[("selected", ACCENT)])
        style.configure("TScrollbar", background=SURFACE2, troughcolor=SURFACE,
                        borderwidth=0, arrowcolor=MUTED)
        style.configure("Vertical.TScrollbar", width=8)

    # ── Checker Tab ───────────────────────────────────────────────────────────
    def _build_checker_tab(self):
        tab = self.tab_checker
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)
        tab.rowconfigure(1, weight=1)

        # ── Left column ──
        left = tk.Frame(tab, bg=BG)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(8, 4), pady=8)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Input card
        in_card = self._card(left, "INPUT TEXT", subtitle="max 500 characters")
        in_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        in_card.columnconfigure(0, weight=1)

        self.input_text = tk.Text(in_card, height=6, width=60,
                                   bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                                   font=("Courier", 11), relief="flat",
                                   wrap="word", padx=10, pady=8,
                                   highlightthickness=1,
                                   highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self.input_text.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
        self.input_text.bind("<KeyRelease>", self._on_input_change)

        # Char counter
        self.char_lbl = tk.Label(in_card, text="0 / 500",
                                  font=("Courier", 9), bg=SURFACE, fg=MUTED)
        self.char_lbl.grid(row=2, column=0, sticky="e", padx=14, pady=(0, 4))

        # Buttons row
        btn_row = tk.Frame(in_card, bg=SURFACE)
        btn_row.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))

        self.check_btn = tk.Button(btn_row, text="▶  Check Spelling",
                                    bg=ACCENT, fg="#0a0c10",
                                    font=("Helvetica", 11, "bold"),
                                    relief="flat", cursor="hand2", padx=16, pady=8,
                                    command=self._run_check)
        self.check_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(btn_row, text="✕  Clear",
                  bg=SURFACE2, fg=MUTED,
                  font=("Helvetica", 10), relief="flat",
                  cursor="hand2", padx=12, pady=8,
                  command=self._clear_all).pack(side="left")

        # Legend
        leg = tk.Frame(in_card, bg=SURFACE)
        leg.grid(row=4, column=0, sticky="w", padx=12, pady=(0, 10))
        self._legend_dot(leg, ACCENT3, "Non-word error")
        self._legend_dot(leg, WARN,    "Real-word error")

        # Result card
        res_card = self._card(left, "ANNOTATED OUTPUT")
        res_card.grid(row=1, column=0, sticky="nsew")
        res_card.rowconfigure(1, weight=1)
        res_card.columnconfigure(0, weight=1)

        # Stats bar
        self.stats_frame = tk.Frame(res_card, bg=SURFACE)
        self.stats_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(0, 6))

        # Result text box
        res_wrap = tk.Frame(res_card, bg=SURFACE2,
                             highlightthickness=1, highlightbackground=BORDER)
        res_wrap.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        res_wrap.rowconfigure(0, weight=1)
        res_wrap.columnconfigure(0, weight=1)

        self.result_box = tk.Text(res_wrap, bg=SURFACE2, fg=TEXT,
                                   font=("Courier", 11), relief="flat",
                                   wrap="word", padx=10, pady=8,
                                   state="disabled", cursor="arrow",
                                   highlightthickness=0)
        res_scroll = ttk.Scrollbar(res_wrap, command=self.result_box.yview)
        self.result_box.configure(yscrollcommand=res_scroll.set)
        self.result_box.grid(row=0, column=0, sticky="nsew")
        res_scroll.grid(row=0, column=1, sticky="ns")

        # Tag styles for errors
        self.result_box.tag_configure("err_nw",
            background=ERR_NW_BG, foreground=ACCENT3,
            underline=True, font=("Courier", 11, "bold"))
        self.result_box.tag_configure("err_rw",
            background=ERR_RW_BG, foreground=WARN,
            underline=True, font=("Courier", 11, "bold"))
        self.result_box.tag_configure("err_nw_sel",
            background="#3a2020", foreground=ACCENT3,
            underline=True, font=("Courier", 11, "bold"),
            relief="raised", borderwidth=1)
        self.result_box.tag_configure("err_rw_sel",
            background="#3a2a10", foreground=WARN,
            underline=True, font=("Courier", 11, "bold"),
            relief="raised", borderwidth=1)

        # ── Right column: Errors panel ──
        right = tk.Frame(tab, bg=BG)
        right.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(4, 8), pady=8)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        err_card = self._card(right, "ERRORS & SUGGESTIONS")
        err_card.grid(row=0, column=0, sticky="nsew")
        err_card.rowconfigure(1, weight=1)
        err_card.columnconfigure(0, weight=1)

        self.err_count_lbl = tk.Label(err_card, text="—",
                                       font=("Courier", 9), bg=SURFACE, fg=MUTED)
        self.err_count_lbl.grid(row=0, column=1, sticky="e", padx=14)

        # Scrollable error list
        err_scroll_frame = tk.Frame(err_card, bg=SURFACE)
        err_scroll_frame.grid(row=1, column=0, columnspan=2, sticky="nsew",
                               padx=8, pady=(0, 8))
        err_scroll_frame.rowconfigure(0, weight=1)
        err_scroll_frame.columnconfigure(0, weight=1)

        self.err_canvas = tk.Canvas(err_scroll_frame, bg=SURFACE,
                                     highlightthickness=0)
        err_vscroll = ttk.Scrollbar(err_scroll_frame,
                                     command=self.err_canvas.yview)
        self.err_canvas.configure(yscrollcommand=err_vscroll.set)
        self.err_canvas.grid(row=0, column=0, sticky="nsew")
        err_vscroll.grid(row=0, column=1, sticky="ns")

        self.err_inner = tk.Frame(self.err_canvas, bg=SURFACE)
        self.err_canvas_window = self.err_canvas.create_window(
            (0, 0), window=self.err_inner, anchor="nw")
        self.err_inner.bind("<Configure>", self._on_err_inner_resize)
        self.err_canvas.bind("<Configure>", self._on_err_canvas_resize)

        self._show_err_placeholder("Click \"Check Spelling\" to begin")

    def _on_err_inner_resize(self, e):
        self.err_canvas.configure(scrollregion=self.err_canvas.bbox("all"))

    def _on_err_canvas_resize(self, e):
        self.err_canvas.itemconfig(self.err_canvas_window, width=e.width)

    def _legend_dot(self, parent, color, label):
        f = tk.Frame(parent, bg=SURFACE)
        f.pack(side="left", padx=(0, 14))
        tk.Frame(f, width=12, height=12, bg=color).pack(side="left", padx=(0, 5))
        tk.Label(f, text=label, font=("Helvetica", 9), bg=SURFACE, fg=MUTED).pack(side="left")

    # ── MED Tab ───────────────────────────────────────────────────────────────
    def _build_med_tab(self):
        tab = self.tab_med
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        card = self._card(tab, "MINIMUM EDIT DISTANCE VISUALIZER")
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tab.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)

        desc = ("Computes weighted Levenshtein distance (Damerau extension) between two strings.\n"
                "Operations: Insert=1  |  Delete=1  |  Substitute=2  |  Transpose=1")
        tk.Label(card, text=desc, font=("Helvetica", 10), bg=SURFACE,
                 fg=MUTED, justify="left").grid(row=1, column=0, sticky="w",
                                                padx=14, pady=(0, 14))

        # Input row
        inp_row = tk.Frame(card, bg=SURFACE)
        inp_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        tk.Label(inp_row, text="SOURCE:", font=("Courier", 9),
                 bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 6))
        self.med_src = tk.Entry(inp_row, font=("Courier", 13), width=16,
                                 bg=SURFACE2, fg=TEXT, insertbackground=ACCENT2,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=BORDER, highlightcolor=ACCENT2)
        self.med_src.pack(side="left", padx=(0, 16), ipady=5, ipadx=6)
        self.med_src.insert(0, "embedings")
        self.med_src.bind("<KeyRelease>", lambda e: self._run_med())

        tk.Label(inp_row, text="TARGET:", font=("Courier", 9),
                 bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 6))
        self.med_tgt = tk.Entry(inp_row, font=("Courier", 13), width=16,
                                 bg=SURFACE2, fg=TEXT, insertbackground=ACCENT2,
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=BORDER, highlightcolor=ACCENT2)
        self.med_tgt.pack(side="left", padx=(0, 16), ipady=5, ipadx=6)
        self.med_tgt.insert(0, "embeddings")
        self.med_tgt.bind("<KeyRelease>", lambda e: self._run_med())

        tk.Button(inp_row, text="Compute", bg=ACCENT2, fg="#0a0c10",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  cursor="hand2", padx=12, pady=5,
                  command=self._run_med).pack(side="left")

        # Score display
        self.med_score_frame = tk.Frame(card, bg=SURFACE)
        self.med_score_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 10))

        self.med_score_lbl = tk.Label(self.med_score_frame, text="",
                                       font=("Helvetica", 28, "bold"),
                                       bg=SURFACE, fg=ACCENT2)
        self.med_score_lbl.pack(side="left", padx=(0, 12))
        self.med_score_desc = tk.Label(self.med_score_frame, text="",
                                        font=("Helvetica", 10), bg=SURFACE, fg=MUTED)
        self.med_score_desc.pack(side="left")

        # Matrix display (scrollable canvas)
        matrix_wrap = tk.Frame(card, bg=SURFACE)
        matrix_wrap.grid(row=4, column=0, sticky="nsew", padx=14, pady=(0, 14))
        matrix_wrap.rowconfigure(0, weight=1)
        matrix_wrap.columnconfigure(0, weight=1)

        self.med_canvas = tk.Canvas(matrix_wrap, bg=SURFACE2,
                                     highlightthickness=1, highlightbackground=BORDER)
        med_hscroll = ttk.Scrollbar(matrix_wrap, orient="horizontal",
                                     command=self.med_canvas.xview)
        med_vscroll = ttk.Scrollbar(matrix_wrap, command=self.med_canvas.yview)
        self.med_canvas.configure(xscrollcommand=med_hscroll.set,
                                   yscrollcommand=med_vscroll.set)
        self.med_canvas.grid(row=0, column=0, sticky="nsew")
        med_hscroll.grid(row=1, column=0, sticky="ew")
        med_vscroll.grid(row=0, column=1, sticky="ns")

        self._run_med()

    # ── Corpus Tab ────────────────────────────────────────────────────────────
    def _build_corpus_tab(self):
        tab = self.tab_corpus
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        card = self._card(tab, "DOMAIN CORPUS DICTIONARY")
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        tab.rowconfigure(0, weight=1)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        # Stats row
        self.corpus_stats_frame = tk.Frame(card, bg=SURFACE)
        self.corpus_stats_frame.grid(row=1, column=0, sticky="ew",
                                      padx=14, pady=(0, 12))

        # Controls
        ctrl = tk.Frame(card, bg=SURFACE)
        ctrl.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 8))

        tk.Label(ctrl, text="🔍", font=("Helvetica", 12),
                 bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 4))
        self.dict_search_var = tk.StringVar()
        self.dict_search_var.trace("w", lambda *a: self._filter_dict())
        dict_entry = tk.Entry(ctrl, textvariable=self.dict_search_var,
                               font=("Courier", 11), width=24,
                               bg=SURFACE2, fg=TEXT, insertbackground=ACCENT,
                               relief="flat", highlightthickness=1,
                               highlightbackground=BORDER, highlightcolor=ACCENT)
        dict_entry.pack(side="left", ipady=5, ipadx=6, padx=(0, 14))

        tk.Label(ctrl, text="Sort:", font=("Helvetica", 10),
                 bg=SURFACE, fg=MUTED).pack(side="left", padx=(0, 4))
        self.sort_var = tk.StringVar(value="freq")
        for val, lbl in [("freq","Frequency ↓"), ("alpha","A → Z"), ("len","Length ↓")]:
            tk.Radiobutton(ctrl, text=lbl, variable=self.sort_var, value=val,
                           bg=SURFACE, fg=MUTED, selectcolor=SURFACE3,
                           activebackground=SURFACE, activeforeground=TEXT,
                           font=("Helvetica", 9), cursor="hand2",
                           command=self._filter_dict).pack(side="left", padx=6)

        # Dictionary list
        list_frame = tk.Frame(card, bg=SURFACE)
        list_frame.grid(row=3, column=0, sticky="nsew", padx=14, pady=(0, 14))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.dict_listbox = tk.Listbox(list_frame,
                                        bg=SURFACE2, fg=TEXT,
                                        font=("Courier", 11),
                                        selectbackground=SURFACE3,
                                        selectforeground=ACCENT,
                                        relief="flat",
                                        highlightthickness=1,
                                        highlightbackground=BORDER,
                                        activestyle="none",
                                        borderwidth=0)
        dict_vscroll = ttk.Scrollbar(list_frame, command=self.dict_listbox.yview)
        self.dict_listbox.configure(yscrollcommand=dict_vscroll.set)
        self.dict_listbox.grid(row=0, column=0, sticky="nsew")
        dict_vscroll.grid(row=0, column=1, sticky="ns")

    # ── About Tab ─────────────────────────────────────────────────────────────
    def _build_about_tab(self):
        tab = self.tab_about
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        card = self._card(tab, "SYSTEM OVERVIEW")
        card.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        text_wrap = tk.Frame(card, bg=SURFACE)
        text_wrap.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        text_wrap.rowconfigure(0, weight=1)
        text_wrap.columnconfigure(0, weight=1)

        about_box = tk.Text(text_wrap, bg=SURFACE2, fg=TEXT,
                             font=("Helvetica", 11), relief="flat",
                             wrap="word", padx=14, pady=12,
                             state="disabled", cursor="arrow",
                             highlightthickness=1, highlightbackground=BORDER,
                             spacing1=4, spacing3=4)
        about_scroll = ttk.Scrollbar(text_wrap, command=about_box.yview)
        about_box.configure(yscrollcommand=about_scroll.set)
        about_box.grid(row=0, column=0, sticky="nsew")
        about_scroll.grid(row=0, column=1, sticky="ns")

        about_box.tag_configure("h1", font=("Helvetica", 14, "bold"), foreground=ACCENT)
        about_box.tag_configure("h2", font=("Helvetica", 11, "bold"), foreground=TEXT)
        about_box.tag_configure("body", font=("Helvetica", 10), foreground=MUTED)
        about_box.tag_configure("code", font=("Courier", 10), foreground=ACCENT2,
                                  background=SURFACE3)

        about_box.configure(state="normal")
        content = [
            ("h1", "Domain-Specific Probabilistic Spelling Correction\n\n"),
            ("h2", "Objective 1 — Corpus Formulation\n"),
            ("body", ("A custom AI/NLP corpus is built from seed text covering transformers, tokenization, "
                      "embeddings, retrieval-augmented generation, RLHF, and more — enriched with 200+ "
                      "domain terms weighted for proper frequency. The corpus includes 2,600+ tokens, "
                      "945+ unique vocabulary entries, and 2,100+ bigrams, supplemented by 400+ common "
                      "English words to prevent false positives.\n\n")),
            ("h2", "Objective 2 — Error Detection & Correction\n"),
            ("body", ("Non-word errors are detected by vocabulary lookup. Real-word errors "
                      "(e.g. 'base' instead of 'bias') are detected when a valid word has anomalously "
                      "low bigram probability in context. Candidates are generated via edit-1/edit-2 "
                      "operations (insert, delete, substitute, transpose) plus keyboard-proximity "
                      "substitutions. Ranking uses a combined score of weighted Minimum Edit Distance "
                      "(ins=1, del=1, sub=2, transpose=1) and Laplace-smoothed Bigram LM probability.\n\n")),
            ("h2", "Objective 3 — Interactive GUI\n"),
            ("body", ("Four-tab interface: Spell Checker (500-char input, colour-coded error annotation, "
                      "click-to-select, one-click correction), MED Visualizer (live DP matrix), "
                      "Corpus Dictionary (searchable/sortable vocabulary), About page.\n\n")),
            ("h2", "Objective 4 — Limitations & Future Work\n"),
            ("body", ("Current limitations: corpus size (production would use 100k+ word corpora from "
                      "arXiv papers), narrow bigram context window for real-word detection, no POS-aware "
                      "filtering. Future work: trigram/n-gram models, POS tagging to constrain candidate "
                      "part-of-speech, transformer contextual embeddings, active corpus expansion.\n\n")),
            ("h2", "Tech Stack\n"),
            ("code", "  Python 3.8+  ·  tkinter (stdlib)  ·  No external dependencies\n"),
            ("code", "  Bigram LM + Laplace smoothing  ·  Damerau-Levenshtein MED\n"),
            ("code", "  Keyboard-proximity candidate generation  ·  Edit-1/Edit-2 search\n"),
        ]
        for tag, text in content:
            about_box.insert("end", text, tag)
        about_box.configure(state="disabled")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _card(self, parent, title, subtitle=""):
        frame = tk.Frame(parent, bg=SURFACE,
                          highlightthickness=1, highlightbackground=BORDER)
        frame.columnconfigure(0, weight=1)

        hdr = tk.Frame(frame, bg=SURFACE)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew",
                 padx=0, pady=0, ipadx=0)

        tk.Label(hdr, text=title, font=("Helvetica", 8, "bold"),
                 bg=SURFACE, fg=MUTED, pady=10, padx=14).pack(side="left")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=("Courier", 8),
                     bg=SURFACE, fg=MUTED).pack(side="right", padx=14)

        sep = tk.Frame(frame, height=1, bg=BORDER)
        sep.grid(row=0, column=0, columnspan=2, sticky="ew",
                 padx=0, pady=(35, 0))

        return frame

    def _show_err_placeholder(self, msg):
        for w in self.err_inner.winfo_children():
            w.destroy()
        tk.Label(self.err_inner, text=msg, font=("Helvetica", 10),
                 bg=SURFACE, fg=MUTED, pady=30).pack()

    # ── Corpus Loading ────────────────────────────────────────────────────────
    def _load_corpus_async(self):
        """Load corpus asynchronously with proper synchronization."""
        def load():
            try:
                with self._corpus_lock:
                    self.corpus = CorpusBuilder().build()
                    self.checker = SpellChecker(self.corpus)
                stats = self.corpus.get_stats()
                self._corpus_ready.set()
                self.after(0, self._on_corpus_loaded, stats)
            except Exception as e:
                import logging
                logging.error(f"Corpus load failed: {e}")
                self.after(0, lambda: messagebox.showerror("Load Error", str(e)))

        threading.Thread(target=load, daemon=True).start()

    def _on_corpus_loaded(self, stats):
        self.status_lbl.config(
            text=f"● {stats['total_tokens']:,} tokens · {stats['unique_words']} terms",
            fg=ACCENT)
        self.check_btn.config(state="normal")
        self._populate_corpus_stats(stats)
        self._filter_dict()

    def _populate_corpus_stats(self, stats):
        chips = [
            (str(stats['total_tokens']), "Tokens"),
            (str(stats['unique_words']), "Unique Words"),
            (str(stats['total_bigrams']), "Bigrams"),
            (f"{stats['total_tokens']/max(1,stats['unique_words']):.1f}×", "Avg Freq"),
        ]
        for val, lbl in chips:
            f = tk.Frame(self.corpus_stats_frame, bg=SURFACE2,
                          highlightthickness=1, highlightbackground=BORDER)
            f.pack(side="left", padx=(0, 8), ipadx=10, ipady=6)
            tk.Label(f, text=val, font=("Helvetica", 16, "bold"),
                     bg=SURFACE2, fg=ACCENT).pack()
            tk.Label(f, text=lbl, font=("Helvetica", 8),
                     bg=SURFACE2, fg=MUTED).pack()

    # ── Spell Check ───────────────────────────────────────────────────────────
    def _on_input_change(self, e=None):
        text = self.input_text.get("1.0", "end-1c")
        n = len(text)
        self.char_lbl.config(
            text=f"{n} / 500",
            fg=ACCENT3 if n > 490 else WARN if n > 400 else MUTED)

    def _run_check(self):
        if not self._corpus_ready.wait(timeout=0.5):
            messagebox.showinfo("LexiAI", "Corpus is still loading, please wait…")
            return
        with self._corpus_lock:
            if not self.checker:
                messagebox.showerror("Error", "Corpus failed to load")
                return
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showinfo("LexiAI", "Please enter some text to check.")
            return
        if len(text) > 500:
            text = text[:500]

        self.check_btn.config(text="⏳ Checking…", state="disabled")
        
        # Run spell check in background thread to prevent UI freezing
        check_thread = threading.Thread(target=self._do_check_async, args=(text,), daemon=True)
        check_thread.start()

    def _do_check_async(self, text):
        """Run spell check in background thread to avoid blocking UI."""
        try:
            result = self.checker.check(text)
            # Schedule UI update on main thread using after()
            self.after(0, self._on_check_complete, result)
        except Exception as e:
            import logging
            logging.error(f"Spell check failed: {e}")
            self.after(0, lambda: messagebox.showerror("Check Error", f"Failed: {str(e)}"))
        finally:
            # Always reset button, even if error occurs
            self.after(0, lambda: self.check_btn.config(text="▶  Check Spelling", state="normal"))

    def _on_check_complete(self, result):
        """Handle spell check completion on main thread."""
        self.current_errors = result['errors']
        self.selected_err_idx = -1
        self._render_result(result)
        self._render_err_panel(result['errors'])
        self._render_stats(result['errors'], result['original'])

    def _render_result(self, result):
        box = self.result_box
        box.configure(state="normal")
        box.delete("1.0", "end")

        if not result['errors']:
            box.insert("end", result['original'])
        else:
            err_map = {e['start']: e for e in result['errors']}
            i = 0
            text = result['original']
            err_idx_map = {e['start']: idx for idx, e in enumerate(result['errors'])}

            while i < len(text):
                if i in err_map:
                    e = err_map[i]
                    idx = err_idx_map[i]
                    tag = "err_nw" if e['type'] == 'non_word' else "err_rw"
                    start_pos = box.index("end-1c")
                    box.insert("end", e['word'], (tag, f"err_{idx}"))
                    # Bind click
                    box.tag_bind(f"err_{idx}", "<Button-1>",
                                 lambda ev, ix=idx: self.select_err(ix))
                    box.tag_bind(f"err_{idx}", "<Enter>",
                                 lambda ev: box.configure(cursor="hand2"))
                    box.tag_bind(f"err_{idx}", "<Leave>",
                                 lambda ev: box.configure(cursor="arrow"))
                    i = e['end']
                else:
                    box.insert("end", text[i])
                    i += 1

        box.configure(state="disabled")

    def _render_stats(self, errors, text):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        words = len([t for t in text.split() if t.isalpha()])
        nw = sum(1 for e in errors if e['type'] == 'non_word')
        rw = sum(1 for e in errors if e['type'] == 'real_word')
        chips = [(str(words), "words", TEXT),
                 (str(nw), "non-word", ACCENT3),
                 (str(rw), "real-word", WARN)]
        for val, lbl, col in chips:
            f = tk.Frame(self.stats_frame, bg=SURFACE2,
                          highlightthickness=1, highlightbackground=BORDER)
            f.pack(side="left", padx=(0, 6), ipadx=8, ipady=3)
            tk.Label(f, text=f"{val}  {lbl}", font=("Courier", 9),
                     bg=SURFACE2, fg=col).pack(padx=2)
        self.err_count_lbl.config(text=f"{len(errors)} error{'s' if len(errors)!=1 else ''}")

    def _render_err_panel(self, errors):
        for w in self.err_inner.winfo_children():
            w.destroy()

        if not errors:
            tk.Label(self.err_inner, text="✓  No errors detected!",
                     font=("Helvetica", 11, "bold"),
                     bg=SURFACE, fg=ACCENT, pady=20).pack()
            tk.Label(self.err_inner, text="Your text looks correct.",
                     font=("Helvetica", 9), bg=SURFACE, fg=MUTED).pack()
            return

        for idx, err in enumerate(errors):
            self._build_err_item(self.err_inner, err, idx)

        self.err_canvas.update_idletasks()
        self.err_canvas.configure(scrollregion=self.err_canvas.bbox("all"))

    def _build_err_item(self, parent, err, idx):
        is_nw = err['type'] == 'non_word'
        border_col = ACCENT3 if is_nw else WARN

        outer = tk.Frame(parent, bg=SURFACE2,
                          highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", padx=6, pady=(0, 6))
        outer.bind("<Button-1>", lambda e, i=idx: self.select_err(i))

        # Header
        hdr = tk.Frame(outer, bg=SURFACE3)
        hdr.pack(fill="x")
        tk.Label(hdr, text=err['word'], font=("Courier", 11, "bold"),
                 bg=SURFACE3, fg=TEXT, pady=6, padx=10).pack(side="left")
        badge_bg = ERR_NW_BG if is_nw else ERR_RW_BG
        badge_fg = ACCENT3 if is_nw else WARN
        badge_text = "NON-WORD" if is_nw else "REAL-WORD"
        tk.Label(hdr, text=badge_text, font=("Courier", 8, "bold"),
                 bg=badge_bg, fg=badge_fg, padx=6, pady=4).pack(side="right", padx=6)

        # Suggestions
        for sug in err['suggestions'][:5]:
            self._build_sug_btn(outer, err, idx, sug)

        # Tag for selection highlight
        outer.idx = idx
        self._err_item_widgets = getattr(self, '_err_item_widgets', {})
        self._err_item_widgets[idx] = outer

    def _build_sug_btn(self, parent, err, err_idx, sug):
        row = tk.Frame(parent, bg=SURFACE2, cursor="hand2")
        row.pack(fill="x", padx=6, pady=2)

        lbl = tk.Label(row, text=sug['word'], font=("Courier", 10, "bold"),
                       bg=SURFACE2, fg=ACCENT, padx=8, pady=4, anchor="w")
        lbl.pack(side="left", fill="x", expand=True)

        meta = tk.Label(row, text=f"MED:{sug['med']}  p:{sug['lm_prob']:.1e}",
                        font=("Courier", 8), bg=SURFACE2, fg=MUTED, padx=8)
        meta.pack(side="right")

        def apply_sug(ev=None, e=err, si=err_idx, sw=sug['word']):
            self._apply_suggestion(e, si, sw)

        for widget in (row, lbl, meta):
            widget.bind("<Button-1>", apply_sug)
            widget.bind("<Enter>", lambda ev, r=row: r.configure(bg=SURFACE3))
            widget.bind("<Leave>", lambda ev, r=row: r.configure(bg=SURFACE2))

    def select_err(self, idx):
        self.selected_err_idx = idx
        # Highlight in result box
        box = self.result_box
        box.configure(state="normal")
        for i, err in enumerate(self.current_errors):
            base_tag = "err_nw" if err['type'] == 'non_word' else "err_rw"
            sel_tag  = "err_nw_sel" if err['type'] == 'non_word' else "err_rw_sel"
            box.tag_remove(sel_tag, "1.0", "end")
            if i == idx:
                box.tag_add(sel_tag, f"1.0", "end")
        box.configure(state="disabled")
        # Highlight error item border
        self._err_item_widgets = getattr(self, '_err_item_widgets', {})
        for i, widget in self._err_item_widgets.items():
            col = ACCENT if i == idx else BORDER
            widget.configure(highlightbackground=col)

    def _apply_suggestion(self, err, err_idx, suggestion):
        # Restore original casing
        corrected = suggestion
        if err['word'] and err['word'][0].isupper():
            corrected = suggestion[0].upper() + suggestion[1:]

        # Replace in input box
        text = self.input_text.get("1.0", "end-1c")
        new_text = text[:err['start']] + corrected + text[err['end']:]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", new_text)
        self._run_check()

    def _clear_all(self):
        self.input_text.delete("1.0", "end")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.configure(state="disabled")
        for w in self.stats_frame.winfo_children():
            w.destroy()
        self.err_count_lbl.config(text="—")
        self.current_errors = []
        self._show_err_placeholder("Click \"Check Spelling\" to begin")
        self._on_input_change()

    # ── MED Visualizer ────────────────────────────────────────────────────────
    def _run_med(self):
        src = self.med_src.get().lower().strip()
        tgt = self.med_tgt.get().lower().strip()
        src = ''.join(c for c in src if c.isalpha())
        tgt = ''.join(c for c in tgt if c.isalpha())

        if not src and not tgt:
            self.med_score_lbl.config(text="")
            self.med_score_desc.config(text="")
            return

        from corrector import MinEditDistance
        med = MinEditDistance()
        dist = med.distance(src, tgt)
        _, ops = med.alignment(src, tgt)

        self.med_score_lbl.config(text=str(dist))
        self.med_score_desc.config(
            text=f"Edit Distance\n\"{src}\"  →  \"{tgt}\"")

        self._draw_med_matrix(src, tgt, dist, ops)

    def _draw_med_matrix(self, src, tgt, dist, ops):
        canvas = self.med_canvas
        canvas.delete("all")

        n, m = len(src), len(tgt)
        cell = 36
        pad = 24
        cols = m + 2
        rows = n + 2

        total_w = cols * cell + pad * 2
        total_h = rows * cell + pad * 2
        canvas.configure(scrollregion=(0, 0, total_w, total_h))

        from corrector import MinEditDistance
        med = MinEditDistance()
        res = med.distance(src, tgt)
        dp = res  # re-run to get dp matrix
        # Build dp directly
        ins_c, del_c, sub_c, tra_c = 1, 1, 2, 1
        nn, mm = len(src), len(tgt)
        dp2 = [[0]*(mm+1) for _ in range(nn+1)]
        for i in range(nn+1): dp2[i][0] = i*del_c
        for j in range(mm+1): dp2[0][j] = j*ins_c
        for i in range(1,nn+1):
            for j in range(1,mm+1):
                if src[i-1]==tgt[j-1]: dp2[i][j]=dp2[i-1][j-1]
                else:
                    dp2[i][j]=min(dp2[i-1][j-1]+sub_c,dp2[i][j-1]+ins_c,dp2[i-1][j]+del_c)
                    if i>1 and j>1 and src[i-1]==tgt[j-2] and src[i-2]==tgt[j-1]:
                        dp2[i][j]=min(dp2[i][j],dp2[i-2][j-2]+tra_c)

        max_val = max(max(row) for row in dp2) or 1

        def cell_color(val):
            ratio = val / max_val
            r = int(0x1e + ratio * (0x4f - 0x1e))
            g = int(0x23 + ratio * (0xff - 0x23))
            b = int(0x30 + ratio * (0xb0 - 0x30))
            return f"#{r:02x}{g:02x}{b:02x}"

        src_chars = ['ε'] + list(src)
        tgt_chars = ['ε'] + list(tgt)

        for i in range(nn+1):
            for j in range(mm+1):
                x = pad + (j+1) * cell
                y = pad + (i+1) * cell
                val = dp2[i][j]
                is_diag = (i == nn and j == mm)
                bg = "#4fffb033" if is_diag else cell_color(val)

                canvas.create_rectangle(x, y, x+cell, y+cell,
                                         fill=SURFACE3, outline=BORDER)
                txt_col = ACCENT if is_diag else TEXT
                canvas.create_text(x+cell//2, y+cell//2,
                                    text=str(val), fill=txt_col,
                                    font=("Courier", 9, "bold" if is_diag else "normal"))

        # Row/col headers
        for j, ch in enumerate(tgt_chars):
            x = pad + (j+1)*cell + cell//2
            canvas.create_text(x, pad + cell//2, text=ch,
                                fill=MUTED, font=("Courier", 10, "bold"))

        for i, ch in enumerate(src_chars):
            y = pad + (i+1)*cell + cell//2
            canvas.create_text(pad + cell//2, y, text=ch,
                                fill=MUTED, font=("Courier", 10, "bold"))

    # ── Corpus Dictionary ─────────────────────────────────────────────────────
    def _filter_dict(self):
        if not self.corpus:
            return
        q = self.dict_search_var.get().lower()
        sort = self.sort_var.get()
        words = [(w, f) for w, f in self.corpus.word_freq.items()
                 if not q or q in w]
        if sort == "freq":
            words.sort(key=lambda x: -x[1])
        elif sort == "alpha":
            words.sort(key=lambda x: x[0])
        elif sort == "len":
            words.sort(key=lambda x: -len(x[0]))

        lb = self.dict_listbox
        lb.delete(0, "end")
        for w, f in words[:600]:
            lb.insert("end", f"  {w:<28} {f:>4}×")
        if len(words) > 600:
            lb.insert("end", f"  … {len(words)-600} more — refine search")

    # ── Tab change ────────────────────────────────────────────────────────────
    def _on_tab_change(self, e):
        tab = self.nb.tab(self.nb.select(), "text").strip()
        if "Corpus" in tab and self.corpus:
            self._filter_dict()
        if "Edit" in tab:
            self._run_med()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = LexiAIApp()
    app.mainloop()
