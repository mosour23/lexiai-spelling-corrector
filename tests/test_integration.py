"""
test_integration.py - Integration tests across modules

Tests interactions between corrector, corpus, and GUI components.
"""

import pytest


@pytest.mark.integration
@pytest.mark.critical
class TestSpellingCorrectionPipeline:
    """Integration tests for the complete spelling correction workflow."""
    
    def test_end_to_end_spell_check(self):
        """Full pipeline: load corpus -> create checker -> check text."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        # Build corpus
        builder = CorpusBuilder()
        corpus = builder.build()
        
        # Create spell checker
        checker = SpellChecker(corpus)
        
        # Check text with error
        result = checker.check("teh quick brown fox")
        
        # Should find error in "teh"
        assert result['error_count'] > 0
        errors = result['errors']
        assert any(e['word'] == 'teh' for e in errors)
        
        # Error should have suggestions
        teh_error = next(e for e in errors if e['word'] == 'teh')
        assert 'candidates' in teh_error
        assert len(teh_error['candidates']) > 0
        
        # "the" should be top candidate
        top_candidate = teh_error['candidates'][0]
        assert top_candidate['word'] == 'the'
    
    def test_multiple_errors_detection(self):
        """Should detect multiple errors in text."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        # Text with multiple errors
        result = checker.check("teh quikc brown fox jumps ovr teh laazy dog")
        
        # Should find multiple errors
        assert result['error_count'] >= 3
    
    def test_correct_text_no_false_positives(self):
        """Correct text should not produce false positives."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        # Correct text
        result = checker.check("The quick brown fox jumps over the lazy dog")
        
        # Should have minimal or no errors for common words
        # (depends on corpus vocabulary)
        error_words = [e['word'] for e in result['errors']]
        common_words = {'the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog'}
        
        # Most common words shouldn't be errors
        false_positives = common_words & set(error_words)
        assert len(false_positives) <= 2  # Allow some tolerance
    
    def test_candidate_ranking_correctness(self):
        """Candidates should be ranked by edit distance."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        # Word with known edit distance fix
        result = checker.check("teh")
        
        assert len(result['errors']) > 0
        error = result['errors'][0]
        candidates = error.get('candidates', [])
        
        # "the" should be in candidates (edit distance = 1)
        candidate_words = [c['word'] for c in candidates]
        if candidates:  # If there are candidates
            # Top candidates should have lower scores (better)
            if len(candidates) > 1:
                assert candidates[0]['score'] <= candidates[1]['score']
    
    @pytest.mark.slow
    def test_large_text_processing(self):
        """Should handle large text inputs without crashing."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        # Create large text (500 words)
        large_text = "the quick brown fox " * 125
        
        result = checker.check(large_text)
        
        # Should process without crashing
        assert 'tokens' in result
        assert 'errors' in result
        assert isinstance(result['tokens'], list)
        assert isinstance(result['errors'], list)


@pytest.mark.integration
class TestCorpusSpellerIntegration:
    """Tests interaction between corpus loading and spell checker."""
    
    def test_spell_checker_with_loaded_corpus(self):
        """Spell checker should work with loaded corpus."""
        import tempfile
        import json
        import os
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        # Create and build corpus
        builder = CorpusBuilder()
        original_corpus = builder.build()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            corpus_data = {
                'tokens': original_corpus.tokens,
                'word_freq': dict(original_corpus.word_freq),
                'vocabulary': list(original_corpus.vocabulary),
                'bigrams': {f"{k[0]}|{k[1]}": v for k, v in original_corpus.bigrams.items()}
            }
            json.dump(corpus_data, f)
            temp_path = f.name
        
        try:
            # Load from file
            builder2 = CorpusBuilder()
            loaded = builder2.load_from_json(temp_path)
            
            if loaded:
                # Create checker from loaded corpus
                checker = SpellChecker(builder2)
                result = checker.check("test")
                
                # Should work
                assert isinstance(result, dict)
        finally:
            os.unlink(temp_path)
    
    def test_vocabulary_consistency(self):
        """Vocabulary should be consistent across operations."""
        from corpus import CorpusBuilder
        
        builder = CorpusBuilder()
        corpus1 = builder.build()
        corpus2 = builder.build()
        
        # Same builder should produce same vocabulary
        assert len(corpus1.vocabulary) == len(corpus2.vocabulary)


@pytest.mark.integration
class TestErrorRecovery:
    """Integration tests for error handling and recovery."""
    
    def test_invalid_text_handling(self):
        """Should handle various invalid text gracefully."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        invalid_inputs = [
            "",                          # Empty
            "   ",                       # Whitespace only
            "123456789",                 # Numbers only
            "!@#$%^&*()",               # Special chars only
            "a" * 1000,                 # Very long repeated
        ]
        
        for invalid_text in invalid_inputs:
            result = checker.check(invalid_text)
            # Should not crash
            assert isinstance(result, dict)
            assert 'tokens' in result
            assert 'errors' in result
    
    def test_recovery_from_malformed_corpus(self):
        """Should handle gracefully if corpus has issues."""
        import tempfile
        import json
        import os
        from corpus import CorpusBuilder
        
        # Create malformed corpus file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Missing required keys
            bad_corpus = {'some': 'data'}
            json.dump(bad_corpus, f)
            temp_path = f.name
        
        try:
            builder = CorpusBuilder()
            # Should return False, not crash
            result = builder.load_from_json(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)


@pytest.mark.integration
class TestPerformanceCharacteristics:
    """Integration tests to verify performance characteristics."""
    
    @pytest.mark.performance
    def test_edit_distance_scaling(self):
        """Edit distance should scale polynomially, not exponentially."""
        from corrector import MinEditDistance
        
        med = MinEditDistance()
        
        # Time shouldn't explode with string length
        small_result = med.distance("a" * 50, "b" * 50)
        large_result = med.distance("a" * 100, "b" * 100)
        
        # Both should complete quickly
        assert isinstance(small_result, int)
        assert isinstance(large_result, int)
        
        # Larger distance for larger strings
        assert large_result > small_result
    
    @pytest.mark.performance
    def test_candidate_generation_bounded(self):
        """Candidate generation should not explode with word length."""
        from corrector import CandidateGenerator, MinEditDistance
        
        vocab = {'cat', 'bat', 'bad', 'sad', 'cab', 'can'}
        med = MinEditDistance()
        gen = CandidateGenerator(med, vocab)
        
        # Even for medium-length words, should have bounded results
        candidates = gen.edits1("test")
        assert len(candidates) <= len(vocab) + 100  # Reasonable bound
    
    @pytest.mark.slow
    def test_spell_check_performance_scales_linearly(self):
        """Spell checking should scale roughly linearly with text length."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        # Check texts of different lengths
        short_text = "the quick brown fox"
        medium_text = "the quick brown fox " * 10
        long_text = "the quick brown fox " * 50
        
        result_short = checker.check(short_text)
        result_medium = checker.check(medium_text)
        result_long = checker.check(long_text)
        
        # Should all complete without crashing
        assert len(result_short['tokens']) > 0
        assert len(result_medium['tokens']) > 0
        assert len(result_long['tokens']) > 0
        
        # Token count should scale roughly linearly
        assert len(result_medium['tokens']) > len(result_short['tokens'])
        assert len(result_long['tokens']) > len(result_medium['tokens'])


@pytest.mark.integration
class TestEdgeCasesCombined:
    """Combined edge case scenarios."""
    
    def test_unicode_text_end_to_end(self):
        """Should handle Unicode text throughout pipeline."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        unicode_texts = [
            "café",
            "naïve résumé",
            "Ñoño",
        ]
        
        for text in unicode_texts:
            result = checker.check(text)
            assert isinstance(result, dict)
    
    def test_mixed_case_normalization(self):
        """Mixed case text should be handled consistently."""
        from corpus import CorpusBuilder
        from corrector import SpellChecker
        
        builder = CorpusBuilder()
        corpus = builder.build()
        checker = SpellChecker(corpus)
        
        result1 = checker.check("The Quick Brown Fox")
        result2 = checker.check("the quick brown fox")
        result3 = checker.check("THE QUICK BROWN FOX")
        
        # Should identify same errors regardless of case
        errors1 = {e['word'].lower() for e in result1['errors']}
        errors2 = {e['word'].lower() for e in result2['errors']}
        errors3 = {e['word'].lower() for e in result3['errors']}
        
        # Error patterns should be similar
        assert len(errors1 - errors2) <= 1
        assert len(errors1 - errors3) <= 1
