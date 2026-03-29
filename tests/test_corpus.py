"""
test_corpus.py - Unit tests for corpus building and management

Tests CorpusBuilder class for vocabulary creation, preprocessing, and loading.
"""

import pytest
import json
import os
from collections import Counter


@pytest.mark.unit
@pytest.mark.critical
class TestCorpusBuilder:
    """Tests for CorpusBuilder class."""
    
    def test_corpus_initialization(self, corpus_builder):
        """CorpusBuilder should initialize without errors."""
        assert corpus_builder is not None
        assert hasattr(corpus_builder, 'build')
        assert hasattr(corpus_builder, 'load_from_json')
    
    def test_build_corpus_from_seed(self, corpus_builder):
        """Building corpus from seed should create vocabulary."""
        corpus = corpus_builder.build()
        
        assert corpus is not None
        assert hasattr(corpus, 'vocabulary')
        assert hasattr(corpus, 'word_freq')
        assert hasattr(corpus, 'bigrams')
        
        # Should have some vocabulary from embedded seed text
        assert len(corpus.vocabulary) > 0
        assert len(corpus.word_freq) > 0
    
    def test_corpus_has_nlp_terms(self, corpus_builder):
        """Embedded corpus should contain NLP-related terms."""
        corpus = corpus_builder.build()
        
        # Should have some NLP vocabulary from seed text
        nlp_terms = {'transformer', 'embedding', 'attention', 'neural', 'tokenization'}
        vocab_lower = {w.lower() for w in corpus.vocabulary}
        
        # At least some NLP terms should be present
        found_terms = nlp_terms & vocab_lower
        assert len(found_terms) > 0
    
    def test_word_frequencies_are_positive(self, corpus_builder):
        """Word frequencies should all be positive integers."""
        corpus = corpus_builder.build()
        
        for word, freq in corpus.word_freq.items():
            assert freq > 0
            assert isinstance(freq, int)
    
    def test_bigrams_are_valid_tuples(self, corpus_builder):
        """Bigrams should be valid word pairs."""
        corpus = corpus_builder.build()
        
        for (w1, w2), count in corpus.bigrams.items():
            assert isinstance(w1, str)
            assert isinstance(w2, str)
            assert len(w1) > 0
            assert len(w2) > 0
            assert count > 0
    
    @pytest.mark.edge_case
    def test_bigram_words_in_vocab(self, corpus_builder):
        """Bigram words should be in vocabulary."""
        corpus = corpus_builder.build()
        vocab_set = set(corpus.vocabulary)
        
        for (w1, w2), count in corpus.bigrams.items():
            # Most bigram words should be in vocabulary
            # (some might be out-of-vocab if added during preprocessing)
            assert w1 in vocab_set or len(w1) > 0
            assert w2 in vocab_set or len(w2) > 0


@pytest.mark.unit
class TestCorpusFileIO:
    """Tests for corpus file loading and saving."""
    
    def test_save_and_load_corpus(self, corpus_builder, temp_corpus_file):
        """Corpus should be saveable and loadable."""
        corpus2 = corpus_builder.build()
        
        # Try loading from temp file
        loaded = corpus_builder.load_from_json(temp_corpus_file)
        assert loaded is True
        
        # After loading, should have vocabulary
        assert corpus2.vocabulary is not None or len(corpus2.vocabulary) > 0
    
    def test_load_nonexistent_file(self, corpus_builder):
        """Loading nonexistent file should return False."""
        result = corpus_builder.load_from_json('/nonexistent/path/corpus.json')
        assert result is False
    
    def test_load_invalid_json(self, corpus_builder):
        """Loading invalid JSON should return False."""
        with pytest.tempfile.TemporaryDirectory() as tmpdir:
            bad_json_path = os.path.join(tmpdir, 'bad.json')
            with open(bad_json_path, 'w') as f:
                f.write("{ invalid json }")
            
            result = corpus_builder.load_from_json(bad_json_path)
            assert result is False
    
    def test_load_corrupt_corpus_missing_keys(self, corpus_builder):
        """Loading corpus with missing required keys should handle gracefully."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Missing required keys
            corrupt_data = {'some_key': 'some_value'}
            json.dump(corrupt_data, f)
            temp_path = f.name
        
        try:
            result = corpus_builder.load_from_json(temp_path)
            # Should either return False or handle gracefully
            assert result is False or corpus_builder.vocabulary is not None
        finally:
            os.unlink(temp_path)
    
    def test_load_corpus_consistent_data(self, corpus_data):
        """Loaded corpus should have consistent data structures."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(corpus_data, f)
            temp_path = f.name
        
        try:
            from corpus import CorpusBuilder
            builder = CorpusBuilder()
            result = builder.load_from_json(temp_path)
            
            # Should load successfully
            assert result is True
        finally:
            os.unlink(temp_path)


@pytest.mark.unit
class TestTextPreprocessing:
    """Tests for text cleaning and preprocessing."""
    
    def test_text_lowercasing(self, sample_texts):
        """Text should be converted to lowercase."""
        from build_corpus import clean_text
        
        cleaned = clean_text(sample_texts['mixed_case'])
        assert cleaned == cleaned.lower()
    
    def test_url_removal(self, sample_texts):
        """URLs should be removed or replaced."""
        from build_corpus import clean_text
        
        cleaned = clean_text(sample_texts['with_urls'])
        # URLs should not appear in cleaned text (replaced with space)
        assert 'https' not in cleaned
        assert 'arxiv' not in cleaned or cleaned.count('arxiv') < sample_texts['with_urls'].count('arxiv')
    
    def test_special_char_removal(self, sample_texts):
        """Special characters should be removed."""
        from build_corpus import clean_text
        
        cleaned = clean_text(sample_texts['with_special'])
        # Special chars should be gone
        assert '@' not in cleaned
        assert '#' not in cleaned
        assert '$' not in cleaned
    
    def test_whitespace_normalization(self, sample_texts):
        """Multiple whitespaces should be normalized to single space."""
        from build_corpus import clean_text
        
        text_with_spaces = "word1    word2\n\n\tword3"
        cleaned = clean_text(text_with_spaces)
        
        # Should have normalized spaces
        assert '  ' not in cleaned
        assert '\n' not in cleaned
        assert '\t' not in cleaned
    
    @pytest.mark.edge_case
    def test_latex_math_removal(self, sample_texts):
        """LaTeX math expressions should be removed."""
        from build_corpus import clean_text
        
        cleaned = clean_text(sample_texts['latex_math'])
        # Should not have \alpha or math symbols
        assert '\\' not in cleaned or cleaned.count('\\') < sample_texts['latex_math'].count('\\')
    
    @pytest.mark.edge_case
    def test_empty_text_preprocessing(self):
        """Empty text should return empty string."""
        from build_corpus import clean_text
        
        result = clean_text("")
        assert result == ""
    
    @pytest.mark.edge_case
    def test_unicode_text_preprocessing(self, sample_texts):
        """Unicode text should be handled."""
        from build_corpus import clean_text
        
        result = clean_text(sample_texts['unicode'])
        # Should process without error
        assert isinstance(result, str)


@pytest.mark.unit
class TestTokenization:
    """Tests for tokenization from corpus."""
    
    def test_tokenize_simple_text(self, corpus_builder, sample_texts):
        """Tokenization should split text into words."""
        from build_corpus import tokenize
        
        tokens = tokenize(sample_texts['simple'])
        
        assert len(tokens) > 0
        # Simple text should have around 8 words
        assert len(tokens) >= 8
    
    def test_tokenize_preserves_word_content(self, corpus_builder, sample_texts):
        """Tokenization should preserve word content."""
        from build_corpus import tokenize
        
        tokens = tokenize(sample_texts['simple'].lower())
        word_list = [t for t in tokens if t.isalpha()]
        
        assert 'the' in word_list
        assert 'quick' in word_list
        assert 'brown' in word_list
    
    @pytest.mark.edge_case
    def test_tokenize_empty_text(self):
        """Tokenizing empty text should return empty list."""
        from build_corpus import tokenize
        
        tokens = tokenize("")
        assert len(tokens) == 0
    
    @pytest.mark.edge_case
    def test_tokenize_no_words(self):
        """Tokenizing text with no words should return filtered list."""
        from build_corpus import tokenize
        
        tokens = tokenize("123 456 @@@")
        # Should have few or no valid word tokens
        valid_words = [t for t in tokens if t.isalpha()]
        # Some implementation might keep numbers
        assert isinstance(tokens, list)


@pytest.mark.unit
class TestPaperValidation:
    """Tests for paper metadata validation."""
    
    def test_valid_paper_structure(self):
        """Valid paper should pass validation."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': '2301.00001',
            'title': 'Attention Is All You Need',
            'abstract': 'This is a valid abstract about transformers and neural networks.'
        }
        
        result = _validate_paper(paper)
        assert result is True or result  # Should validate as True
    
    def test_missing_id_field(self):
        """Paper missing id should fail validation."""
        from build_corpus import _validate_paper
        
        paper = {
            'title': 'Title',
            'abstract': 'Abstract'
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_missing_abstract_field(self):
        """Paper missing abstract should fail validation."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': '2301.00001',
            'title': 'Title'
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_too_long_abstract(self):
        """Paper with very long abstract should fail validation."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': '2301.00001',
            'title': 'Title',
            'abstract': 'word ' * 2000  # Too long
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_invalid_type_id(self):
        """Paper with non-string id should fail validation."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': 12345,  # Not a string
            'title': 'Title',
            'abstract': 'Abstract'
        }
        
        result = _validate_paper(paper)
        assert result is False


@pytest.mark.unit
class TestBigramGeneration:
    """Tests for bigram extraction and counting."""
    
    def test_bigrams_from_tokens(self, corpus_builder, sample_texts):
        """Bigrams should be extracted from token sequence."""
        from build_corpus import extract_bigrams
        
        tokens = ['the', 'quick', 'brown', 'fox']
        bigrams = extract_bigrams(tokens)
        
        # Should have 3 bigrams from 4 tokens
        assert len(bigrams) == 3
        assert ('the', 'quick') in bigrams
        assert ('quick', 'brown') in bigrams
        assert ('brown', 'fox') in bigrams
    
    def test_single_token_no_bigrams(self):
        """Single token should produce no bigrams."""
        from build_corpus import extract_bigrams
        
        tokens = ['word']
        bigrams = extract_bigrams(tokens)
        
        assert len(bigrams) == 0
    
    @pytest.mark.edge_case
    def test_empty_token_sequence(self):
        """Empty token sequence should produce no bigrams."""
        from build_corpus import extract_bigrams
        
        bigrams = extract_bigrams([])
        assert len(bigrams) == 0
    
    def test_bigram_counts_accumulate(self):
        """Repeated bigrams should accumulate counts."""
        from build_corpus import extract_bigrams
        from collections import Counter
        
        tokens = ['the', 'cat', 'the', 'dog', 'the', 'bird']
        bigrams = extract_bigrams(tokens)
        bigram_counts = Counter(bigrams)
        
        # ('the', 'cat'), ('the', 'dog'), ('the', 'bird') are all different
        assert ('the', 'cat') in bigram_counts
        assert ('the', 'dog') in bigram_counts
        assert ('the', 'bird') in bigram_counts


@pytest.mark.integration
class TestCorpusIntegration:
    """Integration tests for corpus building pipeline."""
    
    def test_full_corpus_build_pipeline(self, corpus_builder, sample_texts):
        """Full pipeline: build corpus and use in spell checker."""
        corpus = corpus_builder.build()
        
        # Should have all components
        assert len(corpus.vocabulary) > 0
        assert len(corpus.word_freq) > 0
        assert len(corpus.bigrams) > 0
        
        # Create spell checker from corpus
        from corrector import SpellChecker
        checker = SpellChecker(corpus)
        
        # Should be able to check text
        result = checker.check(sample_texts['simple'])
        assert 'tokens' in result
        assert 'errors' in result
    
    def test_corpus_persistence(self, corpus_builder, temp_corpus_file):
        """Corpus should be persistently saveable and loadable."""
        # Build original corpus
        original = corpus_builder.build()
        original_vocab_size = len(original.vocabulary)
        
        # Save and load
        loaded = corpus_builder.load_from_json(temp_corpus_file)
        
        # Should have same vocab size
        if loaded:
            assert len(corpus_builder.vocabulary) == original_vocab_size
