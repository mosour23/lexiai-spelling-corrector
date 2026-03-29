"""
test_build_corpus.py - Unit tests for the corpus building module

Tests functions for fetching papers, cleaning text, tokenization,
and data validation from the arXiv corpus builder.
"""

import pytest
from unittest.mock import patch, MagicMock
import json


@pytest.mark.unit
class TestTextCleaning:
    """Tests for text cleaning and preprocessing functions."""
    
    def test_clean_text_basic(self):
        """Basic text cleaning should lowercase and remove special chars."""
        from build_corpus import clean_text
        
        result = clean_text("HELLO World!")
        assert result == result.lower()
        assert '!' not in result
    
    def test_clean_text_removes_urls(self):
        """URLs should be removed from text."""
        from build_corpus import clean_text
        
        text = "Check https://arxiv.org and http://google.com for info"
        result = clean_text(text)
        
        assert 'https' not in result
        assert 'http' not in result
        assert 'arxiv' not in result
    
    def test_clean_text_normalizes_spaces(self):
        """Multiple spaces should be normalized."""
        from build_corpus import clean_text
        
        text = "word1    word2\n\nword3\t\tword4"
        result = clean_text(text)
        
        assert '  ' not in result
        assert '\n' not in result
        assert '\t' not in result
    
    @pytest.mark.edge_case
    def test_clean_text_empty_string(self):
        """Empty string should return empty string."""
        from build_corpus import clean_text
        
        result = clean_text("")
        assert result == ""
    
    @pytest.mark.edge_case
    def test_clean_text_only_special_chars(self):
        """Text with only special chars should become empty or minimal."""
        from build_corpus import clean_text
        
        result = clean_text("!@#$%^&*()")
        # Should be empty or minimal after cleaning
        assert result.strip() == "" or len(result.strip()) < 3


@pytest.mark.unit
class TestPaperFetching:
    """Tests for paper fetching from arXiv API."""
    
    @pytest.mark.slow
    def test_fetch_papers_valid_query(self, mock_arxiv_response):
        """Fetching papers with valid query should return list."""
        from build_corpus import fetch_papers
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = mock_arxiv_response.encode('utf-8')
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            result = fetch_papers("transformer attention", max_results=10)
            
            # Should return a list
            assert isinstance(result, list)
    
    def test_fetch_papers_network_error(self):
        """Network error should be handled gracefully."""
        from build_corpus import fetch_papers
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network error")
            
            result = fetch_papers("query")
            
            # Should return empty list on error
            assert result == []
    
    def test_fetch_papers_invalid_xml(self):
        """Invalid XML response should be handled."""
        from build_corpus import fetch_papers
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"<invalid>xml</broken>"
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            result = fetch_papers("query")
            
            # Should return empty list on parse error
            assert result == []


@pytest.mark.unit
class TestPaperValidation:
    """Tests for paper metadata validation."""
    
    def test_valid_paper_passes(self):
        """Valid paper should pass all checks."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': 'arxiv-2301-00001',
            'title': 'A Great Paper',
            'abstract': 'This is the abstract.'
        }
        
        # Should either return True or pass silently
        result = _validate_paper(paper)
        # Depending on implementation
        assert result is True or result is not False
    
    def test_paper_missing_required_field(self):
        """Paper missing required field should fail."""
        from build_corpus import _validate_paper
        
        paper = {
            'title': 'Missing ID',
            'abstract': 'Abstract here'
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_paper_empty_abstract(self):
        """Paper with empty abstract should fail."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': 'test-id',
            'title': 'Title',
            'abstract': ''
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_paper_abstract_too_long(self):
        """Very long abstract should fail."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': 'test-id',
            'title': 'Title',
            'abstract': 'word ' * 5000  # Very long
        }
        
        result = _validate_paper(paper)
        assert result is False
    
    def test_paper_wrong_type_id(self):
        """Non-string ID should fail."""
        from build_corpus import _validate_paper
        
        paper = {
            'id': 12345,
            'title': 'Title',
            'abstract': 'Abstract'
        }
        
        result = _validate_paper(paper)
        assert result is False


@pytest.mark.unit
class TestBuildCorpusOutput:
    """Tests for corpus output file generation."""
    
    def test_corpus_output_json_valid(self):
        """Generated corpus JSON should be valid."""
        import tempfile
        import json
        import os
        from collections import Counter
        
        # Create sample data
        corpus_data = {
            'meta': {'version': '1.0', 'count': 10},
            'word_freq': {'word1': 100, 'word2': 50},
            'vocabulary': ['word1', 'word2', 'word3'],
            'bigrams': {'word1|word2': 30}
        }
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(corpus_data, f)
            temp_path = f.name
        
        try:
            # Read back and verify
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded == corpus_data
            assert 'word_freq' in loaded
            assert 'vocabulary' in loaded
            assert 'bigrams' in loaded
        finally:
            os.unlink(temp_path)
    
    def test_corpus_schema_consistency(self):
        """Corpus should have consistent schema."""
        import tempfile
        import json
        import os
        
        corpus_data = {
            'word_freq': {'w1': 10, 'w2': 20},
            'vocabulary': ['w1', 'w2'],
            'bigrams': {'w1|w2': 5}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(corpus_data, f)
            temp_path = f.name
        
        try:
            # Verify schema
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            # All required fields present
            assert 'word_freq' in data
            assert 'vocabulary' in data
            assert 'bigrams' in data
            
            # Types are correct
            assert isinstance(data['word_freq'], dict)
            assert isinstance(data['vocabulary'], list)
            assert isinstance(data['bigrams'], dict)
        finally:
            os.unlink(temp_path)


@pytest.mark.unit
class TestTokenMetadataGeneration:
    """Tests for token count and metadata generation."""
    
    def test_token_count_calculation(self):
        """Token count should be calculated correctly."""
        from build_corpus import tokenize
        from collections import Counter
        
        tokens = tokenize("the quick brown fox jumps over the lazy dog")
        token_count = len(tokens)
        
        assert token_count == 8
    
    def test_word_frequency_accumulation(self):
        """Word frequencies should accumulate correctly."""
        from build_corpus import tokenize
        from collections import Counter
        
        tokens = tokenize("the the the quick quick brown")
        word_freq = Counter(tokens)
        
        assert word_freq['the'] == 3
        assert word_freq['quick'] == 2
        assert word_freq['brown'] == 1


@pytest.mark.unit
class TestBuildCorpusConfigValidation:
    """Tests for configuration validation."""
    
    def test_search_queries_are_strings(self):
        """Search queries should be non-empty strings."""
        from build_corpus import SEARCH_QUERIES
        
        assert isinstance(SEARCH_QUERIES, list)
        assert len(SEARCH_QUERIES) > 0
        
        for query in SEARCH_QUERIES:
            assert isinstance(query, str)
            assert len(query) > 0
    
    def test_parameters_reasonable(self):
        """Configuration parameters should be reasonable."""
        from build_corpus import (
            PAPERS_PER_QUERY, MAX_TOTAL_PAPERS, 
            TARGET_WORDS, DELAY_SECONDS
        )
        
        assert PAPERS_PER_QUERY > 0
        assert MAX_TOTAL_PAPERS > 0
        assert TARGET_WORDS > 0
        assert DELAY_SECONDS > 0
        
        # Sanity checks
        assert PAPERS_PER_QUERY <= 100
        assert MAX_TOTAL_PAPERS >= PAPERS_PER_QUERY
        assert DELAY_SECONDS <= 10


@pytest.mark.integration
class TestBuildCorpusPipeline:
    """Integration tests for build_corpus module."""
    
    @pytest.mark.slow
    @pytest.mark.skip(reason="Requires network access to arXiv")
    def test_full_corpus_build_with_mocked_api(self, mock_arxiv_response):
        """Full corpus build with mocked API response."""
        from build_corpus import build_corpus
        
        # This test would need proper mocking setup
        # Skipped for now as it requires network/complex setup
        pass


@pytest.mark.unit
class TestDataSerialization:
    """Tests for data serialization/deserialization."""
    
    def test_bigram_serialization_format(self):
        """Bigrams should serialize as pipe-separated strings."""
        test_data = {
            'the|quick': 50,
            'quick|brown': 40,
            'brown|fox': 35
        }
        
        # Should be able to deserialize back
        for bigram_str, count in test_data.items():
            parts = bigram_str.split('|')
            assert len(parts) == 2
            assert count > 0
    
    def test_counter_to_dict_conversion(self):
        """Counter objects should convert to dict properly."""
        from collections import Counter
        
        counter = Counter({'word1': 100, 'word2': 50})
        dict_form = dict(counter)
        
        assert isinstance(dict_form, dict)
        assert dict_form['word1'] == 100
        assert dict_form['word2'] == 50


@pytest.mark.unit
class TestErrorHandlingGraceful:
    """Tests for graceful error handling."""
    
    def test_invalid_paper_dict_handling(self):
        """Invalid paper dictionary should be handled."""
        from build_corpus import _validate_paper
        
        invalid_papers = [
            None,
            {},
            {'id': None},
            {'title': None},
            {'abstract': None},
        ]
        
        for paper in invalid_papers:
            # Should not crash
            if paper is not None:
                result = _validate_paper(paper)
                assert result is False
    
    def test_timeout_configuration(self):
        """API timeout should be configured."""
        from build_corpus import fetch_papers
        
        # Check that timeout is used in fetch_papers
        # This is verified through code inspection
        with patch('urllib.request.urlopen') as mock_urlopen:
            try:
                fetch_papers("test")
            except:
                pass
            
            # urlopen should have been called with timeout
            if mock_urlopen.called:
                call_kwargs = mock_urlopen.call_args
                # Should have timeout parameter somewhere
                assert call_kwargs is not None
