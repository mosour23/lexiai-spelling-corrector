"""Test script to verify misspelled words are excluded from candidate suggestions."""

from corpus import CorpusBuilder
from corrector import SpellChecker

# Initialize spell checker
corpus = CorpusBuilder().build()
checker = SpellChecker(corpus)

# Show corpus info
print(f"Vocabulary size: {len(corpus.vocabulary)}")
print(f"Total tokens: {sum(corpus.word_freq.values())}")
print()

# Test that candidates are properly filtered
print("="*50)
print("Testing candidate generation and filtering")
print("="*50)

gen = checker.gen
test_words = ["proccess", "tokinization", "giid", "xyzabc"]

for test_word in test_words:
    print(f"\nWord: '{test_word}'")
    print("-" * 40)
    
    e1 = gen.edits1(test_word)
    e2 = gen.edits2(test_word) if not e1 else set()
    all_cands = gen.candidates(test_word)
    
    # Check if misspelled word is in any set
    if test_word in e1:
        print(f"  ❌ BUG: '{test_word}' in edit-1!")
    if test_word in e2:
        print(f"  ❌ BUG: '{test_word}' in edit-2!")
    if test_word in all_cands:
        print(f"  ❌ BUG: '{test_word}' in candidates!")
    
    print(f"  Edit-1 candidates: {len(e1)} (first 5: {list(e1)[:5]})")
    print(f"  Edit-2 candidates: {len(e2)}")
    print(f"  Total candidates: {len(all_cands)} (first 5: {list(all_cands)[:5]})")
    
    if test_word not in e1 and test_word not in e2 and test_word not in all_cands:
        print(f"  ✅ OK: '{test_word}' properly excluded from all candidate sets")

# Now test full spell check flow
print("\n" + "="*50)
print("Testing spell checker with full flow")
print("="*50)

test_text = "The tokinization proccess uses embedings."
print(f"\nInput: '{test_text}'")
print("-" * 40)

result = checker.check(test_text)
print(f"Errors found: {result['error_count']}")

for error in result['errors'][:3]:  # Show first 3 errors
    word = error['word']
    print(f"\nError: '{word}' ({error['type']})")
    
    if error['suggestions']:
        print(f"  Suggestions:")
        for i, sugg in enumerate(error['suggestions'][:3], 1):
            print(f"    {i}. '{sugg['word']}' (MED: {sugg['med']})")
        
        # Critical check: misspelled word should never be suggested
        suggested_words = [s['word'] for s in error['suggestions']]
        if word in suggested_words:
            print(f"  ❌ CRITICAL BUG: '{word}' appears in suggestions!")
        else:
            print(f"  ✅ OK: '{word}' NOT in suggestions")
    else:
        print(f"  (No suggestions available)")
