# Old Norse Grammaticality Judgment Evaluation

A statistically rigorous benchmark for evaluating Large Language Models (LLMs) on Old Norse grammatical competence using minimal pairs with comprehensive error analysis.

## Introduction

This project evaluates how well modern LLMs understand Old Norse grammar through a forced-choice grammaticality judgment task. We test 4 models on 500 minimal pairs covering 4 grammatical phenomena unique to Old Norse, with **complete statistical validation** of all findings.

**Research Questions:**
- Can LLMs distinguish grammatical from ungrammatical Old Norse sentences?
- Which grammatical phenomena are most challenging for LLMs?
- How do different model architectures compare on morphologically rich languages?

## Key Findings (Statistically Validated)

- **llama-3.3-70b-versatile** achieves the highest accuracy (**78.6%**).
- **MIDDLE_VOICE** is definitively the hardest phenomenon (54.4% avg, p<0.001).
- **OpenAI models catastrophically fail** on middle voice (42.4% avg vs 66.4% for Llama, p<0.001).
- **77-83% of middle voice errors** involve systematic `-sk`/`-st` suffix removal.
- **Architecture matters more than size**: 70B Llama > 120B OpenAI.

## Grammatical Phenomena Tested

### 1. Quirky Case (`QUIRKY_CASE`)
Old Norse has verbs that require dative or genitive subjects instead of nominative.
- **Grammatical:** *Honum líkar maturinn* (Him.DAT likes the-food)
- **Ungrammatical:** *Hann líkar maturinn* (He.NOM likes the-food)

### 2. U-Umlaut (`UMLAUT`)
Vowel mutation where /a/ becomes /ǫ/ before /u/ in the following syllable.
- **Grammatical:** *lǫnd* (lands, plural)
- **Ungrammatical:** *land* (when plural is required)

### 3. Middle Voice (`MIDDLE_VOICE`)
Reflexive/middle voice marked by `-sk`/`-st` suffix on verbs.
- **Grammatical:** *Hann kallask Óláfr* (He calls-himself Olaf)
- **Ungrammatical:** *Hann kallar Óláfr* (missing reflexive)

### 4. Adjective Declension (`ADJECTIVE`)
Strong vs weak adjective forms depending on definiteness.
- **Grammatical:** *inn gamli maðr* (the old.WEAK man)
- **Ungrammatical:** *inn gamall maðr* (the old.STRONG man)

## Workspace Structure

The project has been cleaned of redundant experimental scripts, leaving the core pipeline:

```text
├── create_minimal_pairs.py        # Dataset generation logic
├── evaluate_models.py             # Model evaluation script
├── comprehensive_error_analysis.py # Statistical validation script
├── generate_analysis_plots.py     # Data visualization
├── minimal_pairs.csv              # The 500-pair benchmark dataset
├── evaluation_results_*.csv       # Raw evaluation data per model
├── ANALYSIS.md                    # Detailed statistical error analysis
├── RESULTS.md                     # Executive summary of findings
└── requirements.txt               # Python dependencies
```

## Usage

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run Analysis
To reproduce the statistical validation findings:
```bash
python comprehensive_error_analysis.py
```

### 3. Generate Visualizations
To recreate the analysis plots:
```bash
python generate_analysis_plots.py
```

## Models Evaluated

| Model | Parameters | Provider |
|-------|------------|----------|
| llama-3.3-70b-versatile | 70B | Groq |
| openai/gpt-oss-120b | 120B | Groq |
| llama-3.1-8b-instant | 8B | Groq |
| openai/gpt-oss-20b | 20B | Groq |

## Results Summary

| Model | Overall Accuracy | Best Phenomenon | Worst Phenomenon |
|-------|------------------|-----------------|------------------|
| llama-3.3-70b | **78.6%** | MIDDLE_VOICE (85.6%) | UMLAUT (68.0%) |
| openai-120b | 74.6% | ADJECTIVE (84.8%) | MIDDLE_VOICE (48.0%) |
| llama-3.1-8b | 61.2% | ADJECTIVE (68.8%) | MIDDLE_VOICE (47.2%) |
| openai-20b | 57.8% | ADJECTIVE (80.0%) | MIDDLE_VOICE (36.8%) |

## Visual Evidence

| Metric | Visualization |
|--------|---------------|
| **Overall Accuracy** | ![Accuracy](plot_overall_accuracy.png) |
| **Middle Voice Failure** | ![Middle Voice](analysis_middle_voice_failure.png) |
| **Architecture vs Size** | ![Arch vs Size](analysis_architecture_vs_size.png) |

---
*See [RESULTS.md](RESULTS.md) for detailed performance breakdowns and [ANALYSIS.md](ANALYSIS.md) for linguistic depth.*
