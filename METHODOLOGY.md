# Data Generation Methodology

This document describes the complete methodology for generating the experimental dataset used in the prompt entropy research, ensuring full reproducibility of results.

## Quick Start

**Complete experimental workflow in one command:**

```bash
# 1. Setup
make setup
make init-env  # Configure API keys in .env

# 2. Run complete experiment (collect data + calculate metrics)
make run-experiment EXPERIMENT=exp001 CONFIG=config/tasks.json

# 3. View results
cat data/processed/metrics_summary.csv
cat logs/exp001_summary.json | jq
```

**All steps are logged with full audit trails** (git state, parameters, file hashes, timestamps).

See `scripts/README.md` for detailed usage.

## Overview

The dataset consists of **1,800 LLM generations** collected across:
- **30 tasks** spanning 6 domains
- **2 prompt types** (specification-driven vs. vague)
- **2 models** (GPT-4, Claude-3.5 Sonnet)
- **30 samples per condition** with temperature=1.0

**All data collection uses Makefile commands with full audit logging for reproducibility.**

## Understanding Temperature in LLM Sampling

### What is Temperature?

**Temperature** is a parameter that controls the randomness of LLM outputs by scaling the probability distribution before sampling.

Think of it across three regimes:

- **Production range (0.3-0.7)**: Reliable, consistent outputs
  - Model picks high-probability tokens
  - Suitable for deterministic tasks (code generation, factual Q&A)
  - Example at 0.3: "The capital of France is Paris" (highly consistent)

- **Baseline (1.0)**: Natural probability distribution
  - Unscaled sampling from model's learned distribution
  - Represents the model's "natural" uncertainty
  - Balances diversity with coherence

- **Latent space exploration (1.2-1.5)**: Diverse, exploratory outputs
  - Model explores lower-probability alternatives
  - Reveals the full range of the model's knowledge
  - Example at 1.5: Model may generate creative variations, alternative phrasings, or explore edge cases

### Why Temperature=1.0 is Our Baseline

We use **temperature=1.0** as the baseline for this research for three important reasons:

**1. Natural Entropy (Theoretical Soundness)**
- At temperature=1.0, we sample directly from the model's learned probability distribution
- This represents the model's "natural" or "unmodified" uncertainty
- It's neither artificially reduced (temp<1.0) nor amplified (temp>1.0)
- This gives us a true measure of the information-theoretic properties we're studying

**2. Maximum Signal Detection (Statistical Power)**
- Higher diversity in outputs makes differences between conditions easier to detect
- With low temperature (e.g., 0.3), all outputs might be too similar
- We might miss the effect of prompt quality on entropy
- At temperature=1.0, we have enough variance to measure meaningful differences

**3. Generalizability Across Sampling Regimes**
- Temperature=1.0 is neither extreme nor conservative
- It balances realism with measurability
- Findings at this temperature are more likely to generalize

### The Trade-off: Production Realism vs. Theoretical Clarity

**Real-world production systems** typically use **temperature=0.3-0.7**:
- Code generation: 0.0-0.3 (highly deterministic)
- Customer service: 0.3-0.5 (consistent, reliable)
- Content generation: 0.5-0.7 (some variety)

**Our research** uses **temperature=1.0** as the baseline because:
- ✓ **Theoretical soundness**: Unscaled probability distribution
- ✓ **Maximum signal**: Enough variance to detect entropy differences
- ✓ **Generalizable**: Neither suppressed (production) nor amplified (exploration)
- ✓ **Information-theoretic validity**: True measure of model's natural entropy

## Theoretical Framework and Hypotheses

### Information-Theoretic Predictions

**Temperature's Effect on Entropy (Known):**

Temperature scales logits before softmax: `p(token) = exp(logit/T) / Σ exp(logit_i/T)`

This guarantees:
- **T < 1.0**: Distribution becomes more peaked → Lower entropy
- **T = 1.0**: Natural distribution → Baseline entropy
- **T > 1.0**: Distribution becomes flatter → Higher entropy

**The Critical Research Question:**

Not *whether* entropy changes with temperature (it will), but:

> **Does the DIFFERENCE in entropy between specification-driven and vague prompts persist across sampling regimes?**

### Formal Hypotheses

**H1: Main Effect of Prompt Type (Primary Hypothesis)**
```
H₁: μ_entropy(vague) > μ_entropy(specification)  for all T ∈ {0.7, 1.0, 1.2}
```
- Specification prompts constrain the output space via mutual information
- This constraint is information-theoretic, not sampling-dependent
- Effect should persist across all temperatures

**H2: Main Effect of Temperature (Guaranteed by Math)**
```
H₂: μ_entropy(T=0.7) < μ_entropy(T=1.0) < μ_entropy(T=1.2)  for each prompt type
```
- This validates our measurement is working correctly
- Not the interesting finding - it's mathematically required

**H3: Interaction Effect (Key Theoretical Question)**

Three possible scenarios:

**Scenario A - Parallel Effects (Predicted):**
```
Δ_entropy(T) = constant across temperatures
Both prompt types increase entropy proportionally
→ Main effect is robust and temperature-independent
```

**Scenario B - Amplification:**
```
Δ_entropy(T) increases with T
Vague prompts benefit more from exploration
→ Specification prompts provide stronger distributional constraints
```

**Scenario C - Convergence:**
```
Δ_entropy(T) decreases with T
At high temps, both explore full latent space
→ Constraints matter less during exploration (limits generalizability)
```

**H4: MI-Entropy Correlation**
```
H₄: r(MI, Entropy) < 0  for all T ∈ {0.7, 1.0, 1.2}
```
- Expected: r strongest at T=1.0 (clean signal)
- May be weaker at T=0.7 (restricted variance)
- May be weaker at T=1.2 (noise from exploration)

### Expected Effect Sizes

Based on information theory:
- **Main effect (H1)**: Cohen's d = 0.6-1.0 (medium to large)
- **Temperature effect (H2)**: η² = 0.7-0.9 (large - guaranteed)
- **Interaction (H3)**: If exists, η² = 0.1-0.3 (small to medium)

### Statistical Power

With N=30 samples per condition:
- Power to detect d=0.8: >95% at α=0.05
- Power to detect interaction: ~80% for η²=0.2

### Multi-Temperature Study Design

We test at **three strategic temperatures**:

**Temperature Selection:**
- **T=0.7** (Production): Real-world deployment, practical relevance
- **T=1.0** (Baseline): Natural, unscaled probability distribution, theoretical purity
- **T=1.2** (Exploration): Latent space exploration, robustness validation

This design tests:
1. **Production validity**: Does the effect hold in real-world settings? (0.7)
2. **Theoretical soundness**: What is the effect at the pure distribution? (1.0)
3. **Robustness**: Does the effect persist during latent exploration? (1.2)

```bash
# Recommended: Full 3-temperature study (3x time/cost)
make run-temperature-study EXPERIMENT=temp_comprehensive
# Tests: temp=0.7, 1.0, 1.2 (production/baseline/exploration)

# Alternative: Quick validation (baseline only)
make run-experiment EXPERIMENT=baseline_only TEMPERATURE=1.0

# Alternative: Baseline + production validation (2x cost)
make run-temperature-baseline EXPERIMENT=production_validation
# Tests: temp=0.7, 1.0

# Small pilot study (3 tasks, 5 samples)
make run-temperature-study-small EXPERIMENT=temp_pilot
```

### Predicted Outcomes

**If H1 holds (main effect across temperatures):**
- Specification prompts reduce entropy by d≈0.8 at all temperatures
- Effect observable at production settings (T=0.7)
- Strong claim: "Effect is robust across sampling regimes"

**If Scenario A (parallel effects):**
```
Entropy difference: Δ ≈ 0.5-0.8 bits (constant)
Claim: "Constraint is temperature-independent"
```

**If Scenario B (amplification):**
```
Δ_0.7 < Δ_1.0 < Δ_1.2
Claim: "Effect amplifies during latent exploration"
```

**If H4 holds (MI-entropy correlation):**
- r ≈ -0.6 to -0.7 at T=1.0
- r ≈ -0.4 to -0.6 at T=0.7, T=1.2
- Claim: "MI predicts entropy reduction"

### Visual Prediction

```
Entropy (bits)
  │
  │     ○──○──○  Vague prompts
  │    ╱
  │   ╱
  │  ╱
  │ ●──●──●  Specification prompts
  │
  └────────────────> Temperature
   0.7  1.0  1.2

Expected: Parallel lines (Scenario A)
          or diverging (Scenario B)
```

**Time & cost impact:**
- Baseline only (1 temp): ~2-3 hours, $30-50
- Production + baseline (2 temps): ~4-6 hours, $60-100
- **Recommended: Full study (3 temps): ~6-9 hours, $90-150**

**Why 3 temperatures is optimal:**
1. ✓ Production validity (0.7)
2. ✓ Theoretical purity (1.0)
3. ✓ Robustness check (1.2)
4. ✓ Can test for interaction effects
5. ✓ Only 3x cost (vs 5x for full range)

## Experimental Design

### Domains and Tasks

#### 1. Technical Programming (5 tasks)
- **Task 1.1**: Write a binary search function
- **Task 1.2**: Implement a linked list data structure
- **Task 1.3**: Create a REST API endpoint
- **Task 1.4**: Write a regular expression parser
- **Task 1.5**: Implement quicksort algorithm

#### 2. Data Analysis (5 tasks)
- **Task 2.1**: Analyze sales data trends
- **Task 2.2**: Clean and preprocess dataset
- **Task 2.3**: Calculate statistical summaries
- **Task 2.4**: Create data visualization
- **Task 2.5**: Perform correlation analysis

#### 3. Business Analysis (5 tasks)
- **Task 3.1**: Write market analysis report
- **Task 3.2**: Create SWOT analysis
- **Task 3.3**: Develop pricing strategy
- **Task 3.4**: Analyze competitor landscape
- **Task 3.5**: Write business requirements

#### 4. Technical Writing (5 tasks)
- **Task 4.1**: Write API documentation
- **Task 4.2**: Create user guide
- **Task 4.3**: Document architecture design
- **Task 4.4**: Write technical specification
- **Task 4.5**: Create troubleshooting guide

#### 5. Creative Writing (5 tasks)
- **Task 5.1**: Write short story opening
- **Task 5.2**: Create product description
- **Task 5.3**: Draft email campaign
- **Task 5.4**: Write blog post introduction
- **Task 5.5**: Create social media content

#### 6. Explanatory Content (5 tasks)
- **Task 6.1**: Explain machine learning concept
- **Task 6.2**: Describe database indexing
- **Task 6.3**: Explain API architecture
- **Task 6.4**: Describe cloud computing
- **Task 6.5**: Explain cryptography basics

## Prompt Engineering

### Specification-Driven Prompts

Specification-driven prompts include:

1. **Explicit constraints**: "Must handle edge cases", "Required to return JSON"
2. **Format specifications**: "Output format: markdown table", "Structure: header, body, footer"
3. **Parameter details**: "Function signature: add(a: int, b: int) -> int"
4. **Examples**: "For instance, input [1,2,3] should return 6"
5. **Technical requirements**: "Use Python 3.10+", "Follow PEP 8 style"
6. **Success criteria**: "Should pass test cases", "Must achieve 95% accuracy"

**Example**:
```
Write a Python function named 'binary_search' that:
- Takes parameters: sorted_list (List[int]), target (int)
- Returns: int (index of target or -1 if not found)
- Must handle: empty lists, single elements, duplicates
- Time complexity: O(log n)
- Include: type hints and docstring
- Format: Follow PEP 8 style guide
```

### Vague Prompts

Vague prompts are intentionally underspecified:

1. **Generic requests**: "Write a function"
2. **Minimal context**: "Analyze the data"
3. **No format guidance**: "Create documentation"
4. **Missing constraints**: "Build an API"
5. **Unclear scope**: "Explain the concept"

**Example**:
```
Write a search function.
```

## Data Collection Protocol

### Environment Setup

```bash
# 1. Complete first-time setup (creates dirs + installs deps + checks env)
make setup

# 2. Configure API keys
make init-env  # Creates .env template
# Edit .env with your API keys:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# 3. Verify environment
make check-env
```

### Makefile-Driven Collection (Recommended)

All data collection is managed through Makefile targets with **full audit logging**:

```bash
# Complete experiment with default settings
make run-experiment EXPERIMENT=exp001

# Or run steps individually:
# 1. Collect data
make collect-data EXPERIMENT=exp001 \
    CONFIG=config/tasks.json \
    MODELS="gpt-4 claude-3.5-sonnet" \
    N_SAMPLES=30

# 2. Calculate metrics
make calculate-metrics EXPERIMENT=exp001
```

**Quick test with small sample:**
```bash
make collect-sample EXPERIMENT=test01
```

**Customization via environment variables:**
```bash
# Custom configuration
export EXPERIMENT=exp002_high_temp
export MODELS="gpt-4"
export PROMPT_TYPES="specification vague"
export N_SAMPLES=50
export TEMPERATURE=1.5
export CONFIG=config/custom_tasks.json

make collect-data
```

### Audit Logging

Every data collection run creates comprehensive audit logs:

**Automatic tracking:**
- Git commit hash and branch
- Uncommitted changes flag
- System information (OS, Python version)
- All parameters and configurations
- SHA256 hashes of all output files
- Execution timestamps and durations
- Success/failure status with errors

**Log files:**
```
logs/
├── exp001.jsonl              # Streaming event log
└── exp001_summary.json       # Experiment summary
```

**View logs:**
```bash
# List recent experiments
make view-logs

# View detailed log
cat logs/exp001.jsonl | jq

# View summary
cat logs/exp001_summary.json | jq

# Filter events
cat logs/exp001.jsonl | jq 'select(.event_type=="data_collection")'
```

### Manual Collection (Alternative)

For custom workflows, use Python scripts directly:

```python
from src.sampling import sample_responses
from src.utils import AuditLogger, save_json

# Initialize audit logger
logger = AuditLogger(experiment_name='exp001')

# Configure
MODELS = ['gpt-4', 'claude-3.5-sonnet']
PROMPT_TYPES = ['specification', 'vague']
N_SAMPLES = 30
TEMPERATURE = 1.0

# Collection loop
for task in tasks:
    for prompt_type in PROMPT_TYPES:
        for model in MODELS:
            # Log step
            logger.log_step(
                step_name=f"Collect task {task['id']}",
                step_type='data_collection',
                parameters={'model': model, 'n': N_SAMPLES}
            )

            # Sample responses
            responses = sample_responses(
                prompt=task['prompts'][prompt_type],
                model=model,
                n=N_SAMPLES,
                temperature=TEMPERATURE,
            )

            # Save and log
            output_file = f"data/raw/task_{task['id']}_{prompt_type}_{model}.json"
            save_json({...}, output_file)

            logger.log_file_output(
                operation='save',
                file_path=output_file,
                file_type='json'
            )

# Finalize
logger.finalize()
```

### Rate Limiting

To respect API rate limits:

- **OpenAI GPT-4**: 0.5-1.0 second delay between requests
- **Anthropic Claude-3**: 0.5-1.0 second delay between requests
- **Between conditions**: 2-5 second delay
- **Error handling**: Exponential backoff for rate limit errors

### Error Handling

```python
import time
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def sample_with_retry(prompt, model, **kwargs):
    """Sample with automatic retry on failures"""
    try:
        return sample_responses(prompt, model, **kwargs)
    except RateLimitError:
        print("Rate limit hit, backing off...")
        raise
    except APIError as e:
        print(f"API error: {e}")
        raise
```

## Metrics Calculation

### 1. Entropy Metrics

```python
from src.metrics import calculate_all_entropies
from src.sampling import get_embeddings

# Calculate token entropy
entropy = calculate_all_entropies(responses)

# Calculate semantic entropy (requires embeddings)
embeddings = get_embeddings(responses)
entropy = calculate_all_entropies(responses, embeddings)
```

**Metrics computed**:
- **Token entropy**: Shannon entropy over token distribution
- **Semantic entropy**: Clustering-based entropy in embedding space
- **Structural entropy**: Entropy over structural features

### 2. Mutual Information

```python
from src.metrics import estimate_mutual_information

mi = estimate_mutual_information(
    prompt=prompt,
    task=task_description,
    prompt_embedding=prompt_emb,
    task_embedding=task_emb,
)
```

**Estimation methods**:
- **MI content**: Information content indicators (numbers, constraints, examples)
- **MI coverage**: Task concept coverage
- **MI semantic**: Embedding similarity
- **MI combined**: Weighted combination

### 3. Quality Assessment

```python
from src.metrics import calculate_overall_quality

quality = calculate_overall_quality(
    response=response,
    task=task_description,
    response_embedding=response_emb,
    task_embedding=task_emb,
    expected_elements=task['expected_elements'],
    required_components=task['required_components'],
    format_requirements=task['format_requirements'],
)
```

**Quality dimensions**:
- **Correctness** (35%): Task-specific correctness
- **Completeness** (25%): Required components present
- **Relevance** (20%): Semantic relevance to task
- **Coherence** (10%): Internal coherence
- **Format compliance** (10%): Format requirements

## Statistical Analysis

### Hypothesis Testing

```python
from src.analysis import paired_t_test, effect_size_interpretation

# Compare specification vs vague
result = paired_t_test(
    spec_entropies,
    vague_entropies,
)

print(f"t({result.degrees_of_freedom})={result.t_statistic:.2f}")
print(f"p={result.p_value:.4f}")
print(f"Cohen's d={result.cohens_d:.2f} ({effect_size_interpretation(result.cohens_d)})")
```

### Correlation Analysis

```python
from src.analysis import pearson_correlation

# MI-Entropy correlation
result = pearson_correlation(mi_values, entropy_values)
print(f"r={result.r:.3f}, p={result.p_value:.4f}")
```

## Data Storage Structure

```
data/
├── raw/                          # Raw LLM generations
│   ├── task_00_specification_gpt-4.json
│   ├── task_00_specification_claude-3-opus.json
│   ├── task_00_vague_gpt-4.json
│   └── ...
├── processed/                    # Processed metrics
│   ├── entropies.csv
│   ├── mutual_information.csv
│   ├── quality_scores.csv
│   └── embeddings.pkl
└── tasks/                        # Task definitions
    └── tasks.json
```

## Reproducibility Checklist

- [ ] Use same model versions (GPT-4-0613, Claude-3-Opus-20240229)
- [ ] Set temperature=1.0 for all generations
- [ ] Collect exactly 30 samples per condition
- [ ] Use same prompt templates
- [ ] Apply same preprocessing steps
- [ ] Use same embedding model (text-embedding-3-small)
- [ ] Follow same metrics calculation procedures
- [ ] Use same statistical tests and parameters
- [ ] Record timestamps and metadata
- [ ] Version control all code

## Random Seed Management

For reproducible analysis:

```python
import numpy as np
import random

# Set seeds
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
```

**Note**: LLM generation is inherently stochastic. Setting temperature=1.0 ensures high diversity, but exact responses cannot be reproduced. Statistical properties should be reproducible across different runs.

## Validation

### Data Quality Checks

1. **Response count**: Verify 30 responses per condition
2. **Empty responses**: Check for and handle empty/error responses
3. **Outliers**: Identify and investigate statistical outliers
4. **Duplicates**: Check for and remove duplicate responses
5. **Format compliance**: Verify responses match expected format

### Metric Validation

1. **Entropy bounds**: Token entropy should be positive
2. **MI bounds**: Mutual information should be non-negative
3. **Quality bounds**: All quality scores should be in [0, 1]
4. **Correlation sanity**: MI-entropy correlation should be negative

## Timeline

Estimated time for full data collection:

- **Setup**: 1 hour
- **Task definition**: 4 hours
- **Prompt engineering**: 8 hours
- **Data collection**: 10-15 hours (with rate limiting)
- **Metrics calculation**: 2-4 hours
- **Quality validation**: 2 hours
- **Statistical analysis**: 2 hours

**Total**: ~30-35 hours

## Ethical Considerations

- Use API keys ethically and within ToS
- Respect rate limits and API guidelines
- Do not use for production systems without review
- Acknowledge LLM providers in publications
- Store API keys securely (never commit to git)
- Review generated content for harmful outputs

## References

- OpenAI API Documentation: https://platform.openai.com/docs
- Anthropic API Documentation: https://docs.anthropic.com
- Shannon, C. E. (1948). A Mathematical Theory of Communication
- Cover, T. M., & Thomas, J. A. (2006). Elements of Information Theory

## Contact

For questions about methodology:
- Email: ibrahim@ibrahimcesar.com
- Repository: https://github.com/ibrahimcesar/prompt-entropy-experiment

## Version History

- v1.0 (2024): Initial methodology document
