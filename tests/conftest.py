"""
conftest.py - Shared pytest fixtures and configuration

Provides fixtures for spelling corrector tests:
- MED instances with different cost weights
- Sample vocabularies
- Test corpora
- Mock data
"""

import pytest
import json
import tempfile
import os
from collections import Counter

# Add the parent directory to path to import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'part_a_section1_spelling_corrector'))


@pytest.fixture
def med_default():
    """Standard MinEditDistance instance with default costs."""
    from corrector import MinEditDistance
    return MinEditDistance(ins_cost=1, del_cost=1, sub_cost=2, trans_cost=1)


@pytest.fixture
def med_equal_costs():
    """MinEditDistance with equal costs (standard Levenshtein)."""
    from corrector import MinEditDistance
    return MinEditDistance(ins_cost=1, del_cost=1, sub_cost=1, trans_cost=1)


@pytest.fixture
def med_expensive_sub():
    """MinEditDistance with expensive substitutions."""
    from corrector import MinEditDistance
    return MinEditDistance(ins_cost=1, del_cost=1, sub_cost=5, trans_cost=1)


@pytest.fixture
def sample_vocab():
    """Small vocabulary for testing."""
    return {
        'the', 'quick', 'brown', 'fox', 'jumps', 'over',
        'lazy', 'dog', 'cat', 'runs', 'walks', 'is', 'a',
        'an', 'and', 'or', 'but', 'tokenization', 'embedding',
        'transformer', 'attention', 'neural', 'network'
    }


@pytest.fixture
def sample_bigrams():
    """Sample bigram frequencies for testing."""
    return Counter({
        ('the', 'quick'): 50,
        ('quick', 'brown'): 45,
        ('brown', 'fox'): 40,
        ('the', 'lazy'): 35,
        ('lazy', 'dog'): 30,
        ('is', 'a'): 100,
        ('a', 'transformer'): 20,
        ('neural', 'network'): 25,
        ('deep', 'learning'): 15,
    })


@pytest.fixture
def sample_word_freq():
    """Sample word frequencies for testing."""
    return Counter({
        'the': 1000,
        'quick': 50,
        'brown': 40,
        'fox': 30,
        'jumps': 25,
        'over': 20,
        'lazy': 15,
        'dog': 35,
        'cat': 20,
        'is': 500,
        'a': 400,
        'transformer': 10,
        'neural': 8,
        'network': 12,
    })


@pytest.fixture
def corpus_data(sample_vocab, sample_bigrams, sample_word_freq):
    """Complete corpus data structure for testing."""
    return {
        'tokens': sum(sample_word_freq.values()),
        'word_freq': dict(sample_word_freq),
        'vocabulary': sorted(list(sample_vocab)),
        'bigrams': {f"{k[0]}|{k[1]}": v for k, v in sample_bigrams.items()}
    }


@pytest.fixture
def temp_corpus_file(corpus_data):
    """Temporary JSON corpus file for testing file I/O."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(corpus_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def spell_checker_factory(sample_vocab, sample_bigrams, sample_word_freq):
    """Factory fixture for creating SpellChecker instances."""
    from corrector import SpellChecker, BigramLanguageModel
    
    def create_checker():
        # Create a minimal corpus-like object
        class MockCorpus:
            def __init__(self):
                self.vocabulary = sample_vocab
                self.word_freq = sample_word_freq
                self.bigrams = sample_bigrams
                self.tokens = sum(sample_word_freq.values())
        
        corpus = MockCorpus()
        return SpellChecker(corpus)
    
    return create_checker


@pytest.fixture
def corpus_builder():
    """CorpusBuilder instance for testing."""
    from corpus import CorpusBuilder
    return CorpusBuilder()


@pytest.fixture
def sample_texts():
    """Sample texts for testing preprocessing and tokenization."""
    return {
        'simple': "The quick brown fox jumps over the lazy dog",
        'with_errors': "The quikc brown fox jumps ovr the laazy dog",
        'with_numbers': "There are 123 cats and 456 dogs",
        'with_punctuation': "Hello, world! How are you? I'm fine.",
        'with_urls': "Check https://arxiv.org/papers for more info",
        'mixed_case': "NEURAL Network Transformer ATTENTION mechanism",
        'with_special': "This has @symbols #hashtags $money and (parens)",
        'empty': "",
        'whitespace_only': "   \n\t  ",
        'unicode': "Café naïve résumé",
        'latex_math': "The equation \\alpha{x} and $y^2 = z$ are here",
    }


@pytest.fixture
def mock_arxiv_response():
    """Mock XML response from arXiv API."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
    <entry>
        <id>http://arxiv.org/abs/2301.00001v1</id>
        <title>Attention Is All You Need</title>
        <summary>We propose a new simple network architecture, the Transformer, based solely on attention mechanisms. This architecture is efficient and effective for many NLP tasks.</summary>
        <arxiv:primary_category term="cs.CL"/>
    </entry>
    <entry>
        <id>http://arxiv.org/abs/2301.00002v1</id>
        <title>BERT: Pre-training of Deep Bidirectional Transformers</title>
        <summary>We introduce BERT, a new pre-training method for NLP that achieves state-of-the-art results on various tasks including named entity recognition and question answering.</summary>
        <arxiv:primary_category term="cs.CL"/>
    </entry>
</feed>"""


# Markers that can be used with pytest
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "critical(reason): marks tests as critical (deselect with '-m \"not critical\"')"
    )
    config.addinivalue_line(
        "markers", "slow(reason): marks tests as slow (deselect with '-m \"not slow\"')"
    )
