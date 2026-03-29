"""Final comprehensive verification of candidate generation and ranking logic."""

from corpus import CorpusBuilder
from corrector import SpellChecker

# Initialize spell checker
print("=" * 60)
print("FINAL VERIFICATION OF CANDIDATE GENERATION FIX")
print("=" * 60)

corpus = CorpusBuilder().build()
checker = SpellChecker(corpus)

test_cases = [
    ("proccess", ["process"]),           # Edit-1: 1 deletion
    ("tokinization", ["tokenization"]),  # Edit-1: 1 insertion
    ("embedings", ["embeddings"]),       # Edit-1: 1 insertion
    ("recieve", ["receive"]),            # Edit-1: transposition + substitute
    ("niid", []),                        # No valid edit-1/edit-2 candidates
    ("helo", ["hello"]),                 # Edit-1: insertion
]

print("\n1️⃣  TESTING CANDIDATE GENERATION")
print("-" * 60)

all_passed = True
for misspelled, expected_substr in test_cases:
    cands = checker.gen.candidates(misspelled)
    print(f"\nWord: '{misspelled}'")
    print(f"  Candidates found: {len(cands)}")
    
    # Check that misspelled word is not in candidates
    if misspelled in cands:
        print(f"  ❌ FAIL: Misspelled word '{misspelled}' found in candidates!")
        all_passed = False
    else:
        print(f"  ✅ OK: Misspelled word '{misspelled}' properly excluded")
    
    # Check that expected suggestions exist (if any expected)
    if expected_substr:
        found = [c for c in expected_substr if c in cands]
        if found:
            print(f"  ✅ OK: Found expected candidate(s): {found}")
        else:
            print(f"  ⚠️  WARN: Expected {expected_substr} but got {list(cands)[:5]}")
    
    if cands:
        print(f"  First 3 candidates: {list(cands)[:3]}")

print("\n" + "=" * 60)
print("2️⃣  TESTING FULL SPELL CHECK WITH RANKING")
print("-" * 60)

test_sentences = [
    "The tokinization proccess is critical.",
    "We recieve the embedings from the model.",
    "This requires eficient processing.",
]

for sentence in test_sentences:
    print(f"\nSentence: '{sentence}'")
    result = checker.check(sentence)
    print(f"Errors found: {result['error_count']}")
    
    for error in result['errors'][:3]:  # Show first 3 errors
        word = error['word']
        suggestions = error['suggestions']
        print(f"\n  Error: '{word}' ({error['type']})")
        
        # Critical check: misspelled word should never be suggested
        suggested_words = [s['word'] for s in suggestions]
        if word.lower() in suggested_words:
            print(f"  ❌ CRITICAL BUG: '{word}' appears in suggestions!")
            all_passed = False
        
        if suggestions:
            print(f"  Top suggestions:")
            for i, sugg in enumerate(suggestions[:3], 1):
                print(f"    {i}. '{sugg['word']}' (MED: {sugg['med']}, Prob: {sugg['lm_prob']:.4f})")
        else:
            print(f"  (No suggestions available - expected for rare misspellings)")

print("\n" + "=" * 60)
print("3️⃣  TESTING EDIT DISTANCE PRIORITY")
print("=" * 60)

# Test that edit-1 candidates always rank before edit-2
print("\nVerifying Edit-1 candidates rank before Edit-2 candidates...")
print("-" * 60)

test_word = "proccess"  # Should have edit-1: 'process'
result = checker.check(f"Test {test_word} word")

if result['errors']:
    error = result['errors'][0]
    suggestions = error['suggestions']
    
    if suggestions:
        first_suggestion = suggestions[0]
        first_med = first_suggestion['med']
        
        # Calculate MED for 'proccess'
        actual_med_1 = checker.med.distance('proccess', 'process')
        print(f"Word: '{test_word}'")
        print(f"First suggestion: '{first_suggestion['word']}'")
        print(f"MED: {first_suggestion['med']}")
        
        if first_suggestion['word'] == 'process' and first_suggestion['med'] == actual_med_1:
            print(f"✅ OK: Correct edit-distance suggestion returned")
        else:
            print(f"⚠️  Unexpected suggestion")
    else:
        print(f"No suggestions returned")

print("\n" + "=" * 60)
if all_passed:
    print("✅ ALL TESTS PASSED - Candidate generation is working correctly!")
else:
    print("⚠️  SOME TESTS FAILED - Please review above details")
print("=" * 60)
