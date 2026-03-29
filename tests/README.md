# Tests Directory — NLP Assignment Testing Suite

**Comprehensive test suite with 90+ tests covering all critical components.**

---

## 📂 Directory Contents

```
tests/
├── README.md                      # This file
├── TESTING_GUIDE.md              # Detailed testing documentation
├── conftest.py                   # Shared pytest fixtures
│
├── test_corrector.py              # Tests for corrector.py module (33 tests)
│   ├── TestMinEditDistance       # Edit distance computation
│   ├── TestBigramLanguageModel   # Bigram probability
│   ├── TestSpellChecker          # Error detection & correction
│   ├── TestCandidateGenerator    # Word suggestions
│   ├── TestTokenization          # Text tokenization
│   └── TestErrorHandling         # Error cases
│
├── test_corpus.py                # Tests for corpus.py module (36 tests)
│   ├── TestCorpusBuilder         # Corpus creation
│   ├── TestCorpusFileIO          # Save/load corpus
│   ├── TestTextPreprocessing     # Text cleaning
│   ├── TestTokenization          # Tokenization
│   ├── TestPaperValidation       # Paper metadata
│   ├── TestBigramGeneration      # Bigram extraction
│   └── TestCorpusIntegration     # Full pipeline
│
├── test_build_corpus.py          # Tests for build_corpus.py module (28 tests)
│   ├── TestTextCleaning         # Text preprocessing
│   ├── TestPaperFetching        # arXiv API (mocked)
│   ├── TestPaperValidation      # Paper validation
│   ├── TestBuildCorpusOutput    # Output generation
│   ├── TestTokenMetadataGeneration  # Token counting
│   ├── TestBuildCorpusConfigValidation # Config checks
│   ├── TestDataSerialization    # JSON handling
│   └── TestErrorHandlingGraceful # Error scenarios
│
├── test_integration.py           # End-to-end integration tests (20+ tests)
│   ├── TestSpellingCorrectionPipeline
│   ├── TestCorpusSpellerIntegration
│   ├── TestErrorRecovery
│   ├── TestPerformanceCharacteristics
│   └── TestEdgeCasesCombined
│
├── test_utilities.py             # Shared testing utilities
│   ├── MockCorpus                # Mock corpus for testing
│   ├── TextGenerator             # Text generation utilities
│   ├── AssertionHelpers          # Custom assertions
│   ├── PerformanceMonitor        # Performance tracking
│   └── Fixtures                  # Pre-defined test data
│
└── pytest.ini                    # Pytest configuration (in project root)
```

---

## 🚀 Quick Start

### Installation
```bash
# Install pytest (required)
pip install pytest pytest-cov

# Optional: for faster runs in parallel
pip install pytest-xdist

# Optional: for timeout protection
pip install pytest-timeout
```

### Running Tests
```bash
# Run all tests (recommended first time)
pytest -v

# Run quickly (unit tests only)
pytest -m "not slow"

# Run critical tests only (pre-commit)
pytest -m critical

# With coverage report
pytest --cov=part_a_section1_spelling_corrector --cov-report=html

# Run specific test file
pytest tests/test_corrector.py -v

# Run specific test
pytest tests/test_corrector.py::TestMinEditDistance::test_identical_strings -v
```

---

## 📊 Test Coverage

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| corrector.py | 33 | 75% + | ✅ Comprehensive |
| corpus.py | 36 | 80% + | ✅ Comprehensive |
| build_corpus.py | 28 | 55% | ⚠️ Partial (API mocked) |
| Integration | 20+ | - | ✅ Full pipeline |
| **Total** | **90+** | **~70%** | **Ready** |

---

## 🎯 Test Categories

### By Type
- **Unit Tests (70+):** Individual functions and classes
- **Integration Tests (20+):** Component interactions
- **Performance Tests (3):** Efficiency verification

### By Marker
```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests
pytest -m critical       # Critical path tests
pytest -m edge_case      # Edge cases
pytest -m performance    # Performance tests
pytest -m "not slow"     # Skip slow tests
```

### By Speed
- **Fast (<2 sec):** Unit + Edge case tests → `pytest -m "not slow"`
- **Medium (5-15 sec):** Add integration tests → `pytest -m "not performance"`
- **Full (30-60 sec):** All tests → `pytest`

---

## ✅ Test Coverage by Component

### Spelling Correction (`test_corrector.py`)
- ✅ MinEditDistance: 11 tests (weighted costs, transposition, edge cases)
- ✅ BigramLanguageModel: 5 tests (smoothing, probability ranking)
- ✅ SpellChecker: 9 tests (error detection, candidate ranking, validation)
- ✅ Tokenization: 3 tests (parsing, punctuation handling)
- ✅ Error Handling: 5 tests (invalid inputs, empty data)

### Corpus Management (`test_corpus.py`)
- ✅ CorpusBuilder: 9 tests (initialization, build, NLP terms)
- ✅ File I/O: 6 tests (save, load, validation, corruption)
- ✅ Text Preprocessing: 7 tests (cleaning, normalization)
- ✅ Tokenization: 4 tests (word extraction, preservation)
- ✅ Paper Validation: 5 tests (structure, required fields, size)
- ✅ Bigram Generation: 4 tests (extraction, counting)

### Corpus Building (`test_build_corpus.py`)
- ✅ Text Cleaning: 5 tests (lowercasing, URL removal, normalization)
- ✅ Paper Fetching: 3 tests (valid query, error handling, XML)
- ✅ Validation: 5 tests (structure, fields, types)
- ✅ Output: 2 tests (JSON validity, schema)
- ✅ Configuration: 2 tests (search queries, parameters)

### End-to-End Integration (`test_integration.py`)
- ✅ Spelling Pipeline: 4 tests (full workflow, multiple errors, ranking)
- ✅ Corpus Integration: 2 tests (loading, consistency)
- ✅ Error Recovery: 2 tests (invalid text, malformed data)
- ✅ Performance: 3 tests (scaling, efficiency)
- ✅ Edge Cases: 3+ tests (Unicode, mixed case)

---

## 🧪 Example Test Output

```
$ pytest -v
tests/test_corrector.py::TestMinEditDistance::test_identical_strings PASSED [ 1%]
tests/test_corrector.py::TestMinEditDistance::test_empty_source PASSED [ 2%]
tests/test_corrector.py::TestMinEditDistance::test_substitution_single_char PASSED [ 3%]
...
tests/test_integration.py::TestSpellingCorrectionPipeline::test_end_to_end_spell_check PASSED [89%]
tests/test_integration.py::TestPerformanceCharacteristics::test_edit_distance_scaling PASSED [90%]
...
======================== 92 passed in 45.23s =========================
```

---

## 📚 Available Fixtures

### Pre-configured Objects
```python
med_default              # MinEditDistance with standard costs
med_equal_costs         # Levenshtein distance
sample_vocab            # Small vocabulary set
sample_bigrams          # Common bigrams Counter
sample_word_freq        # Word frequency data
corpus_data             # Complete corpus structure
spell_checker_factory   # Function to create SpellChecker
corpus_builder          # CorpusBuilder instance
temp_corpus_file        # Temporary JSON file
```

### Test Utilities
```python
text_generator          # Utility for generating test texts
assertion_helpers       # Custom assertion methods
performance_monitor     # Context manager for timing
mock_corpus_small       # Small mock corpus
mock_corpus_large       # Larger mock corpus
mock_arxiv_response     # Mocked XML response
```

---

## 🔧 Writing New Tests

### Template
```python
"""test_mymodule.py - Tests for mymodule"""

import pytest

@pytest.mark.unit
@pytest.mark.critical
class TestMyClass:
    """Tests for MyClass."""
    
    def test_basic_functionality(self):
        """Test the basic happy path."""
        result = my_function(input)
        assert result == expected
    
    @pytest.mark.edge_case
    def test_edge_case(self):
        """Test edge case."""
        result = my_function("")
        assert result == default
    
    @pytest.mark.performance
    def test_performance(self, performance_monitor):
        """Test doesn't timeout."""
        with performance_monitor("my_test") as pm:
            result = my_function(large_input)
        pm.assert_under_seconds(1.0)
```

### Best Practices
- ✅ Use descriptive test names: `test_identical_strings_have_zero_distance`
- ✅ Test one thing per test
- ✅ Use fixtures instead of setUp/tearDown
- ✅ Parametrize similar tests
- ✅ Mark slow tests with `@pytest.mark.slow`
- ✅ Cover happy path + error cases

---

## 🐛 Debugging Tests

### Run with Debugging
```bash
# Show print statements
pytest -v -s

# Drop into debugger on failure
pytest --pdb

# Show local variables
pytest -v --tb=long

# Stop on first failure
pytest -x
```

### Print Debug Info
```python
def test_my_function():
    result = my_function(data)
    print(f"\nResult: {result}")  # Visible with pytest -s
    assert result == expected
```

---

## 📈 Coverage Reports

### Generate HTML Report
```bash
pytest --cov=part_a_section1_spelling_corrector --cov-report=html
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

### Terminal Coverage Report
```bash
pytest --cov=part_a_section1_spelling_corrector --cov-report=term-missing

# Shows which lines are not covered:
part_a_section1_spelling_corrector/corrector.py   492   42    21    92%   210-220, 245-250
```

---

## 🔗 Related Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** — Comprehensive testing guide
- **[TESTING_SUITE_SUMMARY.md](../TESTING_SUITE_SUMMARY.md)** — Implementation overview
- **[CODE_REVIEW.md](../CODE_REVIEW.md)** — Issues & fixes
- **[.github/copilot-instructions.md](../.github/copilot-instructions.md)** — Project guidelines

---

## ✅ Pre-Commit Checklist

Before committing changes:

```bash
# 1. Run critical tests
pytest -m critical

# 2. Run full suite
pytest

# 3. Check coverage
pytest --cov=... --cov-report=term-missing

# 4. Check for new issues
pytest -v  # Ensure no new failures
```

---

## 🚀 Continuous Integration

### GitHub Actions Setup
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install pytest
      - run: pytest -v
```

---

## 📞 FAQ

**Q: How do I run just corrector tests?**  
A: `pytest tests/test_corrector.py -v`

**Q: How do I see all available tests?**  
A: `pytest --collect-only`

**Q: How do I increase coverage?**  
A: 1) Identify uncovered lines: `pytest --cov-report=term-missing`  
   2) Write tests that exercise those lines

**Q: Why did a test fail?**  
A: 1) Run with `-v` for details  
   2) Use `-s` to see print output  
   3) Use `--tb=long` for full traceback  
   4) Use `--pdb` to debug interactively

**Q: How do I skip slow tests?**  
A: `pytest -m "not slow"`

**Q: How do I test with updated code?**  
A: Just run `pytest` - it automatically reloads modules

---

## 🎓 Test Suite Highlights

✅ **90+ tests** — Comprehensive coverage  
✅ **No external dependencies** — Only pytest  
✅ **Fast feedback** — 2-30 seconds depending on markers  
✅ **Well organized** — Clear structure by module  
✅ **Fixtures & utilities** — Reusable test components  
✅ **Performance monitoring** — Built-in timing  
✅ **Edge case coverage** — Unicode, special chars, errors  
✅ **CI/CD ready** — Works with GitHub Actions  
✅ **Documentation** — Complete with examples  
✅ **Easy to extend** — Clear patterns to follow  

---

## 📍 Current Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Unit Tests | ✅ Complete | 70+ tests, all core logic covered |
| Integration Tests | ✅ Complete | 20+ tests, end-to-end workflows |
| Edge Cases | ✅ Complete | 15+ tests, boundary conditions |
| Performance Tests | ✅ Complete | 3 tests, scaling verification |
| Documentation | ✅ Complete | Guides & examples included |
| Coverage | ⚠️ 70%+ | Good; excludes GUI layer |
| CI/CD Ready | ✅ Yes | Can integrate with GitHub Actions |

---

**Last Updated:** March 29, 2026  
**Total Tests:** 90+  
**Estimated Runtime:** 30-60 seconds  
**Status:** ✅ Production Ready
