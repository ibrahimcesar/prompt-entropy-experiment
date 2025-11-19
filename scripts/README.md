# Experimental Scripts with Audit Logging

These scripts provide a fully audited workflow for reproducible experiments.

## Overview

All scripts include comprehensive audit logging that tracks:
- System information and git state
- All parameters and configurations
- Input/output files with SHA256 hashes
- Execution duration for each step
- Success/failure status with error details

## Scripts

### 1. `collect_data.py`

Collect LLM responses for experimental tasks with full audit trail.

**Via Makefile (recommended):**
```bash
# Full experiment
make collect-data EXPERIMENT=exp001

# Custom configuration
make collect-data EXPERIMENT=exp002 CONFIG=config/my_tasks.json

# Specific models
make collect-data MODELS="gpt-4" PROMPT_TYPES="specification"

# Quick sample for testing
make collect-sample EXPERIMENT=test01
```

**Direct usage:**
```bash
python scripts/collect_data.py \
  --experiment exp001 \
  --config config/tasks.json \
  --models gpt-4 claude-3-opus \
  --prompt-types specification vague \
  --n-samples 30 \
  --temperature 1.0
```

**Options:**
- `--experiment`: Experiment name for audit logging (required)
- `--config`: Path to task configuration file
- `--models`: Space-separated list of models
- `--prompt-types`: Space-separated list of prompt types
- `--n-samples`: Number of samples per condition (default: 30)
- `--temperature`: Sampling temperature (default: 1.0)
- `--task-ids`: Specific task IDs to collect (optional)

**Output:**
- Raw data: `data/raw/task_XXX_TYPE_MODEL.json`
- Audit log: `logs/EXPERIMENT.jsonl`
- Summary: `logs/EXPERIMENT_summary.json`

### 2. `calculate_metrics.py`

Calculate entropy and mutual information metrics for collected data.

**Via Makefile (recommended):**
```bash
# Calculate metrics for all data
make calculate-metrics EXPERIMENT=exp001

# Custom directories
make calculate-metrics \
  EXPERIMENT=exp002_metrics \
  INPUT_DIR=data/raw \
  OUTPUT_DIR=data/processed
```

**Direct usage:**
```bash
python scripts/calculate_metrics.py \
  --experiment exp001_metrics \
  --input-dir data/raw \
  --output-dir data/processed
```

**Options:**
- `--experiment`: Experiment name for audit logging (required)
- `--input-dir`: Input directory with raw data
- `--output-dir`: Output directory for processed metrics
- `--pattern`: File pattern to match (default: `task_*.json`)

**Output:**
- Metrics: `data/processed/metrics_summary.csv`
- Audit log: `logs/EXPERIMENT_metrics.jsonl`
- Summary: `logs/EXPERIMENT_metrics_summary.json`

## Complete Workflow

Run entire experiment (collect + metrics) in one command:

```bash
make run-experiment EXPERIMENT=exp001 CONFIG=config/tasks.json
```

This will:
1. Collect data for all tasks, models, and prompt types
2. Calculate all metrics
3. Generate comprehensive audit logs
4. Show summary of results

## Audit Logs

### Viewing Logs

```bash
# List recent logs
make view-logs

# View specific log
cat logs/exp001.jsonl | jq

# View summary
cat logs/exp001_summary.json | jq

# Filter by event type
cat logs/exp001.jsonl | jq 'select(.event_type=="data_collection")'

# Get error events only
cat logs/exp001.jsonl | jq 'select(.event_type=="error")'
```

### Log Format

Each log entry is a JSON object with:

```json
{
  "timestamp": "2024-11-19T10:30:45.123456",
  "event_type": "data_collection",
  "task_id": 5,
  "prompt_type": "specification",
  "model": "gpt-4",
  "n_samples": 30,
  "temperature": 1.0,
  "output_file": "data/raw/task_005_specification_gpt_4.json",
  "output_hash": "a1b2c3...",
  "duration_seconds": 45.3,
  "success": true
}
```

### Event Types

- `session_start`: Experiment initialization
- `step`: General experimental step
- `data_collection`: LLM response collection
- `metrics_calculation`: Entropy/MI calculation
- `statistical_analysis`: Statistical tests
- `file_output`: File write operations
- `error`: Error events with traceback

## Makefile Variables

Configure experiments via environment variables or command-line:

```bash
# Via environment
export EXPERIMENT=exp001
export N_SAMPLES=50
export TEMPERATURE=0.8
make collect-data

# Via command-line
make collect-data EXPERIMENT=exp001 N_SAMPLES=50 TEMPERATURE=0.8
```

**Available variables:**
- `EXPERIMENT`: Experiment ID (auto-generated timestamp if not set)
- `CONFIG`: Task configuration file (default: config/tasks.example.json)
- `MODELS`: Space-separated model list (default: gpt-4 claude-3-opus)
- `PROMPT_TYPES`: Space-separated prompt types (default: specification vague)
- `N_SAMPLES`: Samples per condition (default: 30)
- `TEMPERATURE`: Sampling temperature (default: 1.0)

## Configuration File Format

Tasks are defined in JSON format:

```json
{
  "tasks": [
    {
      "id": 0,
      "domain": "technical_programming",
      "description": "Write a binary search function",
      "prompts": {
        "specification": "Detailed specification...",
        "vague": "Simple request..."
      },
      "expected_elements": ["def", "binary_search"],
      "required_components": ["function"],
      "format_requirements": {
        "has_code": true,
        "min_length": 50
      }
    }
  ]
}
```

See `config/tasks.example.json` for complete example.

## Reproducibility

Every run creates a complete audit trail including:
- Git commit hash and branch
- Uncommitted changes flag
- System information (platform, Python version)
- All parameters and configurations
- SHA256 hashes of all input/output files
- Execution timestamps and durations

This ensures experiments can be:
1. **Verified**: Check file hashes match
2. **Reproduced**: Re-run with same parameters
3. **Debugged**: Trace errors with full context
4. **Published**: Include audit logs with results

## Examples

### Example 1: Quick Test

```bash
# Collect small sample for testing
make collect-sample EXPERIMENT=test01

# Verify results
ls -lh data/raw/
cat logs/test01_summary.json | jq
```

### Example 2: Single Model

```bash
# Collect data for GPT-4 only
make collect-data \
  EXPERIMENT=gpt4_only \
  MODELS="gpt-4" \
  N_SAMPLES=50
```

### Example 3: Specification Prompts Only

```bash
# Collect specification prompts only
make collect-data \
  EXPERIMENT=spec_only \
  PROMPT_TYPES="specification" \
  MODELS="gpt-4 claude-3-opus"
```

### Example 4: Complete Pipeline

```bash
# 1. Collect data
make collect-data EXPERIMENT=exp001 N_SAMPLES=30

# 2. Calculate metrics
make calculate-metrics EXPERIMENT=exp001

# 3. Review results
cat data/processed/metrics_summary.csv | head
cat logs/exp001_summary.json | jq '.event_counts'
```

## Troubleshooting

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### API Rate Limits

Adjust delay in scripts:
```python
delay_between_requests=1.0  # Increase to 1-2 seconds
```

### Viewing Logs Without jq

```bash
# Pretty print with Python
python -m json.tool logs/exp001_summary.json
```

### Permission Errors

```bash
chmod +x scripts/*.py
```

## Best Practices

1. **Use descriptive experiment names**: `exp001_baseline`, `exp002_high_temp`
2. **Review audit logs**: Always check summary after collection
3. **Verify file hashes**: Ensure data integrity
4. **Keep git clean**: Commit before major experiments
5. **Document runs**: Note experiment goals in lab notebook

## Integration with Analysis

After collecting data and metrics:

```bash
# 1. Run Jupyter notebook for analysis
make notebook

# 2. Open notebooks/01_entropy_analysis.ipynb

# 3. Load processed metrics
df = pd.read_csv('data/processed/metrics_summary.csv')

# 4. Reference audit logs in notebook
with open('logs/exp001_summary.json') as f:
    experiment_meta = json.load(f)
```
