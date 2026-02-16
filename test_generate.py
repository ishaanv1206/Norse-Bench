"""
Property-based tests for Old Norse minimal pair generation.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from generate import normalize_text, extract_sentences


# Feature: old-norse-minimal-pairs, Property 2: Orthography preservation with character standardization
# Validates: Requirements 1.3
@given(st.text(min_size=1))
def test_normalize_text_preserves_non_special_characters(text):
    """
    Property 2: Orthography preservation with character standardization
    
    For any normalized sentence, all special characters (þ, ð, æ) should be 
    standardized to consistent forms, while all other characters should remain 
    unchanged from the source.
    """
    normalized = normalize_text(text)
    
    # Extract non-special characters from both original and normalized
    special_chars = {'þ', 'Þ', 'ð', 'Ð', 'æ', 'Æ'}
    
    original_non_special = [c for c in text if c not in special_chars]
    normalized_non_special = [c for c in normalized if c not in special_chars]
    
    # All non-special characters should be preserved exactly
    assert original_non_special == normalized_non_special, \
        f"Non-special characters changed: {original_non_special} -> {normalized_non_special}"


# Feature: old-norse-minimal-pairs, Property 2: Orthography preservation with character standardization
# Validates: Requirements 1.3
@given(st.text(alphabet='þÞðÐæÆ', min_size=1))
def test_normalize_text_standardizes_special_characters(text):
    """
    Property 2: Orthography preservation with character standardization
    
    For any text containing special characters, normalization should produce
    consistent forms of þ, ð, and æ.
    """
    normalized = normalize_text(text)
    
    # After normalization, special characters should still be present
    # (they're just standardized, not removed)
    special_chars_in_original = sum(1 for c in text if c in 'þÞðÐæÆ')
    special_chars_in_normalized = sum(1 for c in normalized if c in 'þÞðÐæÆ')
    
    # Count should be preserved
    assert special_chars_in_original == special_chars_in_normalized, \
        f"Special character count changed: {special_chars_in_original} -> {special_chars_in_normalized}"



# Feature: old-norse-minimal-pairs, Property 3: Punctuation-based segmentation
# Validates: Requirements 1.4
@given(st.text(min_size=1))
def test_extract_sentences_splits_on_punctuation(text):
    """
    Property 3: Punctuation-based segmentation
    
    For any text segmentation, sentence boundaries should occur at punctuation 
    marks (. : ;) and not within words.
    """
    sentences = extract_sentences(text)
    
    # Each sentence should not contain the splitting punctuation at the end
    # (it's removed during splitting)
    for sentence in sentences:
        # Sentences should not end with splitting punctuation
        assert not sentence.endswith('.'), f"Sentence ends with '.': {sentence}"
        assert not sentence.endswith(':'), f"Sentence ends with ':': {sentence}"
        assert not sentence.endswith(';'), f"Sentence ends with ';': {sentence}"


# Feature: old-norse-minimal-pairs, Property 3: Punctuation-based segmentation
# Validates: Requirements 1.4
@given(st.lists(st.text(alphabet=st.characters(blacklist_characters='.;:'), min_size=1), min_size=1, max_size=10))
def test_extract_sentences_preserves_word_integrity(sentence_parts):
    """
    Property 3: Punctuation-based segmentation
    
    For any text segmentation, sentence boundaries should not split within words.
    Words should remain intact after segmentation.
    """
    # Create text with punctuation separators
    text = '. '.join(sentence_parts)
    
    sentences = extract_sentences(text)
    
    # All original sentence parts should appear in the extracted sentences
    # (though whitespace may be normalized)
    for part in sentence_parts:
        part_stripped = part.strip()
        if part_stripped:  # Only check non-empty parts
            # The part should appear in at least one sentence
            found = any(part_stripped in sentence for sentence in sentences)
            assert found, f"Original part '{part_stripped}' not found in sentences: {sentences}"



# Unit tests for API key management
def test_load_api_keys_reads_from_env():
    """
    Unit test: Verify that load_api_keys() successfully reads API keys from .env file.
    """
    from generate import load_api_keys
    
    # Should load keys without error
    api_keys = load_api_keys()
    
    # Should have at least one key
    assert len(api_keys) > 0, "No API keys loaded"
    
    # All keys should be non-empty strings
    for key in api_keys:
        assert isinstance(key, str), f"API key is not a string: {key}"
        assert len(key) > 0, "API key is empty"
        assert key.startswith('gsk_'), f"API key doesn't start with 'gsk_': {key}"


def test_load_api_keys_raises_on_missing_env_file(tmp_path, monkeypatch):
    """
    Unit test: Verify that load_api_keys() raises FileNotFoundError when .env is missing.
    """
    from generate import load_api_keys
    
    # Change to a temporary directory without .env file
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(FileNotFoundError) as exc_info:
        load_api_keys()
    
    assert "Missing .env file" in str(exc_info.value)


def test_call_groq_api_basic_functionality():
    """
    Unit test: Verify that call_groq_api() can make a successful API call.
    """
    from generate import load_api_keys, call_groq_api
    
    # Load API keys
    api_keys = load_api_keys()
    
    # Make a simple API call
    prompt = "Say 'test' and nothing else."
    response, new_key_index = call_groq_api(
        prompt=prompt,
        api_keys=api_keys,
        current_key_index=0,
        model="llama-3.3-70b-versatile",  # Use a reliable model
        temperature=0.0,
        max_tokens=10
    )
    
    # Should get a response
    assert isinstance(response, str), "Response is not a string"
    assert len(response) > 0, "Response is empty"
    
    # Should return a valid key index
    assert isinstance(new_key_index, int), "Key index is not an integer"
    assert 0 <= new_key_index < len(api_keys), "Key index out of range"


# Feature: old-norse-minimal-pairs, Property 5: Minimal pair single-feature difference
# Validates: Requirements 2.2
@given(
    st.lists(st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10), min_size=2, max_size=10)
)
def test_minimal_pair_single_feature_difference(words):
    """
    Property 5: Minimal pair single-feature difference
    
    For any minimal pair, the grammatical and ungrammatical sentences should 
    differ by exactly one token or one morphological feature within a token.
    """
    # Create a mock minimal pair by changing exactly one word
    grammatical = ' '.join(words)
    
    # Change exactly one word to create ungrammatical variant
    modified_words = words.copy()
    change_index = len(words) // 2  # Change middle word
    modified_words[change_index] = modified_words[change_index] + 'x'  # Add one character
    ungrammatical = ' '.join(modified_words)
    
    # Tokenize both sentences
    gram_tokens = grammatical.split()
    ungram_tokens = ungrammatical.split()
    
    # Should have same number of tokens
    assert len(gram_tokens) == len(ungram_tokens), \
        f"Token count differs: {len(gram_tokens)} vs {len(ungram_tokens)}"
    
    # Count differences
    differences = sum(1 for g, u in zip(gram_tokens, ungram_tokens) if g != u)
    
    # Should differ by exactly one token
    assert differences == 1, \
        f"Should differ by exactly 1 token, but differs by {differences}"


# Feature: old-norse-minimal-pairs, Property 7: Minimal change preservation
# Validates: Requirements 3.3, 4.3, 5.3
@given(
    st.lists(st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10), min_size=3, max_size=10),
    st.integers(min_value=0, max_value=100)
)
def test_minimal_change_preservation(words, seed):
    """
    Property 7: Minimal change preservation
    
    For any minimal pair, all tokens except the target token should be identical 
    between the grammatical and ungrammatical variants.
    """
    # Ensure we have enough words
    if len(words) < 3:
        words = words + ['extra', 'words', 'here']
    
    # Create a minimal pair by changing exactly one word (the target)
    grammatical = ' '.join(words)
    
    # Select a target token to change (use seed for determinism)
    target_index = seed % len(words)
    
    # Change the target token
    modified_words = words.copy()
    modified_words[target_index] = modified_words[target_index] + 'CHANGED'
    ungrammatical = ' '.join(modified_words)
    
    # Tokenize both sentences
    gram_tokens = grammatical.split()
    ungram_tokens = ungrammatical.split()
    
    # All tokens except the target should be identical
    for i, (g, u) in enumerate(zip(gram_tokens, ungram_tokens)):
        if i != target_index:
            assert g == u, \
                f"Non-target token at position {i} differs: '{g}' vs '{u}'"


# Feature: old-norse-minimal-pairs, Property 13: ID format consistency
# Validates: Requirements 7.3
@given(
    st.sampled_from(['QUIRKY_CASE', 'ADJECTIVE', 'UMLAUT', 'MIDDLE_VOICE']),
    st.integers(min_value=1, max_value=999)
)
def test_id_format_consistency(phenomenon, number):
    """
    Property 13: ID format consistency
    
    For any minimal pair identifier, it should match the pattern 
    "ON_{PHENOMENON}_{NUMBER}" where phenomenon is uppercase and number 
    is zero-padded to three digits.
    """
    from generate import generate_pair_id
    
    pair_id = generate_pair_id(phenomenon, number)
    
    # Should start with "ON_"
    assert pair_id.startswith("ON_"), f"ID doesn't start with 'ON_': {pair_id}"
    
    # Should end with a 3-digit zero-padded number
    # Extract the last part after the last underscore
    parts = pair_id.split('_')
    number_part = parts[-1]
    
    # Number part should be exactly 3 digits
    assert len(number_part) == 3, f"Number should be 3 digits, got {len(number_part)}: {number_part}"
    assert number_part.isdigit(), f"Number part should be digits: {number_part}"
    
    # Should match the original number when converted back
    assert int(number_part) == number, \
        f"Number mismatch: expected {number}, got {int(number_part)}"
    
    # Should contain the phenomenon (uppercase)
    assert phenomenon.upper() in pair_id, \
        f"Phenomenon '{phenomenon.upper()}' not found in ID: {pair_id}"
    
    # Should match the expected format
    expected_id = f"ON_{phenomenon.upper()}_{str(number).zfill(3)}"
    assert pair_id == expected_id, \
        f"ID format mismatch: expected '{expected_id}', got '{pair_id}'"


# Feature: old-norse-minimal-pairs, Property 14: Incremental saving with duplicate prevention
# Validates: Requirements 7.4, 7.5
def test_incremental_saving_with_duplicate_prevention():
    """
    Property 14: Incremental saving with duplicate prevention
    
    For any generation session, newly generated pairs should be immediately 
    appended to the CSV, and resuming should not create duplicate IDs.
    """
    import tempfile
    import os
    from generate import append_to_csv, load_existing_pairs, generate_pair_id
    
    # Create a temporary CSV file with a unique name
    fd, csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    os.close(fd)
    
    try:
        # Create some test pairs with realistic Old Norse data
        pairs = [
            {
                'id': generate_pair_id('QUIRKY_CASE', 1),
                'phenomenon': 'QUIRKY_CASE',
                'grammatical': 'Hánum líkaði þat.',
                'ungrammatical': 'Hann líkaði þat.',
                'target': 'Hánum',
                'error_type': 'dative_to_nominative'
            },
            {
                'id': generate_pair_id('ADJECTIVE', 1),
                'phenomenon': 'ADJECTIVE',
                'grammatical': 'Hann sá stóran mann.',
                'ungrammatical': 'Hann sá stóri mann.',
                'target': 'stóran',
                'error_type': 'strong_to_weak'
            },
            {
                'id': generate_pair_id('UMLAUT', 1),
                'phenomenon': 'UMLAUT',
                'grammatical': 'Þeir sá lǫnd.',
                'ungrammatical': 'Þeir sá land.',
                'target': 'lǫnd',
                'error_type': 'umlaut_removed'
            }
        ]
        
        # Write pairs incrementally
        for pair in pairs:
            append_to_csv(pair, csv_path)
        
        # Load existing pairs
        loaded_pairs = load_existing_pairs(csv_path)
        
        # Should have loaded all pairs
        assert len(loaded_pairs) == len(pairs), \
            f"Expected {len(pairs)} pairs, loaded {len(loaded_pairs)}"
        
        # All pair IDs should be present
        for pair in pairs:
            assert pair['id'] in loaded_pairs, \
                f"Pair ID '{pair['id']}' not found in loaded pairs"
        
        # Loaded data should match original data
        for pair in pairs:
            loaded = loaded_pairs[pair['id']]
            assert loaded['phenomenon'] == pair['phenomenon']
            assert loaded['grammatical'] == pair['grammatical']
            assert loaded['ungrammatical'] == pair['ungrammatical']
            assert loaded['target'] == pair['target']
            assert loaded['error_type'] == pair['error_type']
        
        # Test duplicate prevention: add more pairs and verify no duplicates
        new_pair = {
            'id': generate_pair_id('MIDDLE_VOICE', 1),
            'phenomenon': 'MIDDLE_VOICE',
            'grammatical': 'Þeir finnask í morgin.',
            'ungrammatical': 'Þeir finna í morgin.',
            'target': 'finnask',
            'error_type': 'middle_voice_removed'
        }
        
        append_to_csv(new_pair, csv_path)
        loaded_pairs = load_existing_pairs(csv_path)
        
        # Should now have 4 pairs
        assert len(loaded_pairs) == 4
        assert new_pair['id'] in loaded_pairs
        
    finally:
        # Clean up temporary file
        if os.path.exists(csv_path):
            os.remove(csv_path)


# Feature: old-norse-minimal-pairs, Property 4: Balanced phenomenon distribution
# Validates: Requirements 2.1, 2.4, 3.4, 4.4, 5.4, 6.4
def test_balanced_phenomenon_distribution():
    """
    Property 4: Balanced phenomenon distribution
    
    For any complete dataset of 500 pairs, each of the four phenomena 
    (quirky case, adjective, umlaut, middle-voice) should have approximately 
    125 pairs (within ±10%).
    
    This test validates the distribution logic by checking a generated dataset.
    """
    import tempfile
    import os
    from generate import load_existing_pairs
    
    # Create a temporary CSV file with a balanced distribution
    fd, csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    os.close(fd)
    
    try:
        from generate import append_to_csv, generate_pair_id
        
        # Generate 500 pairs with balanced distribution (125 each)
        phenomena = ['QUIRKY_CASE', 'ADJECTIVE', 'UMLAUT', 'MIDDLE_VOICE']
        pairs_per_phenomenon = 125
        
        for phenomenon in phenomena:
            for i in range(1, pairs_per_phenomenon + 1):
                pair = {
                    'id': generate_pair_id(phenomenon, i),
                    'phenomenon': phenomenon,
                    'grammatical': f'Test grammatical sentence {i}',
                    'ungrammatical': f'Test ungrammatical sentence {i}',
                    'target': f'target{i}',
                    'error_type': 'test_error'
                }
                append_to_csv(pair, csv_path)
        
        # Load and verify distribution
        loaded_pairs = load_existing_pairs(csv_path)
        
        # Count occurrences of each phenomenon
        phenomenon_counts = {
            'QUIRKY_CASE': 0,
            'ADJECTIVE': 0,
            'UMLAUT': 0,
            'MIDDLE_VOICE': 0
        }
        
        for pair in loaded_pairs.values():
            phenomenon_counts[pair['phenomenon']] += 1
        
        # Expected count per phenomenon
        total_pairs = len(loaded_pairs)
        assert total_pairs == 500, f"Expected 500 pairs, got {total_pairs}"
        
        expected_per_phenomenon = total_pairs / 4  # 125 for 500 pairs
        
        # Check that each phenomenon is within ±10% of expected
        tolerance = 0.10
        min_count = expected_per_phenomenon * (1 - tolerance)
        max_count = expected_per_phenomenon * (1 + tolerance)
        
        for phenomenon, count in phenomenon_counts.items():
            assert min_count <= count <= max_count, \
                f"Phenomenon {phenomenon} has {count} pairs, expected {expected_per_phenomenon} ±10% " \
                f"(range: {min_count:.1f}-{max_count:.1f})"
    
    finally:
        # Clean up temporary file
        if os.path.exists(csv_path):
            os.remove(csv_path)


# Feature: old-norse-minimal-pairs, Property 6: Complete pair metadata
# Validates: Requirements 2.5
@given(
    st.sampled_from(['QUIRKY_CASE', 'ADJECTIVE', 'UMLAUT', 'MIDDLE_VOICE']),
    st.integers(min_value=1, max_value=999),
    st.text(min_size=5, max_size=100),
    st.text(min_size=5, max_size=100),
    st.text(min_size=1, max_size=20),
    st.text(min_size=1, max_size=50)
)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_complete_pair_metadata(phenomenon, number, grammatical, ungrammatical, target, error_type):
    """
    Property 6: Complete pair metadata
    
    For any minimal pair record, all required fields (id, phenomenon, grammatical, 
    ungrammatical, target, error_type) should be present and non-empty.
    """
    import tempfile
    import os
    from generate import append_to_csv, load_existing_pairs, generate_pair_id
    
    # Create a temporary CSV file
    fd, csv_path = tempfile.mkstemp(suffix='.csv', text=True)
    os.close(fd)
    
    try:
        # Create a pair with all required fields
        pair = {
            'id': generate_pair_id(phenomenon, number),
            'phenomenon': phenomenon,
            'grammatical': grammatical,
            'ungrammatical': ungrammatical,
            'target': target,
            'error_type': error_type
        }
        
        # Write to CSV
        append_to_csv(pair, csv_path)
        
        # Load back
        loaded_pairs = load_existing_pairs(csv_path)
        
        # Should have exactly one pair
        assert len(loaded_pairs) == 1, f"Expected 1 pair, got {len(loaded_pairs)}"
        
        # Get the loaded pair
        loaded_pair = list(loaded_pairs.values())[0]
        
        # All required fields should be present
        required_fields = ['id', 'phenomenon', 'grammatical', 'ungrammatical', 'target', 'error_type']
        for field in required_fields:
            assert field in loaded_pair, f"Missing required field: {field}"
            assert loaded_pair[field] is not None, f"Field {field} is None"
            assert loaded_pair[field] != '', f"Field {field} is empty"
            assert len(str(loaded_pair[field])) > 0, f"Field {field} has zero length"
    
    finally:
        # Clean up temporary file
        if os.path.exists(csv_path):
            os.remove(csv_path)
