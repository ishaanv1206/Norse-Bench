# Requirements Document

## Introduction

This document specifies requirements for a diagnostic evaluation dataset for testing Large Language Model (LLM) grammatical competence in Old Norse. The system generates controlled minimal pairs from historical texts to evaluate whether LLMs can distinguish grammatical from ungrammatical Old Norse sentences. The LLM is treated as a black box, and evaluation focuses on grammatical preference through forced-choice tasks.

## Glossary

- **Minimal Pair**: Two sentences differing in exactly one grammatical feature, where one is grammatical and one is ungrammatical
- **Dataset Generator**: The system that creates minimal pairs from source texts
- **Evaluation System**: The component that tests LLMs using the generated dataset
- **Target Token**: The specific word in a sentence that is modified to create the ungrammatical variant
- **Phenomenon**: A specific grammatical feature being tested (e.g., case assignment, agreement)
- **Forced Choice Task**: An evaluation format where the LLM must select between two options (A or B)
- **Groq API**: The API service used to generate minimal pairs using the gpt-oss-120b model
- **Norse Corpus**: The Python package providing access to Old Norse texts in TEI XML format

## Requirements

### Requirement 1

**User Story:** As a computational linguist, I want to acquire grammatical Old Norse sentences from historical texts, so that I can build a dataset based on authentic language usage.

#### Acceptance Criteria

1. WHEN the Dataset Generator initializes THEN the system SHALL load texts from the norsecorpus package
2. WHEN processing source texts THEN the Dataset Generator SHALL extract prose sentences while excluding poetry, editorial notes, and line numbers
3. WHEN normalizing text THEN the Dataset Generator SHALL preserve historical orthography while standardizing special characters (þ, ð, æ)
4. WHEN segmenting text THEN the Dataset Generator SHALL split sentences using rule-based punctuation detection (. : ;)
5. THE Dataset Generator SHALL acquire a minimum of 500 grammatical sentences from the corpus

### Requirement 2

**User Story:** As a researcher, I want to generate minimal pairs for specific Old Norse grammatical phenomena, so that I can systematically test LLM understanding of these features.

#### Acceptance Criteria

1. WHEN generating minimal pairs THEN the Dataset Generator SHALL create pairs for exactly four phenomena: quirky case subjects, strong versus weak adjective selection, u-umlaut morphology, and middle-voice suffix usage
2. WHEN creating an ungrammatical variant THEN the Dataset Generator SHALL modify exactly one grammatical feature from the source sentence
3. WHEN generating pairs THEN the Dataset Generator SHALL use the Groq API with the gpt-oss-120b model to create transformations
4. WHEN distributing pairs across phenomena THEN the Dataset Generator SHALL create approximately 125 pairs per phenomenon to reach 500 total pairs
5. WHEN storing a minimal pair THEN the Dataset Generator SHALL record the pair identifier, phenomenon type, grammatical sentence, ungrammatical sentence, target token, and error type

### Requirement 3

**User Story:** As a researcher, I want minimal pairs that test quirky case subject violations, so that I can evaluate whether LLMs understand non-nominative subjects.

#### Acceptance Criteria

1. WHEN identifying quirky case verbs THEN the Dataset Generator SHALL recognize verbs requiring dative or accusative subjects
2. WHEN creating a quirky case violation THEN the Dataset Generator SHALL change a dative or accusative subject to nominative case
3. WHEN generating quirky case pairs THEN the Dataset Generator SHALL preserve all other sentence elements unchanged
4. THE Dataset Generator SHALL create approximately 125 minimal pairs testing quirky case subjects

### Requirement 4

**User Story:** As a researcher, I want minimal pairs that test strong versus weak adjective selection, so that I can evaluate whether LLMs understand definiteness marking.

#### Acceptance Criteria

1. WHEN identifying adjective contexts THEN the Dataset Generator SHALL determine whether the noun phrase is definite or indefinite
2. WHEN creating an adjective agreement violation THEN the Dataset Generator SHALL substitute a weak adjective form where a strong form is required or vice versa
3. WHEN generating adjective pairs THEN the Dataset Generator SHALL maintain the noun and article unchanged
4. THE Dataset Generator SHALL create approximately 125 minimal pairs testing adjective selection

### Requirement 5

**User Story:** As a researcher, I want minimal pairs that test u-umlaut morphology, so that I can evaluate whether LLMs recognize internal word structure.

#### Acceptance Criteria

1. WHEN identifying umlauted forms THEN the Dataset Generator SHALL recognize vowel shifts from 'a' to 'ǫ' in plural or dative contexts
2. WHEN creating an umlaut violation THEN the Dataset Generator SHALL revert an umlauted vowel to its base form
3. WHEN generating umlaut pairs THEN the Dataset Generator SHALL preserve case and number markings
4. THE Dataset Generator SHALL create approximately 125 minimal pairs testing u-umlaut morphology

### Requirement 6

**User Story:** As a researcher, I want minimal pairs that test middle-voice suffix usage, so that I can evaluate whether LLMs understand reflexive and reciprocal semantics.

#### Acceptance Criteria

1. WHEN identifying middle-voice verbs THEN the Dataset Generator SHALL recognize verbs with the -sk suffix indicating reflexive or reciprocal action
2. WHEN creating a middle-voice violation THEN the Dataset Generator SHALL remove the -sk suffix to create an active voice form
3. WHEN generating middle-voice pairs THEN the Dataset Generator SHALL ensure the context requires reciprocal or reflexive meaning
4. THE Dataset Generator SHALL create approximately 125 minimal pairs testing middle-voice suffix usage

### Requirement 7

**User Story:** As a researcher, I want to store the dataset in CSV format with incremental updates, so that progress is preserved if generation is interrupted.

#### Acceptance Criteria

1. WHEN serializing a minimal pair THEN the Dataset Generator SHALL encode it as a CSV row with columns for id, phenomenon, grammatical, ungrammatical, target, and error_type
2. WHEN writing the dataset THEN the Dataset Generator SHALL create a single CSV file with headers
3. WHEN generating pair identifiers THEN the Dataset Generator SHALL use the format "ON_{PHENOMENON}_{NUMBER}" where phenomenon is uppercase and number is zero-padded to three digits
4. WHEN a new minimal pair is generated THEN the Dataset Generator SHALL immediately append it to the CSV file to preserve progress
5. WHEN resuming generation THEN the Dataset Generator SHALL read existing pairs from the CSV to avoid duplicates

### Requirement 8

**User Story:** As a researcher, I want to evaluate multiple LLMs using forced-choice tasks, so that I can compare their grammatical competence in Old Norse.

#### Acceptance Criteria

1. WHEN evaluating an LLM THEN the Evaluation System SHALL test exactly four models: openai/gpt-oss-120b, openai/gpt-oss-20b, meta-llama/llama-4-scout-17b-16e-instruct, and meta-llama/llama-3.3-70b-versatile
2. WHEN presenting a minimal pair THEN the Evaluation System SHALL format it as a forced choice with options A and B
3. WHEN prompting the LLM THEN the Evaluation System SHALL use the template "Which of the following Old Norse sentences is grammatically correct? A: {sentence1} B: {sentence2} Answer with A or B only."
4. WHEN recording responses THEN the Evaluation System SHALL append results to a CSV file with columns for model, pair_id, order, response, and correct
5. WHEN calling the Groq API THEN the Evaluation System SHALL use consistent temperature and generation settings across all models
6. WHEN a rate limit error occurs during evaluation THEN the Evaluation System SHALL switch to the next available API key

### Requirement 9

**User Story:** As a researcher, I want to calculate accuracy metrics per model and per phenomenon, so that I can identify systematic patterns in LLM performance.

#### Acceptance Criteria

1. WHEN computing overall accuracy THEN the Evaluation System SHALL calculate the percentage of correct grammatical choices across all pairs
2. WHEN computing phenomenon-specific accuracy THEN the Evaluation System SHALL calculate accuracy separately for each of the four phenomena
3. WHEN generating results THEN the Evaluation System SHALL output accuracy for each model tested
4. WHEN storing evaluation results THEN the Evaluation System SHALL write metrics to a CSV file with columns for model, overall_accuracy, quirky_case_accuracy, adjective_accuracy, umlaut_accuracy, and middle_voice_accuracy
5. THE Evaluation System SHALL validate that all 500 pairs have been evaluated before computing final metrics

### Requirement 11

**User Story:** As a researcher, I want comprehensive visualizations of evaluation results, so that I can quickly understand model performance patterns across phenomena.

#### Acceptance Criteria

1. WHEN generating visualizations THEN the Evaluation System SHALL create a bar chart comparing overall accuracy across all four models
2. WHEN visualizing phenomenon performance THEN the Evaluation System SHALL create a heatmap showing model-phenomenon accuracy combinations
3. THE Evaluation System SHALL save all plots as PNG files with descriptive filenames
4. THE Evaluation System SHALL use consistent color schemes and clear labels across all visualizations

### Requirement 12

**User Story:** As a researcher, I want detailed documentation of the research methodology and results, so that the work is reproducible and findings are clearly communicated.

#### Acceptance Criteria

1. WHEN documenting the project THEN the system SHALL create a README.md file explaining the research purpose, methodology, and usage instructions
2. WHEN documenting results THEN the system SHALL create a RESULTS.md file containing detailed findings with accuracy tables, phenomenon analysis, and error patterns
3. WHEN describing methodology THEN the README SHALL include sections for installation, data acquisition, pair generation, evaluation process, and visualization
4. WHEN presenting results THEN the RESULTS.md SHALL include embedded plots, per-model analysis, per-phenomenon analysis, and qualitative error examples
5. THE documentation SHALL reference all generated CSV files and explain their structure

### Requirement 10

**User Story:** As a researcher, I want to manage API credentials with automatic failover, so that generation continues when rate limits are encountered.

#### Acceptance Criteria

1. WHEN initializing the system THEN the Dataset Generator SHALL read multiple Groq API keys from a .env file, one per line
2. WHEN the .env file is missing THEN the Dataset Generator SHALL raise an error with a clear message indicating the required configuration
3. THE Dataset Generator SHALL store API keys with variable names GROQ_API_KEY_1, GROQ_API_KEY_2, etc.
4. WHEN a rate limit error occurs THEN the Dataset Generator SHALL automatically switch to the next available API key
5. WHEN all API keys are exhausted THEN the Dataset Generator SHALL raise an error indicating no available keys remain
6. THE system SHALL include .env in .gitignore to prevent credential exposure
