# Design Document

## Overview

This system generates a diagnostic evaluation dataset for testing LLM grammatical competence in Old Norse through controlled minimal pairs. The architecture consists of three main components: a Dataset Generator that extracts sentences from historical texts and creates minimal pairs using LLM-assisted transformations, an Evaluation System that tests multiple LLMs using forced-choice tasks, and a Visualization & Documentation module that produces comprehensive analysis outputs.

The system treats LLMs as black boxes, focusing on their ability to distinguish grammatical from ungrammatical Old Norse sentences across four key phenomena: quirky case subjects, strong/weak adjective selection, u-umlaut morphology, and middle-voice suffix usage.

## Architecture

The system follows a pipeline architecture with three sequential stages:

1. **Data Acquisition & Pair Generation**: Extracts sentences from the norsecorpus package, then uses the Groq API (gpt-oss-120b model) to generate minimal pairs by introducing controlled grammatical violations
2. **Evaluation**: Tests four LLM models using forced-choice prompts, recording responses incrementally to CSV
3. **Analysis & Visualization**: Computes accuracy metrics, generates plots, and produces comprehensive documentation

Key design decisions:
- CSV format for all data to enable incremental saving and easy inspection
- API key rotation to handle rate limits automatically
- Minimal file structure (single Python script, CSV outputs, plots, documentation)
- Direct use of Groq API for both generation and evaluation to keep dependencies simple

## Components and Interfaces

The system uses simple functions organized into three modules. No classes or dataclasses are needed.

### Generation Functions (generate.py)

- `load_api_keys()`: Reads API keys from .env file
- `load_corpus()`: Loads texts from norsecorpus package
- `extract_sentences(text)`: Segments text using punctuation rules
- `normalize_text(sentence)`: Standardizes special characters
- `call_groq_api(prompt, api_keys, current_key_index)`: Makes API call with key rotation
- `generate_minimal_pair(sentence, phenomenon, api_keys, key_index)`: Creates ungrammatical variant
- `append_to_csv(pair, csv_path)`: Writes pair to CSV immediately
- `load_existing_pairs(csv_path)`: Reads existing pairs to avoid duplicates
- `generate_dataset()`: Main function that orchestrates generation

### Evaluation Functions (evaluate.py)

- `load_pairs(csv_path)`: Reads minimal pairs from CSV
- `format_prompt(grammatical, ungrammatical, order)`: Creates forced-choice prompt
- `evaluate_pair(pair, model, api_keys, key_index)`: Tests one pair with one model
- `evaluate_all_models(pairs_csv, results_csv, api_keys)`: Runs all evaluations
- `compute_accuracy(results_csv)`: Calculates metrics per model and phenomenon
- `save_metrics(metrics, output_csv)`: Writes metrics to CSV

### Visualization Functions (visualize.py)

- `plot_overall_accuracy(metrics_csv)`: Creates bar chart
- `plot_heatmap(metrics_csv)`: Creates model-phenomenon heatmap
- `generate_readme()`: Writes README.md
- `generate_results(metrics_csv, pairs_csv, results_csv)`: Writes RESULTS.md with analysis

## Data Models

Data is stored directly in CSV files with no intermediate data structures needed.

### minimal_pairs.csv

Contains the generated dataset.

Columns: `id,phenomenon,grammatical,ungrammatical,target,error_type`

Example row:
```
ON_QUIRKY_CASE_001,QUIRKY_CASE,"Hánum líkaði þat.","Hann líkaði þat.",Hánum,dative_to_nominative
```

### evaluation_results.csv

Contains individual LLM responses.

Columns: `model,pair_id,order,response,correct`

Example row:
```
gpt-oss-120b,ON_QUIRKY_CASE_001,A_gram,A,True
```

### metrics.csv

Contains aggregated accuracy metrics.

Columns: `model,overall_accuracy,quirky_case_accuracy,adjective_accuracy,umlaut_accuracy,middle_voice_accuracy`

Example row:
```
gpt-oss-120b,0.85,0.82,0.88,0.84,0.86
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After reviewing all testable criteria, I've identified opportunities to consolidate redundant properties:

- Properties 3.3, 4.3, and 5.3 all test "preserve other elements unchanged" - these can be combined into a single "minimal change" property
- Properties 3.4, 4.4, 5.4, 6.4 all test phenomenon counts - these can be combined into a single "balanced distribution" property
- Properties 2.1 and 2.4 both test phenomenon distribution - 2.4 subsumes 2.1
- Properties 7.4 and 7.5 both test incremental saving behavior - can be combined

This consolidation reduces redundancy while maintaining comprehensive coverage.

### Correctness Properties

Property 1: Prose-only extraction
*For any* extracted sentence from the corpus, it should not contain poetry markers, editorial notes, or line numbers
**Validates: Requirements 1.2**

Property 2: Orthography preservation with character standardization
*For any* normalized sentence, all special characters (þ, ð, æ) should be standardized to consistent forms, while all other characters should remain unchanged from the source
**Validates: Requirements 1.3**

Property 3: Punctuation-based segmentation
*For any* text segmentation, sentence boundaries should occur at punctuation marks (. : ;) and not within words
**Validates: Requirements 1.4**

Property 4: Balanced phenomenon distribution
*For any* complete dataset of 500 pairs, each of the four phenomena (quirky case, adjective, umlaut, middle-voice) should have approximately 125 pairs (within ±10%)
**Validates: Requirements 2.1, 2.4, 3.4, 4.4, 5.4, 6.4**

Property 5: Minimal pair single-feature difference
*For any* minimal pair, the grammatical and ungrammatical sentences should differ by exactly one token or one morphological feature within a token
**Validates: Requirements 2.2**

Property 6: Complete pair metadata
*For any* minimal pair record, all required fields (id, phenomenon, grammatical, ungrammatical, target, error_type) should be present and non-empty
**Validates: Requirements 2.5**

Property 7: Minimal change preservation
*For any* minimal pair, all tokens except the target token should be identical between the grammatical and ungrammatical variants
**Validates: Requirements 3.3, 4.3, 5.3**

Property 8: Quirky case transformation
*For any* quirky case minimal pair, the target token should show a case change from dative or accusative to nominative
**Validates: Requirements 3.2**

Property 9: Adjective form transformation
*For any* adjective minimal pair, the target token should show a change between strong and weak adjective forms
**Validates: Requirements 4.2**

Property 10: Umlaut vowel transformation
*For any* umlaut minimal pair, the target token should show a vowel change between 'ǫ' and 'a'
**Validates: Requirements 5.2**

Property 11: Middle-voice suffix identification
*For any* identified middle-voice verb, the verb should contain the -sk suffix
**Validates: Requirements 6.1**

Property 12: Middle-voice suffix removal
*For any* middle-voice minimal pair, the ungrammatical variant should have the -sk suffix removed from the target verb
**Validates: Requirements 6.2**

Property 13: ID format consistency
*For any* minimal pair identifier, it should match the pattern "ON_{PHENOMENON}_{NUMBER}" where phenomenon is uppercase and number is zero-padded to three digits
**Validates: Requirements 7.3**

Property 14: Incremental saving with duplicate prevention
*For any* generation session, newly generated pairs should be immediately appended to the CSV, and resuming should not create duplicate IDs
**Validates: Requirements 7.4, 7.5**

Property 15: Forced-choice prompt format
*For any* evaluation prompt, it should contain the template text "Which of the following Old Norse sentences is grammatically correct?" followed by options "A:" and "B:" and ending with "Answer with A or B only."
**Validates: Requirements 8.2, 8.3**

Property 16: Consistent API settings
*For any* set of API calls during evaluation, the temperature and generation settings should be identical across all models
**Validates: Requirements 8.5**

Property 17: Accuracy calculation correctness
*For any* set of evaluation results, the overall accuracy should equal the count of correct responses divided by the total count of responses
**Validates: Requirements 9.1**

Property 18: Per-phenomenon accuracy calculation
*For any* complete evaluation, each of the four phenomena should have a separate accuracy value calculated from only the pairs of that phenomenon
**Validates: Requirements 9.2**

Property 19: Complete model coverage
*For any* metrics output, all four evaluated models should have accuracy values present
**Validates: Requirements 9.3**

Property 20: Evaluation completeness validation
*For any* final metrics computation, it should only proceed when all 500 pairs have been evaluated
**Validates: Requirements 9.5**

## Error Handling

### API Rate Limiting
- The system maintains a list of API keys loaded from the .env file
- When a rate limit error (HTTP 429) is encountered, the system automatically rotates to the next key
- If all keys are exhausted, the system raises a clear error message and saves progress
- Progress is preserved in CSV files, allowing resumption without data loss

### Malformed API Responses
- If the LLM returns a response that doesn't contain "A" or "B", the system logs the raw response and marks it as invalid
- Invalid responses are recorded in the results CSV with a special marker
- Generation continues with the next pair

### Missing or Corrupted Data
- On initialization, the system validates that the norsecorpus package is installed
- If CSV files are corrupted, the system attempts to read valid rows and reports the error
- The system validates CSV structure (correct columns) before writing

### Network Failures
- API calls include timeout settings (30 seconds)
- Transient network errors trigger retry logic (3 attempts with exponential backoff)
- Persistent failures are logged and the system saves progress before exiting

## Testing Strategy

This system requires both unit tests and property-based tests to ensure correctness.

### Unit Testing Approach

Unit tests will verify specific examples and integration points:

- **Configuration loading**: Test that .env file is correctly parsed and API keys are loaded
- **CSV operations**: Test that CSV files are created with correct headers and data is appended correctly
- **Prompt formatting**: Test that evaluation prompts match the exact template
- **Metric calculation**: Test accuracy calculation with known input/output examples
- **File generation**: Test that README.md and RESULTS.md are created with expected sections

### Property-Based Testing Approach

We will use **Hypothesis** (Python's property-based testing library) to verify universal properties across many inputs.

Each property-based test will:
- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment referencing the design document property
- Use smart generators that constrain inputs to valid Old Norse-like structures

Key property-based tests:

1. **Minimal change property**: Generate random sentence pairs and verify only one token differs
2. **ID format property**: Generate random IDs and verify they match the pattern
3. **Accuracy calculation property**: Generate random evaluation results and verify accuracy formula
4. **Distribution balance property**: Generate random datasets and verify phenomenon counts are balanced
5. **CSV round-trip property**: Generate random minimal pairs, write to CSV, read back, and verify equivalence

### Testing Configuration

- Property-based tests configured for 100 iterations minimum
- Each test tagged with format: `# Feature: old-norse-minimal-pairs, Property {N}: {description}`
- Tests focus on core logic, avoiding mocking where possible
- Integration tests verify end-to-end pipeline with small sample data

