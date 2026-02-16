"""
Data acquisition and minimal pair generation for Old Norse grammatical evaluation.
"""

import os
import re
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
from groq import Groq
import norsecorpus.reader as ncr


def load_corpus() -> str:
    """
    Load texts from the norsecorpus package.
    
    Returns:
        Combined text from the corpus
    """
    texts = []
    
    # Get all available texts from the corpus
    available_texts = ncr.get_available_texts()
    
    # Load prose texts from the corpus
    for filename in available_texts:
        try:
            # Read words from each text using the file path
            text_data = ncr.read_tei_words(available_texts[filename])
            
            # text_data structure: text_data[chapter][paragraph][sentence] = list of words
            for chapter in text_data:
                for paragraph in chapter:
                    for sentence in paragraph:
                        if sentence:  # sentence is a list of words
                            # Join words to form sentence text
                            sentence_text = " ".join(word for word in sentence if word)
                            if sentence_text.strip():
                                texts.append(sentence_text.strip())
        except Exception as e:
            # Skip texts that can't be loaded
            print(f"Warning: Could not load {filename}: {e}")
            continue
    
    return " ".join(texts)


def normalize_text(sentence: str) -> str:
    """
    Standardize special characters (þ, ð, æ) while preserving orthography.
    
    Args:
        sentence: Input sentence with potential character variations
        
    Returns:
        Normalized sentence with standardized special characters
    """
    # Standardize thorn variations
    sentence = sentence.replace('Þ', 'Þ')  # Ensure uppercase thorn is consistent
    sentence = sentence.replace('þ', 'þ')  # Ensure lowercase thorn is consistent
    
    # Standardize eth variations
    sentence = sentence.replace('Ð', 'Ð')  # Ensure uppercase eth is consistent
    sentence = sentence.replace('ð', 'ð')  # Ensure lowercase eth is consistent
    
    # Standardize ash variations
    sentence = sentence.replace('Æ', 'Æ')  # Ensure uppercase ash is consistent
    sentence = sentence.replace('æ', 'æ')  # Ensure lowercase ash is consistent
    
    return sentence


def extract_sentences(text: str) -> List[str]:
    """
    Segment text using punctuation rules (. : ;).
    
    Args:
        text: Input text to segment
        
    Returns:
        List of sentences split by punctuation
    """
    # Split on sentence-ending punctuation: . : ;
    # Use regex to split while preserving the structure
    sentences = re.split(r'[.;:]', text)
    
    # Clean up sentences: strip whitespace and filter empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def filter_usable_sentences(sentences: List[str]) -> List[str]:
    """
    Select sentences that are grammatically complete, contain relevant phenomena,
    and are of appropriate length (5-20 words).
    
    Args:
        sentences: List of candidate sentences
        
    Returns:
        Filtered list of usable sentences
    """
    usable = []
    
    for sentence in sentences:
        # Count words (split by whitespace)
        words = sentence.split()
        word_count = len(words)
        
        # Check length constraint (5-20 words)
        if word_count < 5 or word_count > 20:
            continue
        
        # Filter out poetry markers, editorial notes, line numbers
        # Poetry often has specific markers or unusual formatting
        if any(marker in sentence for marker in ['[', ']', '(', ')', '<', '>']):
            continue
        
        # Filter out sentences that are just numbers or very short fragments
        if sentence.isdigit():
            continue
        
        # Check for basic sentence completeness (should have at least one verb-like word)
        # This is a heuristic - Old Norse verbs often end in common patterns
        # We'll be permissive here and let the LLM filter further
        
        usable.append(sentence)
    
    return usable



def load_api_keys() -> List[str]:
    """
    Read multiple Groq API keys from .env file.
    
    Returns:
        List of API keys loaded from environment variables
        
    Raises:
        FileNotFoundError: If .env file is missing
        ValueError: If no API keys are found in .env file
    """
    # Load environment variables from .env file
    if not os.path.exists('.env'):
        raise FileNotFoundError(
            "Missing .env file. Please create a .env file with your Groq API keys. "
            "Format: GROQ_API_KEY_1=your_key_here, GROQ_API_KEY_2=your_key_here, etc."
        )
    
    load_dotenv()
    
    # Collect all API keys from environment variables
    api_keys = []
    key_index = 1
    
    while True:
        key_name = f"GROQ_API_KEY_{key_index}"
        key_value = os.getenv(key_name)
        
        if key_value is None:
            break
        
        # Strip whitespace and quotes
        key_value = key_value.strip().strip('"').strip("'")
        
        if key_value:
            api_keys.append(key_value)
        
        key_index += 1
    
    if not api_keys:
        raise ValueError(
            "No API keys found in .env file. Please add at least one key with format: "
            "GROQ_API_KEY_1=your_key_here"
        )
    
    return api_keys


def call_groq_api(
    prompt: str,
    api_keys: List[str],
    current_key_index: int = 0,
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> Tuple[str, int]:
    """
    Call Groq API with automatic key rotation on rate limit errors.
    
    Args:
        prompt: The prompt to send to the API
        api_keys: List of available API keys
        current_key_index: Index of the current API key to use
        model: Model name to use (default: gpt-oss-120b)
        temperature: Temperature setting for generation
        max_tokens: Maximum tokens to generate
        
    Returns:
        Tuple of (response_text, new_key_index)
        
    Raises:
        RuntimeError: If all API keys are exhausted due to rate limits
    """
    import time
    from groq import RateLimitError
    
    attempts = 0
    max_attempts = len(api_keys)
    
    while attempts < max_attempts:
        try:
            # Get current API key
            api_key = api_keys[current_key_index]
            
            # Create Groq client with current key
            client = Groq(api_key=api_key)
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30.0
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            return response_text, current_key_index
            
        except RateLimitError as e:
            # Rate limit hit - rotate to next key
            print(f"Rate limit hit on key {current_key_index + 1}. Rotating to next key...")
            current_key_index = (current_key_index + 1) % len(api_keys)
            attempts += 1
            
            # If we've tried all keys, raise error
            if attempts >= max_attempts:
                raise RuntimeError(
                    "All API keys have been exhausted due to rate limits. "
                    "Please wait for rate limits to reset or add more API keys to .env file."
                )
            
            # Brief pause before trying next key
            time.sleep(1)
            
        except Exception as e:
            # For other errors, re-raise with context
            raise RuntimeError(f"API call failed: {str(e)}")
    
    # Should not reach here, but just in case
    raise RuntimeError(
        "All API keys have been exhausted due to rate limits. "
        "Please wait for rate limits to reset or add more API keys to .env file."
    )


def generate_minimal_pair(
    sentence: str,
    phenomenon: str,
    api_keys: List[str],
    key_index: int = 0
) -> Tuple[Dict[str, Any], int]:
    """
    Generate a minimal pair by calling Groq API with phenomenon-specific prompts.
    
    Args:
        sentence: The grammatical Old Norse sentence
        phenomenon: One of 'QUIRKY_CASE', 'ADJECTIVE', 'UMLAUT', 'MIDDLE_VOICE'
        api_keys: List of available API keys
        key_index: Current API key index
        
    Returns:
        Tuple of (minimal_pair_dict, new_key_index) where minimal_pair_dict contains:
            - grammatical: The original grammatical sentence
            - ungrammatical: The ungrammatical variant
            - target: The token that was changed
            - error_type: Description of the grammatical violation
            - skip: Boolean indicating if sentence should be skipped (doesn't contain phenomenon)
        
    Raises:
        RuntimeError: If API call fails or response cannot be parsed
    """
    # Define phenomenon-specific prompts
    prompts = {
        'QUIRKY_CASE': f"""You are an Old Norse linguist. Analyze this sentence:

"{sentence}"

Task: Determine if this sentence contains a quirky case verb (verbs like líka, þykja, þurfa that require dative or accusative subjects instead of nominative).

If YES:
1. Identify the quirky case subject (dative or accusative)
2. Create an UNGRAMMATICAL variant by changing that subject to nominative case
3. Respond in this exact format:
CONTAINS: yes
GRAMMATICAL: [original sentence]
UNGRAMMATICAL: [sentence with nominative subject]
TARGET: [the word that was changed]
ERROR_TYPE: [e.g., "dative_to_nominative" or "accusative_to_nominative"]

If NO (sentence doesn't contain a quirky case verb):
Respond with only:
CONTAINS: no

Example:
Input: "Hánum líkaði þat."
Output:
CONTAINS: yes
GRAMMATICAL: Hánum líkaði þat.
UNGRAMMATICAL: Hann líkaði þat.
TARGET: Hánum
ERROR_TYPE: dative_to_nominative""",

        'ADJECTIVE': f"""You are an Old Norse linguist. Analyze this sentence:

"{sentence}"

Task: Determine if this sentence contains an adjective that must be in strong or weak form based on definiteness.

If YES:
1. Identify the adjective and determine if it should be strong (indefinite context) or weak (definite context)
2. Create an UNGRAMMATICAL variant by using the wrong form
3. Respond in this exact format:
CONTAINS: yes
GRAMMATICAL: [original sentence]
UNGRAMMATICAL: [sentence with wrong adjective form]
TARGET: [the adjective that was changed]
ERROR_TYPE: [e.g., "strong_to_weak" or "weak_to_strong"]

If NO (sentence doesn't contain a clear adjective agreement case):
Respond with only:
CONTAINS: no

Example:
Input: "Hann sá stóran mann."
Output:
CONTAINS: yes
GRAMMATICAL: Hann sá stóran mann.
UNGRAMMATICAL: Hann sá stóri mann.
TARGET: stóran
ERROR_TYPE: strong_to_weak""",

        'UMLAUT': f"""You are an Old Norse linguist. Analyze this sentence:

"{sentence}"

Task: Determine if this sentence contains a word with u-umlaut (vowel shift from 'a' to 'ǫ' in plural or dative contexts, like land → lǫnd).

If YES:
1. Identify the umlauted word
2. Create an UNGRAMMATICAL variant by reverting the ǫ to a
3. Respond in this exact format:
CONTAINS: yes
GRAMMATICAL: [original sentence]
UNGRAMMATICAL: [sentence with ǫ changed to a]
TARGET: [the word that was changed]
ERROR_TYPE: umlaut_removed

If NO (sentence doesn't contain u-umlaut):
Respond with only:
CONTAINS: no

Example:
Input: "Þeir sá lǫnd."
Output:
CONTAINS: yes
GRAMMATICAL: Þeir sá lǫnd.
UNGRAMMATICAL: Þeir sá land.
TARGET: lǫnd
ERROR_TYPE: umlaut_removed""",

        'MIDDLE_VOICE': f"""You are an Old Norse linguist. Analyze this sentence:

"{sentence}"

Task: Determine if this sentence contains a middle-voice verb (verb with -sk suffix indicating reflexive or reciprocal action).

If YES:
1. Identify the middle-voice verb (ends in -sk, -st, or similar)
2. Create an UNGRAMMATICAL variant by removing the middle-voice suffix
3. Respond in this exact format:
CONTAINS: yes
GRAMMATICAL: [original sentence]
UNGRAMMATICAL: [sentence with -sk suffix removed]
TARGET: [the verb that was changed]
ERROR_TYPE: middle_voice_removed

If NO (sentence doesn't contain a middle-voice verb):
Respond with only:
CONTAINS: no

Example:
Input: "Þeir finnask í morgin."
Output:
CONTAINS: yes
GRAMMATICAL: Þeir finnask í morgin.
UNGRAMMATICAL: Þeir finna í morgin.
TARGET: finnask
ERROR_TYPE: middle_voice_removed"""
    }
    
    # Get the appropriate prompt
    if phenomenon not in prompts:
        raise ValueError(f"Unknown phenomenon: {phenomenon}. Must be one of {list(prompts.keys())}")
    
    prompt = prompts[phenomenon]
    
    # Call the API
    response, new_key_index = call_groq_api(
        prompt=prompt,
        api_keys=api_keys,
        current_key_index=key_index,
        model="openai/gpt-oss-120b",
        temperature=0.3,  # Lower temperature for more consistent formatting
        max_tokens=300
    )
    
    # Parse the response
    response = response.strip()
    
    # Check if sentence should be skipped
    if "CONTAINS: no" in response or "CONTAINS:no" in response:
        return {"skip": True}, new_key_index
    
    # Parse the structured response
    try:
        lines = response.split('\n')
        result = {"skip": False}
        
        for line in lines:
            line = line.strip()
            if line.startswith("GRAMMATICAL:"):
                result["grammatical"] = line.replace("GRAMMATICAL:", "").strip()
            elif line.startswith("UNGRAMMATICAL:"):
                result["ungrammatical"] = line.replace("UNGRAMMATICAL:", "").strip()
            elif line.startswith("TARGET:"):
                result["target"] = line.replace("TARGET:", "").strip()
            elif line.startswith("ERROR_TYPE:"):
                result["error_type"] = line.replace("ERROR_TYPE:", "").strip()
        
        # Validate that all required fields are present
        required_fields = ["grammatical", "ungrammatical", "target", "error_type"]
        missing_fields = [f for f in required_fields if f not in result]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in API response: {missing_fields}")
        
        return result, new_key_index
        
    except Exception as e:
        raise RuntimeError(f"Failed to parse API response: {response}\nError: {str(e)}")


def generate_pair_id(phenomenon: str, number: int) -> str:
    """
    Generate pair ID in format "ON_{PHENOMENON}_{NUMBER}" with zero-padded numbers.
    
    Args:
        phenomenon: The phenomenon type (e.g., 'QUIRKY_CASE', 'ADJECTIVE')
        number: The sequence number for this phenomenon
        
    Returns:
        Formatted pair ID (e.g., "ON_QUIRKY_CASE_001")
    """
    # Ensure phenomenon is uppercase
    phenomenon = phenomenon.upper()
    
    # Zero-pad number to 3 digits
    padded_number = str(number).zfill(3)
    
    return f"ON_{phenomenon}_{padded_number}"


def append_to_csv(pair: Dict[str, Any], csv_path: str = "minimal_pairs.csv") -> None:
    """
    Immediately write a minimal pair to CSV file.
    
    Args:
        pair: Dictionary containing pair data with keys:
              id, phenomenon, grammatical, ungrammatical, target, error_type
        csv_path: Path to the CSV file (default: minimal_pairs.csv)
    """
    import csv
    
    # Check if file exists AND has content (not just an empty file)
    file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
    
    # Define CSV columns
    fieldnames = ['id', 'phenomenon', 'grammatical', 'ungrammatical', 'target', 'error_type']
    
    # Open file in append mode
    with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new or empty
        if not file_exists:
            writer.writeheader()
        
        # Write the pair data
        writer.writerow({
            'id': pair['id'],
            'phenomenon': pair['phenomenon'],
            'grammatical': pair['grammatical'],
            'ungrammatical': pair['ungrammatical'],
            'target': pair['target'],
            'error_type': pair['error_type']
        })


def load_existing_pairs(csv_path: str = "minimal_pairs.csv") -> Dict[str, Dict[str, Any]]:
    """
    Read existing pairs from CSV to avoid duplicates.
    
    Args:
        csv_path: Path to the CSV file (default: minimal_pairs.csv)
        
    Returns:
        Dictionary mapping pair IDs to pair data
    """
    import csv
    
    pairs = {}
    
    # If file doesn't exist, return empty dict
    if not os.path.exists(csv_path):
        return pairs
    
    # Read existing pairs
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                pair_id = row['id']
                pairs[pair_id] = {
                    'id': row['id'],
                    'phenomenon': row['phenomenon'],
                    'grammatical': row['grammatical'],
                    'ungrammatical': row['ungrammatical'],
                    'target': row['target'],
                    'error_type': row['error_type']
                }
    except Exception as e:
        print(f"Warning: Error reading CSV file: {e}")
        # Return what we have so far
        return pairs
    
    return pairs


def generate_dataset(
    target_total: int = 500,
    csv_path: str = "minimal_pairs.csv",
    api_keys: List[str] = None
) -> None:
    """
    Orchestrate full generation process to create minimal pairs dataset.
    
    Distributes 500 pairs across 4 phenomena (approximately 125 each).
    Handles interruptions gracefully by resuming from existing CSV.
    Shows progress bar with current count, target count, percentage, and ETA.
    
    Args:
        target_total: Total number of pairs to generate (default: 500)
        csv_path: Path to the CSV file (default: minimal_pairs.csv)
        api_keys: List of API keys (if None, will load from .env)
    """
    from tqdm import tqdm
    
    # Load API keys if not provided
    if api_keys is None:
        api_keys = load_api_keys()
    
    # Define the four phenomena and their target counts
    phenomena = ['QUIRKY_CASE', 'ADJECTIVE', 'UMLAUT', 'MIDDLE_VOICE']
    target_per_phenomenon = target_total // len(phenomena)  # 125 each
    
    # Load existing pairs to resume from interruption
    existing_pairs = load_existing_pairs(csv_path)
    
    # Count existing pairs per phenomenon
    phenomenon_counts = {p: 0 for p in phenomena}
    for pair in existing_pairs.values():
        phenomenon = pair['phenomenon']
        if phenomenon in phenomenon_counts:
            phenomenon_counts[phenomenon] += 1
    
    # Calculate how many more pairs we need
    total_existing = len(existing_pairs)
    total_needed = target_total - total_existing
    
    print(f"Resuming generation: {total_existing}/{target_total} pairs already exist")
    print(f"Phenomenon distribution: {phenomenon_counts}")
    
    # If we already have enough pairs, we're done
    if total_needed <= 0:
        print("Target already reached!")
        return
    
    # Load corpus
    print("Loading Old Norse corpus...")
    corpus_text = load_corpus()
    
    # Extract and filter sentences
    print("Extracting sentences...")
    sentences = extract_sentences(corpus_text)
    sentences = [normalize_text(s) for s in sentences]
    sentences = filter_usable_sentences(sentences)
    
    print(f"Found {len(sentences)} usable sentences")
    
    # Initialize progress bar
    pbar = tqdm(
        total=target_total,
        initial=total_existing,
        desc="Generating pairs",
        unit="pair"
    )
    
    # Track current API key index
    current_key_index = 0
    
    # Keep track of sentence index for each phenomenon
    sentence_indices = {p: 0 for p in phenomena}
    
    try:
        # Generate pairs until we reach the target
        while len(existing_pairs) < target_total:
            # Find which phenomenon needs more pairs
            # Prioritize phenomena that are furthest from their target
            phenomenon_to_generate = None
            max_deficit = 0
            
            for phenomenon in phenomena:
                current_count = phenomenon_counts[phenomenon]
                deficit = target_per_phenomenon - current_count
                
                if deficit > max_deficit:
                    max_deficit = deficit
                    phenomenon_to_generate = phenomenon
            
            # If no phenomenon needs more pairs, we're done
            if phenomenon_to_generate is None or max_deficit <= 0:
                break
            
            # Get next sentence for this phenomenon
            sentence_idx = sentence_indices[phenomenon_to_generate]
            
            # Check if we've run out of sentences
            if sentence_idx >= len(sentences):
                print(f"\nWarning: Ran out of sentences for {phenomenon_to_generate}")
                # Mark this phenomenon as complete by setting its count to target
                phenomenon_counts[phenomenon_to_generate] = target_per_phenomenon
                continue
            
            sentence = sentences[sentence_idx]
            sentence_indices[phenomenon_to_generate] += 1
            
            try:
                # Generate minimal pair
                pair_data, current_key_index = generate_minimal_pair(
                    sentence=sentence,
                    phenomenon=phenomenon_to_generate,
                    api_keys=api_keys,
                    key_index=current_key_index
                )
                
                # Skip if sentence doesn't contain the phenomenon
                if pair_data.get('skip', False):
                    continue
                
                # Generate pair ID
                pair_number = phenomenon_counts[phenomenon_to_generate] + 1
                pair_id = generate_pair_id(phenomenon_to_generate, pair_number)
                
                # Create full pair record
                pair = {
                    'id': pair_id,
                    'phenomenon': phenomenon_to_generate,
                    'grammatical': pair_data['grammatical'],
                    'ungrammatical': pair_data['ungrammatical'],
                    'target': pair_data['target'],
                    'error_type': pair_data['error_type']
                }
                
                # Save to CSV immediately
                append_to_csv(pair, csv_path)
                
                # Update tracking
                existing_pairs[pair_id] = pair
                phenomenon_counts[phenomenon_to_generate] += 1
                
                # Update progress bar
                pbar.update(1)
                
            except Exception as e:
                # Log error but continue with next sentence
                print(f"\nError processing sentence: {e}")
                continue
    
    finally:
        # Close progress bar
        pbar.close()
    
    print(f"\nGeneration complete!")
    print(f"Final distribution: {phenomenon_counts}")
    print(f"Total pairs: {len(existing_pairs)}/{target_total}")
