# Implementation Plan

- [x] 1. Set up project structure and dependencies









  - Create .env file with API keys (GROQ_API_KEY_1, GROQ_API_KEY_2, etc.)
  - Create .gitignore with .env entry
  - Install required packages: norsecorpus, python-dotenv, groq, pandas, matplotlib, seaborn, tqdm
  - _Requirements: 10.1, 10.2, 10.3, 10.6_

- [x] 2. Implement data acquisition and text processing





  - Write `load_corpus()` to load texts from norsecorpus package
  - Write `extract_sentences()` to segment text using punctuation rules (. : ;)
  - Write `normalize_text()` to standardize special characters (þ, ð, æ) while preserving orthography
  - Write `filter_usable_sentences()` to select sentences that are grammatically complete, contain relevant phenomena, and are of appropriate length (5-20 words)
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.1 Write property test for text normalization



  - **Property 2: Orthography preservation with character standardization**
  - **Validates: Requirements 1.3**

- [x] 2.2 Write property test for sentence segmentation


  - **Property 3: Punctuation-based segmentation**
  - **Validates: Requirements 1.4**

- [x] 3. Implement API key management and rotation




  - Write `load_api_keys()` to read multiple keys from .env file
  - Write `call_groq_api()` with automatic key rotation on rate limit errors (HTTP 429)
  - Handle exhausted keys with clear error message
  - _Requirements: 10.1, 10.4, 10.5_

- [x] 4. Implement minimal pair generation






  - Write `generate_minimal_pair()` to call Groq API (gpt-oss-120b) with phenomenon-specific prompts
  - Create prompts for each phenomenon that instruct the LLM to: identify if the sentence contains the target phenomenon, and if so, create the ungrammatical variant
  - Prompts should specify: quirky case verbs (líka, þykja), strong/weak adjective contexts, u-umlaut forms (land/lǫnd), middle-voice verbs (-sk suffix)
  - Parse API response to extract grammatical, ungrammatical, target, and error_type
  - Skip sentences that don't contain the target phenomenon
  - _Requirements: 2.1, 2.2, 2.3, 3.2, 4.2, 5.2, 6.2_

- [x] 4.1 Write property test for minimal change


  - **Property 5: Minimal pair single-feature difference**
  - **Validates: Requirements 2.2**

- [x] 4.2 Write property test for minimal change preservation


  - **Property 7: Minimal change preservation**
  - **Validates: Requirements 3.3, 4.3, 5.3**

- [x] 5. Implement CSV operations for dataset generation




  - Write `append_to_csv()` to immediately write pairs to minimal_pairs.csv
  - Write `load_existing_pairs()` to read existing pairs and avoid duplicates
  - Generate pair IDs in format "ON_{PHENOMENON}_{NUMBER}" with zero-padded numbers
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.1 Write property test for ID format


  - **Property 13: ID format consistency**
  - **Validates: Requirements 7.3**

- [x] 5.2 Write property test for incremental saving



  - **Property 14: Incremental saving with duplicate prevention**
  - **Validates: Requirements 7.4, 7.5**

- [x] 6. Implement main generation orchestration





  - Write `generate_dataset()` to orchestrate full generation process
  - Distribute 500 pairs across 4 phenomena (approximately 125 each)
  - Handle interruptions gracefully by resuming from existing CSV
  - Add progress bar using tqdm to show generation progress (current count, target count, percentage, ETA)
  - _Requirements: 1.5, 2.4, 2.5_

- [x] 6.1 Write property test for balanced distribution



  - **Property 4: Balanced phenomenon distribution**
  - **Validates: Requirements 2.1, 2.4, 3.4, 4.4, 5.4, 6.4**

- [x] 6.2 Write property test for complete metadata


  - **Property 6: Complete pair metadata**
  - **Validates: Requirements 2.5**

- [x] 7. Checkpoint - Ensure generation works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement evaluation prompt formatting
  - Write `format_prompt()` to create forced-choice prompts with template: "Which of the following Old Norse sentences is grammatically correct? A: {sentence1} B: {sentence2} Answer with A or B only."
  - Randomize order (A_gram or B_gram) for each pair
  - _Requirements: 8.2, 8.3_

- [ ] 8.1 Write property test for prompt format
  - **Property 15: Forced-choice prompt format**
  - **Validates: Requirements 8.2, 8.3**

- [ ] 9. Implement model evaluation
  - Write `evaluate_pair()` to test one pair with one model using Groq API
  - Write `evaluate_all_models()` to test all 4 models: openai/gpt-oss-120b, openai/gpt-oss-20b, meta-llama/llama-4-scout-17b-16e-instruct, meta-llama/llama-3.3-70b-versatile
  - Parse responses to extract A/B choice
  - Append results immediately to evaluation_results.csv
  - Use consistent temperature and settings across all models
  - _Requirements: 8.1, 8.4, 8.5, 8.6_

- [ ] 9.1 Write property test for consistent API settings
  - **Property 16: Consistent API settings**
  - **Validates: Requirements 8.5**

- [ ] 10. Implement metrics calculation
  - Write `compute_accuracy()` to calculate overall accuracy (correct / total)
  - Calculate per-phenomenon accuracy for each of the 4 phenomena
  - Validate that all 500 pairs have been evaluated before computing final metrics
  - Write metrics to metrics.csv
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10.1 Write property test for accuracy calculation
  - **Property 17: Accuracy calculation correctness**
  - **Validates: Requirements 9.1**

- [ ] 10.2 Write property test for per-phenomenon accuracy
  - **Property 18: Per-phenomenon accuracy calculation**
  - **Validates: Requirements 9.2**

- [ ] 10.3 Write property test for complete model coverage
  - **Property 19: Complete model coverage**
  - **Validates: Requirements 9.3**

- [ ] 10.4 Write property test for evaluation completeness
  - **Property 20: Evaluation completeness validation**
  - **Validates: Requirements 9.5**

- [ ] 11. Checkpoint - Ensure evaluation works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement visualizations
  - Write `plot_overall_accuracy()` to create bar chart comparing all 4 models
  - Write `plot_heatmap()` to create model-phenomenon accuracy heatmap
  - Save plots as PNG files with descriptive names
  - Use consistent color schemes and clear labels
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 13. Implement comprehensive documentation generation
  - Write `generate_readme()` to create detailed README.md with sections:
    - Introduction: research motivation and goals
    - Background: Old Norse grammar phenomena explained
    - Installation: step-by-step setup instructions
    - Data acquisition: corpus sources and processing pipeline
    - Pair generation: methodology and quality controls
    - Evaluation: forced-choice task design and model selection
    - Visualization: plot descriptions and interpretations
    - File structure: detailed explanation of all outputs
    - Reproducibility: instructions for replicating results
  - Write `generate_results()` to create comprehensive RESULTS.md with:
    - Executive summary of findings
    - Detailed accuracy tables (overall and per-phenomenon)
    - Per-model analysis with strengths and weaknesses
    - Per-phenomenon analysis with difficulty rankings
    - Embedded plots with detailed captions
    - Qualitative error analysis with 10+ concrete examples per phenomenon
    - Statistical significance testing (chi-square tests for model comparisons)
    - Discussion of implications for LLM grammatical competence
  - Write `generate_analysis()` to create ANALYSIS.md for research paper with:
    - Detailed error analysis: categorize errors by type (case confusion, morphological errors, etc.)
    - How: methodology for error classification and pattern identification
    - Why: linguistic explanations for each error pattern (e.g., English bias, tokenization issues)
    - What it implies: theoretical implications for LLM architecture and training
    - Comparison with human language acquisition patterns
    - Limitations of current LLM approaches to morphology
    - Recommendations for improving LLM performance on low-resource languages
    - Future research directions
  - Reference all CSV files with column-by-column explanations
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 14. Add research paper quality analysis
  - Add confusion matrix analysis for systematic error patterns across phenomena
  - Generate LaTeX-formatted tables for paper inclusion (accuracy table, phenomenon comparison)
  - Create supplementary materials document with:
    - Full dataset statistics (sentence length distribution, phenomenon distribution)
    - Example minimal pairs for each phenomenon (20 examples each)
    - Complete model responses for error analysis
    - Methodology details for reproducibility
  - Generate PAPER_SECTIONS.md with draft sections ready for paper:
    - Abstract draft
    - Introduction section
    - Related work section outline
    - Methodology section (complete)
    - Results section (complete with tables)
    - Discussion section with key findings
    - Conclusion and future work
  - _Requirements: 12.4_

- [ ] 15. Final checkpoint - Complete system test
  - Ensure all tests pass, ask the user if questions arise.
