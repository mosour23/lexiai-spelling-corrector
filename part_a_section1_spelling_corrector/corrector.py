"""
corrector.py - Probabilistic Spelling Correction Engine
Implements:
  1. Non-word error detection via vocabulary lookup
  2. Real-word error detection via Bigram language model
  3. Candidate generation via keyboard proximity + edit operations
  4. Ranking via Minimum Edit Distance + Bigram probability
"""

import re
import math
from collections import Counter, defaultdict


# ─── Keyboard Layout for Typo-Aware Candidate Generation ────────────────────
KEYBOARD_NEIGHBORS = {
    'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'esxcfr', 'e': 'wsdr',
    'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujbn', 'i': 'ujko', 'j': 'huikmn',
    'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
    'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
    'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
    'z': 'asx'
}


class MinEditDistance:
    """
    Computes minimum edit distance (Levenshtein) between two strings.
    Supports weighted operations: insert, delete, substitute, transpose.
    """
    
    MAX_MED_LENGTH = 1000

    def __init__(self, ins_cost=1, del_cost=1, sub_cost=2, trans_cost=1):
        self.ins_cost = ins_cost
        self.del_cost = del_cost
        self.sub_cost = sub_cost
        self.trans_cost = trans_cost

    def distance(self, source: str, target: str) -> int:
        """Compute weighted edit distance with allocation bounds."""
        if len(source) > self.MAX_MED_LENGTH or len(target) > self.MAX_MED_LENGTH:
            return abs(len(source) - len(target))
        n, m = len(source), len(target)
        # Initialize DP matrix
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = i * self.del_cost
        for j in range(m + 1):
            dp[0][j] = j * self.ins_cost

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if source[i-1] == target[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    sub = dp[i-1][j-1] + self.sub_cost
                    ins = dp[i][j-1] + self.ins_cost
                    dele = dp[i-1][j] + self.del_cost
                    dp[i][j] = min(sub, ins, dele)
                    # Transposition (Damerau extension)
                    if (i > 1 and j > 1 and
                            source[i-1] == target[j-2] and
                            source[i-2] == target[j-1]):
                        dp[i][j] = min(dp[i][j], dp[i-2][j-2] + self.trans_cost)

        return dp[n][m]

    def alignment(self, source: str, target: str):
        """Return the edit distance and alignment path for visualization."""
        n, m = len(source), len(target)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        ops = [[''] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i * self.del_cost
            ops[i][0] = 'D' * i
        for j in range(m + 1):
            dp[0][j] = j * self.ins_cost
            ops[0][j] = 'I' * j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if source[i-1] == target[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                    ops[i][j] = 'M'
                else:
                    candidates = [
                        (dp[i-1][j-1] + self.sub_cost, 'S'),
                        (dp[i][j-1] + self.ins_cost, 'I'),
                        (dp[i-1][j] + self.del_cost, 'D'),
                    ]
                    best_cost, best_op = min(candidates)
                    dp[i][j] = best_cost
                    ops[i][j] = best_op

        return dp[n][m], ops


class BigramLanguageModel:
    """
    Bigram language model with Laplace (add-1) smoothing.
    Used for real-word error detection and candidate ranking.
    """

    def __init__(self, word_freq: Counter, bigrams: Counter, vocab: set):
        self.word_freq = word_freq
        self.bigrams = bigrams
        self.vocab = vocab
        self.vocab_size = len(vocab)
        self.total_tokens = sum(word_freq.values())

    def unigram_prob(self, word: str) -> float:
        """Laplace-smoothed unigram probability."""
        count = self.word_freq.get(word, 0)
        return (count + 1) / (self.total_tokens + self.vocab_size)

    def bigram_prob(self, w1: str, w2: str) -> float:
        """Laplace-smoothed bigram probability P(w2 | w1)."""
        bigram_count = self.bigrams.get((w1, w2), 0)
        w1_count = self.word_freq.get(w1, 0)
        return (bigram_count + 1) / (w1_count + self.vocab_size)

    def sentence_log_prob(self, tokens: list) -> float:
        """Compute log probability of a token sequence."""
        if not tokens:
            return float('-inf')
        log_prob = math.log(self.unigram_prob(tokens[0]))
        for i in range(1, len(tokens)):
            log_prob += math.log(self.bigram_prob(tokens[i-1], tokens[i]))
        return log_prob

    def is_real_word_error(self, tokens: list, idx: int, threshold: float = 2.5) -> bool:
        """
        Detect real-word errors by comparing bigram probability of the
        current word in context to an expected threshold.

        Guard: high-frequency words (common English vocab) are never flagged —
        their low bigram probability against AI/NLP neighbours is expected, not erroneous.
        """
        word = tokens[idx]
        if word not in self.vocab:
            return False  # Non-word error, handled separately

        # Guard: skip high-frequency words — common English words have naturally
        # low bigram probability in a domain corpus, not because they are errors.
        freq = self.word_freq.get(word, 0)
        freq_threshold = self.total_tokens / self.vocab_size * 1.5
        if freq >= freq_threshold:
            return False

        context_probs = []
        if idx > 0:
            context_probs.append(self.bigram_prob(tokens[idx-1], word))
        if idx < len(tokens) - 1:
            context_probs.append(self.bigram_prob(word, tokens[idx+1]))

        if not context_probs:
            return False

        avg_prob = sum(context_probs) / len(context_probs)
        # Low bigram probability signals likely real-word error
        return avg_prob < (1 / (self.vocab_size ** 0.6))


class CandidateGenerator:
    """Generates correction candidates using edit operations + keyboard proximity."""

    def __init__(self, vocab: set):
        self.vocab = vocab
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def edits1(self, word: str) -> set:
        """Generate all strings one edit away, filtered by vocabulary."""
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        # Step 1: Generate raw candidates
        deletes = {L + R[1:] for L, R in splits if R}
        transposes = {L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1}
        replaces = {L + c + R[1:] for L, R in splits if R for c in self.alphabet}
        inserts = {L + c + R for L, R in splits for c in self.alphabet}
        kb_replaces = set()
        for L, R in splits:
            if R:
                neighbors = KEYBOARD_NEIGHBORS.get(R[0], '')
                kb_replaces.update({L + c + R[1:] for c in neighbors})
        
        # Step 2: Filter by vocabulary - ONLY keep words in vocab
        raw_candidates = deletes | transposes | replaces | inserts | kb_replaces
        valid_candidates = raw_candidates & self.vocab
        
        # Step 3: Explicitly remove the original misspelled word
        valid_candidates.discard(word)
        
        return valid_candidates

    def edits2(self, word: str) -> set:
        """Generate bounded set of edit-2 candidates, filtered by vocabulary."""
        MAX_EDIT_2 = 500
        e1 = self.edits1(word)
        if not e1:
            return set()
        
        # Step 1: Generate raw edit-2 candidates by applying edits1 to edit-1 words
        raw_candidates = set()
        for e1_word in sorted(e1):
            if len(raw_candidates) >= MAX_EDIT_2:
                break
            for e2_word in self.edits1(e1_word):
                raw_candidates.add(e2_word)
                if len(raw_candidates) >= MAX_EDIT_2:
                    break
        
        # Step 2: Filter by vocabulary - ONLY keep words in vocab
        valid_candidates = raw_candidates & self.vocab
        
        # Step 3: Explicitly remove the original misspelled word
        valid_candidates.discard(word)
        
        return valid_candidates

    def candidates(self, word: str) -> set:
        """Return candidates: prefer edit-1, fallback to edit-2.
        Both sets are already filtered by vocabulary and have original word removed.
        """
        e1 = self.edits1(word)
        if e1:
            return e1
        e2 = self.edits2(word)
        if e2:
            return e2
        return set()  # Return empty set if no valid candidates available


class SpellChecker:
    """
    Main spelling correction system combining all components.
    Detects non-word errors and real-word errors.
    Ranks candidates using MED + bigram probability.
    """
    
    MAX_INPUT_LENGTH = 50000

    def __init__(self, corpus_builder):
        self.corpus = corpus_builder
        self.med = MinEditDistance(ins_cost=1, del_cost=1, sub_cost=2, trans_cost=1)
        self.lm = BigramLanguageModel(
            corpus_builder.word_freq,
            corpus_builder.bigrams,
            corpus_builder.vocabulary
        )
        self.gen = CandidateGenerator(corpus_builder.vocabulary)

    def tokenize_input(self, text: str) -> list:
        """Tokenize input preserving original case and positions."""
        pattern = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)*|[^a-zA-Z\s]+|\s+")
        tokens = []
        for match in pattern.finditer(text):
            tokens.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'is_word': bool(re.match(r"[a-zA-Z]", match.group()))
            })
        return tokens

    def rank_candidates(self, word: str, candidates: set,
                        prev_word: str = None, next_word: str = None,
                        top_n: int = 5) -> list:
        """
        Rank candidates following explicit flow:
        1. Filter candidates: ONLY keep valid vocabulary words
        2. Explicitly remove original misspelled word (defense-in-depth)
        3. Sort by (edit_distance, -frequency/probability)
        4. Return formatted list
        
        PRIMARY sort key: Edit Distance (lower is better)
        SECONDARY sort key: Probability (higher is better, for tie-breaking only)
        """
        word_lower = word.lower()
        
        # Step 1-2: Create valid candidate set, ensuring original word excluded
        valid_candidates = set(candidates)  # Copy input set
        valid_candidates.discard(word_lower)  # Explicit removal
        
        if not valid_candidates:
            # No valid candidates available
            return []
        
        # Step 3: Score and sort candidates
        scored = []
        for cand in valid_candidates:
            # PRIMARY: Minimum Edit Distance (strict primary sort key)
            med_score = self.med.distance(word_lower, cand)
            
            # SECONDARY: Compute probability for tie-breaking only
            # Get unigram probability
            unigram_prob = self.lm.unigram_prob(cand)
            ctx_log_prob = math.log(unigram_prob)
            
            # Add context bigram probabilities if available
            if prev_word:
                ctx_log_prob += math.log(self.lm.bigram_prob(prev_word.lower(), cand))
            if next_word:
                ctx_log_prob += math.log(self.lm.bigram_prob(cand, next_word.lower()))
            
            # Convert log probability to probability for sorting
            num_context_words = int(bool(prev_word)) + int(bool(next_word)) + 1
            lm_prob = math.exp(ctx_log_prob / max(1, num_context_words))
            
            scored.append({
                'word': cand,
                'med': med_score,
                'lm_prob': lm_prob,
                'score': (med_score, -lm_prob)  # Tuple: (primary, secondary)
            })
        
        # Sort by tuple: (edit_distance, -probability)
        # Python compares tuples element-wise: first by edit_distance (ascending),
        # then by -probability (ascending, which means highest probability wins)
        scored.sort(key=lambda x: x['score'])
        
        # Step 4: Return formatted list
        return scored[:top_n]

    def check(self, text: str) -> dict:
        """
        Full spell-check pipeline with input validation.
        Returns list of errors with positions and ranked suggestions.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be string")
        if len(text) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"Input exceeds {self.MAX_INPUT_LENGTH} chars")
        if not text.strip():
            return {'original': text, 'tokens': [], 'errors': [], 'error_count': 0}
        
        tokens = self.tokenize_input(text)
        word_tokens = [t for t in tokens if t['is_word']]
        errors = []

        for i, tok in enumerate(word_tokens):
            word = tok['text']
            word_lower = word.lower()
            prev_word = word_tokens[i-1]['text'] if i > 0 else None
            next_word = word_tokens[i+1]['text'] if i < len(word_tokens)-1 else None

            error_type = None

            # 1. Non-word error: not in vocabulary
            if word_lower not in self.corpus.vocabulary:
                # Skip: numbers, single chars, proper nouns (all-caps abbreviations)
                if len(word) > 1 and not re.match(r'^\d+$', word) and not (word.isupper() and len(word) <= 4):
                    error_type = 'non_word'

            # 2. Real-word error: in vocabulary but contextually wrong
            elif len(word_tokens) > 1:
                lm_tokens = [t['text'].lower() for t in word_tokens]
                if self.lm.is_real_word_error(lm_tokens, i):
                    error_type = 'real_word'

            if error_type:
                candidates = self.gen.candidates(word_lower)
                suggestions = self.rank_candidates(word, candidates, prev_word, next_word)
                errors.append({
                    'word': word,
                    'start': tok['start'],
                    'end': tok['end'],
                    'type': error_type,
                    'suggestions': suggestions
                })

        return {
            'original': text,
            'tokens': tokens,
            'errors': errors,
            'error_count': len(errors)
        }

    def get_med_detail(self, source: str, target: str) -> dict:
        """Get detailed MED alignment for visualization."""
        dist, ops = self.med.alignment(source.lower(), target.lower())
        return {'source': source, 'target': target, 'distance': dist, 'ops': ops}


if __name__ == "__main__":
    from corpus import CorpusBuilder
    cb = CorpusBuilder().build()
    sc = SpellChecker(cb)

    test = "The tokinization proccess uses contextual embedings for sematic retrival."
    result = sc.check(test)
    print(f"\nText: {test}")
    print(f"Errors found: {result['error_count']}")
    for e in result['errors']:
        print(f"  [{e['type']}] '{e['word']}' → {[s['word'] for s in e['suggestions'][:3]]}")
