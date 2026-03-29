"""
test_utilities.py - Shared testing utilities and helpers

Provides fixtures, mock data generators, and testing utilities
used across multiple test files.
"""

import pytest
import tempfile
import json
import os
from collections import Counter
from typing import List, Dict, Any


def create_temp_json_file(data: Dict[str, Any], suffix: str = '.json') -> str:
    """
    Create a temporary JSON file with given data.
    
    Args:
        data: Dictionary to serialize
        suffix: File extension
    
    Returns:
        Path to temporary file (caller must clean up)
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    json.dump(data, temp_file)
    temp_file.close()
    return temp_file.name


def cleanup_temp_file(path: str) -> None:
    """Remove temporary file if it exists."""
    if os.path.exists(path):
        os.unlink(path)


class MockCorpus:
    """Mock corpus object for testing without loading real corpus."""
    
    def __init__(
        self,
        vocabulary: set = None,
        word_freq: Counter = None,
        bigrams: Counter = None,
        tokens: int = 1000
    ):
        self.vocabulary = vocabulary or {'the', 'quick', 'brown', 'fox', 'jumps'}
        self.word_freq = word_freq or Counter({'the': 100, 'quick': 50, 'brown': 40})
        self.bigrams = bigrams or Counter({('the', 'quick'): 20})
        self.tokens = tokens


class TextGenerator:
    """Generate test texts for performance and edge case testing."""
    
    @staticmethod
    def repeated_word(word: str, count: int) -> str:
        """Generate text with repeated word."""
        return ' '.join([word] * count)
    
    @staticmethod
    def random_words(words: List[str], count: int) -> str:
        """Generate text with random word selection."""
        import random
        selected = [random.choice(words) for _ in range(count)]
        return ' '.join(selected)
    
    @staticmethod
    def with_errors(base_text: str, error_count: int) -> str:
        """
        Generate text with intentional errors.
        
        Typical: inject typos by removing/changing characters.
        """
        words = base_text.split()
        errors_made = 0
        
        for i, word in enumerate(words):
            if errors_made >= error_count:
                break
            if len(word) > 2:
                # Simple typo: swap adjacent characters
                chars = list(word)
                idx = len(chars) // 2
                chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
                words[i] = ''.join(chars)
                errors_made += 1
        
        return ' '.join(words)
    
    @staticmethod
    def unicode_text() -> str:
        """Generate text with Unicode characters."""
        return "café naïve résumé façade"
    
    @staticmethod
    def mixed_case_text() -> str:
        """Generate text with mixed cases."""
        return "ThE QuIcK BrOwN FoX JuMpS"
    
    @staticmethod
    def with_special_chars() -> str:
        """Generate text with special characters."""
        return "Hello! World? How are you... I'm fine @#$%"
    
    @staticmethod
    def with_urls() -> str:
        """Generate text with URLs."""
        return "Check https://example.com or http://google.com for info"
    
    @staticmethod
    def with_numbers() -> str:
        """Generate text with numbers and digits."""
        return "There are 123 cats, 456 dogs, and 789 birds"


class AssertionHelpers:
    """Helper methods for common assertions in tests."""
    
    @staticmethod
    def assert_is_probability(value: float, name: str = "value") -> None:
        """Assert value is valid probability (0 to 1)."""
        assert 0 <= value <= 1, f"{name} must be between 0 and 1, got {value}"
    
    @staticmethod
    def assert_is_positive(value: int, name: str = "value") -> None:
        """Assert value is positive integer."""
        assert isinstance(value, int), f"{name} must be int, got {type(value)}"
        assert value > 0, f"{name} must be positive, got {value}"
    
    @staticmethod
    def assert_valid_word(word: str) -> None:
        """Assert word is non-empty lowercase string."""
        assert isinstance(word, str), f"Word must be string, got {type(word)}"
        assert len(word) > 0, "Word cannot be empty"
        assert word == word.lower(), f"Word must be lowercase, got {word}"
    
    @staticmethod
    def assert_vocabulary_consistency(vocab: set, word_freq: Dict) -> None:
        """Assert vocabulary and word_freq are consistent."""
        for word in word_freq.keys():
            assert word in vocab or len(word) == 0, f"Word {word} not in vocab"


class PerformanceMonitor:
    """Simple performance monitoring for tests."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.time()
    
    @property
    def elapsed_seconds(self) -> float:
        """Elapsed time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def assert_under_seconds(self, max_seconds: float) -> None:
        """Assert operation completed within time limit."""
        assert self.elapsed_seconds < max_seconds, \
            f"{self.name} took {self.elapsed_seconds:.2f}s, limit is {max_seconds}s"
    
    def __repr__(self) -> str:
        return f"{self.name}: {self.elapsed_seconds:.3f}s"


@pytest.fixture
def text_generator():
    """Fixture providing TextGenerator utility."""
    return TextGenerator()


@pytest.fixture
def assertion_helpers():
    """Fixture providing AssertionHelpers utility."""
    return AssertionHelpers()


@pytest.fixture
def performance_monitor():
    """Fixture providing PerformanceMonitor context manager."""
    return PerformanceMonitor


@pytest.fixture
def mock_corpus_small():
    """Small mock corpus for quick tests."""
    return MockCorpus(
        vocabulary={'the', 'quick', 'brown', 'fox', 'cat', 'dog'},
        word_freq=Counter({'the': 100, 'quick': 20, 'brown': 15}),
        bigrams=Counter({('the', 'quick'): 10, ('quick', 'brown'): 8}),
        tokens=135
    )


@pytest.fixture
def mock_corpus_large():
    """Larger mock corpus for realistic tests."""
    vocab = set()
    words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog',
             'cat', 'runs', 'walks', 'is', 'a', 'an', 'and', 'or', 'but',
             'there', 'they', 'them', 'this', 'that', 'these', 'transformer',
             'attention', 'embedding', 'neural', 'network', 'learning', 'model']
    vocab.update(words)
    
    word_freq = Counter({w: (100 - i * 3) for i, w in enumerate(words[:20])})
    
    bigrams = Counter({
        ('the', 'quick'): 50,
        ('quick', 'brown'): 45,
        ('brown', 'fox'): 40,
        ('neural', 'network'): 35,
        ('transformer', 'attention'): 30,
    })
    
    return MockCorpus(
        vocabulary=vocab,
        word_freq=word_freq,
        bigrams=bigrams,
        tokens=sum(word_freq.values())
    )


# Test data constants
VALID_PAPERS = [
    {
        'id': 'arxiv-2301-00001',
        'title': 'Attention Is All You Need',
        'abstract': 'We propose a new simple network architecture based solely on attention mechanisms.'
    },
    {
        'id': 'arxiv-2301-00002',
        'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
        'abstract': 'We introduce BERT, a new pre-training method that achieves state-of-the-art results.'
    },
]

INVALID_PAPERS = [
    {'title': 'Missing ID'},
    {'id': 'test', 'title': 'Missing Abstract'},
    {'id': 123, 'title': 'Title', 'abstract': 'Abstract'},  # Wrong ID type
    {'id': 'test', 'title': 'Title', 'abstract': ''},  # Empty abstract
]

COMMON_TYPOS = [
    ('teh', 'the'),
    ('recieve', 'receive'),
    ('occured', 'occurred'),
    ('seperete', 'separate'),
    ('definately', 'definitely'),
    ('accomodate', 'accommodate'),
    ('neccessary', 'necessary'),
    ('untill', 'until'),
]

EDGE_CASE_TEXTS = {
    'empty': '',
    'whitespace': '   \n\t  ',
    'single_word': 'word',
    'numbers_only': '123 456 789',
    'special_chars': '!@#$%^&*()',
    'unicode': 'café naïve résumé',
    'mixed_case': 'HeLLo WoRLd',
    'urls': 'https://example.com http://test.org',
    'emails': 'test@example.com user@domain.co.uk',
    'emojis': '😀 🎉 ✨',
}
