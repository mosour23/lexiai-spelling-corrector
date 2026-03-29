# Testing Guide for NLP Assignment

## Overview

This document provides comprehensive guidance for running, writing, and maintaining tests for the NLP Assignment project. The test suite covers:

- **Unit tests** for individual functions and classes
- **Integration tests** for component interactions
- **Edge cases** and error scenarios
- **Performance tests** for algorithm efficiency

---

## 📁 Test Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                  # Main pytest configuration (in project root)
├── test_corrector.py          # MinEditDistance, BigramLM, SpellChecker tests
├── test_corpus.py             # CorpusBuilder, preprocessing tests
├── test_build_corpus.py       # arXiv fetching, validation tests
├── test_integration.py        # End-to-end pipeline tests
└── utils/
    ├── test_helpers.py        # (Optional) Shared test utilities
    └── test_data.py           # (Optional) Test data generators
```

---

## 🚀 Quick Start

### Installation

```bash
# Install pytest (only testing dependency)
pip install pytest

# Optional: For coverage reports
pip install pytest-cov

# Optional: For parallel test execution
pip install pytest-xdist

# Optional: For test timeouts
pip install pytest-timeout
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only unit tests (fast)
pytest -m unit

# Run only critical tests
pytest -m critical

# Run with coverage report
pytest --cov=part_a_section1_spelling_corrector --cov-report=html

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/test_corrector.py

# Run specific test class
pytest tests/test_corrector.py::TestMinEditDistance

# Run specific test
pytest tests/test_corrector.py::TestMinEditDistance::test_identical_strings

# Run with markers (skip slow tests)
pytest -m "not slow"

# Run only slow/performance tests
pytest -m slow

# Run with specific timeout (seconds)
pytest --timeout=300
```

---

## 📊 Test Coverage Breakdown

### `test_corrector.py` — Spelling Correction Engine

#### MinEditDistance (15 tests)
- ✅ Identical strings → distance 0
- ✅ Empty string handling
- ✅ Single operation costs (substitution=2, insertion=1, deletion=1)
- ✅ Transposition cost=1
- ✅ Multiple operations
- ✅ Case sensitivity
- ✅ Equal cost weights (standard Levenshtein)
- ✅ Long strings (up to 100 characters)
- ✅ Unicode character handling
- ✅ Special character handling
- ✅ Different cost weight configurations

**Edge Cases:**
- Very long strings (100+ chars)
- Unicode characters (café, naïve, résumé)
- Special characters and punctuation

#### BigramLanguageModel (5 tests)
- ✅ Laplace smoothing for unseen bigrams
- ✅ Zero word frequency handling
- ✅ Probability ranking by frequency
- ✅ Empty bigram dictionary

#### SpellChecker (9 tests)
- ✅ Non-word error detection
- ✅ Correct text → no errors
- ✅ Candidate generation and ranking
- ✅ Real-word error detection (context)
- ✅ Empty text handling
- ✅ Whitespace-only text
- ✅ Single word processing
- ✅ Duplicate error handling
- ✅ Long text processing (500+ words)

**Performance Tests:**
- Long text (500+ words)
- Multiple errors in same text

---

### `test_corpus.py` — Corpus Building

#### CorpusBuilder (7 tests)
- ✅ Initialization
- ✅ Build from seed corpus
- ✅ NLP terminology inclusion
- ✅ Word frequency validation (all positive)
- ✅ Bigram tuple validation
- ✅ Bigram word membership in vocab

#### File I/O (6 tests)
- ✅ Save and load corpus
- ✅ Nonexistent file handling
- ✅ Invalid JSON handling
- ✅ Corrupt corpus (missing keys)
- ✅ Consistent data after load

#### Text Preprocessing (7 tests)
- ✅ Lowercasing
- ✅ URL removal
- ✅ Special character removal
- ✅ Whitespace normalization
- ✅ LaTeX math removal
- ✅ Empty text handling
- ✅ Unicode preservation

#### Tokenization (4 tests)
- ✅ Simple text tokenization
- ✅ Word preservation
- ✅ Empty text
- ✅ Non-word token handling

#### Paper Validation (5 tests)
- ✅ Valid paper structure
- ✅ Missing required fields
- ✅ Very long abstract rejection
- ✅ Invalid type validation

#### Bigram Generation (4 tests)
- ✅ Bigram extraction from tokens
- ✅ Single token → no bigrams
- ✅ Empty sequence → no bigrams
- ✅ Count accumulation

#### Integration (2 tests)
- ✅ Full build pipeline
- ✅ Corpus persistence

---

### `test_build_corpus.py` — corpus Builder Utils

#### Text Cleaning (5 tests)
- ✅ Basic lowercasing and special char removal
- ✅ URL removal
- ✅ Whitespace normalization
- ✅ Empty string handling
- ✅ Special-char-only handling

#### Paper Fetching (3 tests)
- ✅ Valid query handling (mocked)
- ✅ Network error graceful handling
- ✅ Invalid XML response handling

#### Paper Validation (5 tests)
- ✅ Valid paper passes
- ✅ Missing required fields
- ✅ Empty abstract rejection
- ✅ Oversized abstract rejection
- ✅ Wrong type ID rejection

#### Output Generation (2 tests)
- ✅ Valid JSON output
- ✅ Schema consistency

#### Configuration (2 tests)
- ✅ Search queries validation
- ✅ Parameters reasonableness

#### Serialization (2 tests)
- ✅ Bigram string format
- ✅ Counter to dict conversion

#### Error Handling (2 tests)
- ✅ Invalid paper dictionary handling
- ✅ Timeout configuration

---

### `test_integration.py` — End-to-End Tests

#### Spelling Correction Pipeline (4 tests)
- ✅ End-to-end: load corpus → check text
- ✅ Multiple error detection
- ✅ False positive minimization
- ✅ Candidate ranking verification

#### Corpus-Speller Integration (2 tests)
- ✅ Loaded corpus with spell checker
- ✅ Vocabulary consistency

#### Error Recovery (2 tests)
- ✅ Invalid text graceful handling
- ✅ Malformed corpus file recovery

#### Performance Characteristics (3 tests)
- ✅ Edit distance scaling (polynomial, not exponential)
- ✅ Candidate generation bounding
- ✅ Linear text processing scaling

#### Combined Edge Cases (3 tests)
- ✅ Unicode text end-to-end
- ✅ Mixed case text handling consistency

---

## 📋 Test Markers & Categories

### By Marker

```bash
# Critical functionality - must pass
pytest -m critical

# Unit tests only (fast, < 1 second each)
pytest -m unit

# Integration tests (slower, test across modules)
pytest -m integration

# Edge case scenarios
pytest -m edge_case

# Performance/load tests (slowest)
pytest -m performance

# Skip slow tests (for CI/rapid feedback)
pytest -m "not slow"
```

### By Category

| Category | Count | Avg Time | Purpose |
|----------|-------|----------|---------|
| Critical | 8 | <0.1s | MUST PASS before commit |
| Unit | 65+ | <0.5s/each | Individual components |
| Integration | 12+ | 0.5-2s | Component interactions |
| Edge Cases | 15+ | <0.1s | Boundary conditions |
| Performance | 3 | 1-5s | Algorithm efficiency |

---

## ✍️ Writing New Tests

### Test Template

```python
"""
test_mymodule.py - Tests for mymodule.py

Brief description of what's being tested.
"""

import pytest

@pytest.mark.unit
@pytest.mark.critical
class TestMyFeature:
    """Tests for MyFeature class/function."""
    
    def test_basic_functionality(self):
        """Test basic happy path."""
        result = my_function(inputs)
        assert result == expected
    
    @pytest.mark.edge_case
    def test_edge_case_empty_input(self):
        """Test with empty input."""
        result = my_function("")
        assert result == expected_empty
    
    @pytest.mark.performance
    def test_large_input_performance(self):
        """Test doesn't timeout with large input."""
        large_input = data * 1000
        result = my_function(large_input)
        # Should complete quickly
        assert result is not None
```

### Test Naming Conventions

```python
# Good test names (describe what's being tested)
def test_identical_strings_have_zero_distance()
def test_empty_source_requires_n_insertions()
def test_invalid_paper_missing_id_fails_validation()

# Avoid vague names
def test_works()              # ❌ Too vague
def test_case_1()             # ❌ Not descriptive
def test_edit_distance()      # ❌ Too general
```

### Using Fixtures

```python
# Use existing fixtures from conftest.py
def test_with_med(med_default):
    """Use pre-configured MinEditDistance."""
    assert med_default.distance("cat", "cat") == 0

# Create local fixtures within test file
@pytest.fixture
def temp_data():
    yield {"key": "value"}

def test_with_local_fixture(temp_data):
    assert temp_data["key"] == "value"

# Parametrize for multiple test cases
@pytest.mark.parametrize("input,expected", [
    ("cat", "cat", 0),
    ("cat", "bat", 2),
    ("", "xyz", 3),
])
def test_distance_various_cases(med_default, input, expected):
    assert med_default.distance(input, expected) == expected
```

### Testing Error Conditions

```python
# Test exceptions
def test_invalid_input_raises_error():
    with pytest.raises(ValueError):
        my_function(invalid_input)

# Test error messages
def test_error_message_is_clear():
    with pytest.raises(ValueError, match="Input too long"):
        my_function(huge_input)

# Test graceful degradation
def test_handles_none_input_gracefully():
    result = my_function(None)
    assert result is not None or result == default_value
```

---

## 🔍 Debugging Tests

### Run with Detailed Output

```bash
# Show print statements and full tracebacks
pytest -v -s tests/test_corrector.py::TestMinEditDistance::test_identical_strings

# Show local variables in traceback
pytest -v --tb=long

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb
```

### Print Debug Info

```python
def test_with_debug_info(med_default):
    result = med_default.distance("teh", "the")
    
    # Print for debugging (visible with pytest -s)
    print(f"\nResult: {result}")
    print(f"Expected: 1")
    
    assert result == 1
```

### Use pytest fixtures for inspection

```python
def test_inspect_corpus(corpus_builder):
    corpus = corpus_builder.build()
    
    print(f"\nCorpus stats:")
    print(f"  Vocab size: {len(corpus.vocabulary)}")
    print(f"  Unique words: {len(corpus.word_freq)}")
    print(f"  Bigrams: {len(corpus.bigrams)}")
```

---

## 📊 Coverage Analysis

### Generate Coverage Report

```bash
# Generate coverage report (HTML)
pytest --cov=part_a_section1_spelling_corrector --cov-report=html

# View report
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows

# Show coverage in terminal
pytest --cov=part_a_section1_spelling_corrector --cov-report=term-missing
```

### Target Coverage

| Module | Target | Current |
|--------|--------|---------|
| corrector.py | 85% | TBD |
| corpus.py | 80% | TBD |
| build_corpus.py | 75% | TBD |
| gui_app.py | 50%* | TBD |

*GUI testing is harder; focus on core logic

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=part_a_section1_spelling_corrector
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run critical tests before allowing commit
pytest -m critical --tb=short

if [ $? -ne 0 ]; then
    echo "❌ Critical tests failed. Cannot commit."
    exit 1
fi

echo "✅ Tests passed. Committing..."
```

---

## 🐛 Common Issues & Solutions

### Issue: ImportError for modules
**Solution:** Ensure `conftest.py` adds parent directory to path:
```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'part_a_section1_spelling_corrector'))
```

### Issue: Fixtures not found
**Solution:** Ensure `conftest.py` is in `tests/` directory, not subdirectories

### Issue: Tests timeout
**Solution:** Use `@pytest.mark.slow` and run with `pytest -m "not slow"`

### Issue: Mocking arXiv API calls
**Solution:** Use `unittest.mock.patch` as shown in `test_build_corpus.py`

### Issue: Temporary files not cleaning up
**Solution:** Use `pytest.fixture` with `yield` for cleanup:
```python
@pytest.fixture
def temp_file():
    path = create_temp_file()
    yield path
    cleanup(path)  # Runs after test
```

---

## 📈 Test Execution Timeline

### Quick Run (2-3 seconds)
```bash
pytest -m "not slow"  # Excludes performance tests
```

### Full Run (30-60 seconds)
```bash
pytest  # All tests including integration and performance
```

### Coverage Report (60+ seconds)
```bash
pytest --cov=part_a_section1_spelling_corrector --cov-report=html
```

---

## ✅ Pre-Commit Checklist

Before committing code:

- [ ] All critical tests pass: `pytest -m critical`
- [ ] No new test failures: `pytest`
- [ ] Coverage not decreased: `pytest --cov=...`
- [ ] No linting errors: `pylint` or `flake8`
- [ ] No import errors: `python -m py_compile *.py`

---

## 📚 References

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://realpython.com/python-testing/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

## 🚀 Next Steps

1. Run `pytest -v` to see all tests
2. Run `pytest --cov=part_a_section1_spelling_corrector -report=html` for coverage
3. Add tests for new features before implementing (TDD)
4. Review coverage report and add tests for gaps
5. Set up CI/CD with GitHub Actions
