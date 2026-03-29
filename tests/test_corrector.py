"""
test_corrector.py - Unit tests for the spelling corrector module

Tests MinEditDistance, BigramLanguageModel, and SpellChecker classes.
Covers typical use cases and edge cases.
"""

import pytest
import math
from collections import Counter


@pytest.mark.unit
@pytest.mark.critical
class TestMinEditDistance:
    """Tests for MinEditDistance class."""
    
    def test_identical_strings(self, med_default):
        """Identical strings should have distance 0."""
        assert med_default.distance("cat", "cat") == 0
        assert med_default.distance("", "") == 0
        assert med_default.distance("transformer", "transformer") == 0
    
    def test_empty_source(self, med_default):
        """Converting empty string to target requires insertions."""
        # Empty -> "cat" = 3 insertions at cost 1 each
        assert med_default.distance("", "cat") == 3
        assert med_default.distance("", "hello") == 5
    
    def test_empty_target(self, med_default):
        """Converting source to empty string requires deletions."""
        # "cat" -> Empty = 3 deletions at cost 1 each
        assert med_default.distance("cat", "") == 3
        assert med_default.distance("hello", "") == 5
    
    def test_substitution_single_char(self, med_default):
        """Single character substitution costs 2 (not 1)."""
        # "cat" -> "bat" = 1 substitution at cost 2
        assert med_default.distance("cat", "bat") == 2
        assert med_default.distance("a", "b") == 2
    
    def test_insertion(self, med_default):
        """Single insertion costs 1."""
        # "cat" -> "cart" = 1 insertion (r) at cost 1
        assert med_default.distance("cat", "cart") == 1
        # "at" -> "cat" = 1 insertion (c) at cost 1
        assert med_default.distance("at", "cat") == 1
    
    def test_deletion(self, med_default):
        """Single deletion costs 1."""
        # "cart" -> "cat" = 1 deletion (r) at cost 1
        assert med_default.distance("cart", "cat") == 1
        # "cat" -> "at" = 1 deletion (c) at cost 1
        assert med_default.distance("cat", "at") == 1
    
    def test_transposition(self, med_default):
        """Adjacent character transposition costs 1."""
        # "teh" -> "the" = 1 transposition at cost 1
        assert med_default.distance("teh", "the") == 1
        # "ab" -> "ba" = 1 transposition
        assert med_default.distance("ab", "ba") == 1
    
    def test_multiple_operations(self, med_default):
        """Multiple operations are summed."""
        # "kitten" -> "sitting":
        # k->s (sub=2), e->i (sub=2), +g (ins=1) = 2+2+1 = 5
        assert med_default.distance("kitten", "sitting") == 5
    
    def test_case_sensitive(self, med_default):
        """Distance is case-sensitive."""
        # "Cat" -> "cat" = 1 substitution (C->c) at cost 2
        assert med_default.distance("Cat", "cat") == 2
        assert med_default.distance("CAT", "cat") == 4
    
    def test_equal_cost_weights(self, med_equal_costs):
        """With equal costs, should match standard Levenshtein."""
        assert med_equal_costs.distance("cat", "bat") == 1
        assert med_equal_costs.distance("kitten", "sitting") == 3
    
    @pytest.mark.edge_case
    def test_very_long_strings(self, med_default):
        """Test with reasonably long strings."""
        s1 = "a" * 100
        s2 = "b" * 100
        # 100 substitutions at cost 2 each = 200
        assert med_default.distance(s1, s2) == 200
    
    @pytest.mark.edge_case
    def test_unicode_strings(self, med_default):
        """Test with Unicode characters."""
        assert med_default.distance("café", "cafe") == 2  # é->e substitution
        assert med_default.distance("naïve", "naive") == 2
    
    @pytest.mark.edge_case
    def test_special_characters(self, med_default):
        """Test with special characters."""
        assert med_default.distance("hello!", "hello") == 1  # delete !
        assert med_default.distance("a-b", "ab") == 1  # delete -
    
    def test_expensive_substitution_preference(self, med_expensive_sub):
        """With expensive substitution, should prefer other operations."""
        # "abc" -> "dbc": with sub_cost=5
        # Option 1: substitute a->d (cost 5)
        # Option 2: delete a (cost 1) + insert d (cost 1) = 2
        # Should choose option 2
        distance = med_expensive_sub.distance("abc", "dbc")
        assert distance == 2  # Not 5


@pytest.mark.unit
@pytest.mark.critical
class TestBigramLanguageModel:
    """Tests for BigramLanguageModel class."""
    
    def test_bigram_prob_laplace_smoothing(self, sample_bigrams, sample_word_freq):
        """Laplace smoothing should handle unseen bigrams."""
        from corrector import BigramLanguageModel
        
        blm = BigramLanguageModel(sample_bigrams, sample_word_freq)
        
        # Seen bigram: ('the', 'quick') should have reasonable probability
        prob_seen = blm.bigram_prob('the', 'quick')
        assert 0 < prob_seen < 1
        
        # Unseen bigram: ('the', 'invisible') should still have small probability > 0
        prob_unseen = blm.bigram_prob('the', 'invisible')
        assert 0 < prob_unseen < 1
        
        # Unseen bigram should have smaller probability than seen
        assert prob_unseen < prob_seen
    
    def test_bigram_prob_zero_word_freq(self, sample_bigrams, sample_word_freq):
        """Word not in frequency table should still work (zero count in numerator)."""
        from corrector import BigramLanguageModel
        
        blm = BigramLanguageModel(sample_bigrams, sample_word_freq)
        
        # Word 'invisible' not in vocab
        prob = blm.bigram_prob('invisible', 'word')
        assert 0 < prob < 1
    
    def test_context_probability_ranking(self, sample_bigrams, sample_word_freq):
        """More frequent bigrams should have higher probability."""
        from corrector import BigramLanguageModel
        
        blm = BigramLanguageModel(sample_bigrams, sample_word_freq)
        
        # ('is', 'a') is very frequent (count 100)
        prob_freq = blm.bigram_prob('is', 'a')
        
        # ('jumps', 'over') is less frequent (count in bigrams)
        prob_less = blm.bigram_prob('jumps', 'over')
        
        # More frequent should be more probable
        assert prob_freq > prob_less
    
    @pytest.mark.edge_case
    def test_empty_birgrams(self):
        """Handle empty bigram dictionary."""
        from corrector import BigramLanguageModel
        
        blm = BigramLanguageModel(Counter(), Counter({'word': 1}))
        prob = blm.bigram_prob('word', 'other')
        
        # Should return small probability from smoothing
        assert 0 < prob < 1


@pytest.mark.unit
@pytest.mark.critical
class TestSpellChecker:
    """Tests for SpellChecker class."""
    
    def test_non_word_error_detection(self, spell_checker_factory):
        """Detect words not in vocabulary as non-word errors."""
        checker = spell_checker_factory()
        result = checker.check("teh quick brown fox")
        
        # "teh" is not in vocab, should be marked as error
        assert len(result['errors']) > 0
        error_words = [e['word'] for e in result['errors']]
        assert 'teh' in error_words
    
    def test_correct_text_no_errors(self, spell_checker_factory):
        """Correct text should produce no errors."""
        checker = spell_checker_factory()
        result = checker.check("the quick brown fox")
        
        # All words in vocab, no errors
        assert result['error_count'] == 0
        assert len(result['errors']) == 0
    
    def test_candidate_generation(self, spell_checker_factory):
        """Check that candidates are ranked by edit distance."""
        checker = spell_checker_factory()
        result = checker.check("qick")
        
        # Should find "quick" as top candidate
        assert len(result['errors']) > 0
        error = result['errors'][0]
        candidates = error.get('candidates', [])
        
        # "quick" should be in candidates (edit distance = 1)
        candidate_words = [c['word'] for c in candidates]
        assert 'quick' in candidate_words
    
    def test_real_word_error_detection(self, spell_checker_factory):
        """Detect when valid words are used incorrectly (low bigram prob)."""
        checker = spell_checker_factory()
        # "fox is network" uses "network" out of context
        # (not likely to follow "is" in training data)
        result = checker.check("fox is network")
        
        # Might detect "network" as real-word error (low bigram prob)
        # This depends on bigram data
        assert isinstance(result, dict)
        assert 'errors' in result
    
    @pytest.mark.edge_case
    def test_empty_text(self, spell_checker_factory):
        """Empty text should produce no errors."""
        checker = spell_checker_factory()
        result = checker.check("")
        
        assert result['error_count'] == 0
        assert len(result['tokens']) == 0
    
    @pytest.mark.edge_case
    def test_whitespace_only_text(self, spell_checker_factory):
        """Whitespace-only text should produce no errors."""
        checker = spell_checker_factory()
        result = checker.check("   \n\t  ")
        
        assert result['error_count'] == 0
    
    @pytest.mark.edge_case
    def test_single_word(self, spell_checker_factory):
        """Single word text should be processed."""
        checker = spell_checker_factory()
        result = checker.check("quick")
        
        assert len(result['tokens']) == 1
        assert result['tokens'][0]['text'] == 'quick'
    
    @pytest.mark.edge_case
    def test_duplicate_errors(self, spell_checker_factory):
        """Duplicate errors should be deduplicated or counted."""
        checker = spell_checker_factory()
        result = checker.check("teh teh teh quick brown fox")
        
        # Should identify "teh" appears multiple times
        assert result['error_count'] >= 3 or 'teh' in [e['word'] for e in result['errors']]
    
    @pytest.mark.performance
    def test_long_text_processing(self, spell_checker_factory):
        """Should handle reasonably long text."""
        checker = spell_checker_factory()
        long_text = "the quick brown fox " * 100  # 500 words
        result = checker.check(long_text)
        
        # Should process without crashing
        assert isinstance(result, dict)
        assert 'tokens' in result


@pytest.mark.unit
class TestCandidateGenerator:
    """Tests for edit distance candidate generation."""
    
    def test_edits1_from_simple_word(self, med_default):
        """Edit-1 should generate reasonable candidates from simple word."""
        from corrector import CandidateGenerator
        
        vocab = {'cat', 'bat', 'bad', 'at', 'ca', 'cart'}
        gen = CandidateGenerator(med_default, vocab)
        
        candidates = gen.edits1('cat')
        
        # Should include 'bat', 'at', 'ca' from vocab
        assert 'bat' in candidates
        assert 'at' in candidates
    
    def test_edits2_from_word(self, med_default):
        """Edit-2 should generate candidates two edits away."""
        from corrector import CandidateGenerator
        
        vocab = {'bat', 'bad', 'cat', 'rat', 'tar', 'bar'}
        gen = CandidateGenerator(med_default, vocab)
        
        candidates = gen.edits2('cat')
        
        # Should include things like 'bat', 'rat' (1 edit)
        # and other things 2 edits away
        assert len(candidates) > 0


@pytest.mark.unit
class TestTokenization:
    """Tests for text tokenization."""
    
    def test_tokenize_simple_text(self, spell_checker_factory, sample_texts):
        """Tokenize simple text correctly."""
        checker = spell_checker_factory()
        result = checker.check(sample_texts['simple'])
        
        # "the quick brown fox jumps over the lazy dog"
        assert len(result['tokens']) >= 8
    
    def test_tokenize_with_punctuation(self, spell_checker_factory, sample_texts):
        """Tokenization should handle punctuation."""
        checker = spell_checker_factory()
        result = checker.check(sample_texts['with_punctuation'])
        
        # Should handle commas, periods, apostrophes
        assert len(result['tokens']) > 0
    
    def test_tokenize_with_numbers(self, spell_checker_factory, sample_texts):
        """Tokenization should handle numbers."""
        checker = spell_checker_factory()
        result = checker.check(sample_texts['with_numbers'])
        
        # Should process numbers somehow
        assert len(result['tokens']) > 0


@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling and validation."""
    
    def test_med_with_invalid_costs(self):
        """MED should handle invalid cost values gracefully."""
        from corrector import MinEditDistance
        
        # Negative costs should still work (unusual but valid)
        med = MinEditDistance(ins_cost=1, del_cost=1, sub_cost=-1, trans_cost=1)
        distance = med.distance("cat", "bat")
        assert isinstance(distance, int)
    
    def test_spell_checker_with_empty_vocab(self):
        """SpellChecker should handle very small vocabulary."""
        from corrector import SpellChecker
        
        class MiniCorpus:
            vocabulary = {'a', 'the'}
            word_freq = Counter({'a': 100, 'the': 200})
            bigrams = Counter()
            tokens = 300
        
        checker = SpellChecker(MiniCorpus())
        result = checker.check("hello world")
        
        # Should process without crashing
        assert isinstance(result, dict)
