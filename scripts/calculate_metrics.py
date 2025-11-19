#!/usr/bin/env python3
"""
Calculate metrics for collected data with audit logging

Usage:
    python scripts/calculate_metrics.py --experiment exp001_metrics
    make calculate-metrics EXPERIMENT=exp001_metrics
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics import calculate_all_entropies, estimate_mutual_information
from src.utils import AuditLogger, load_json, save_dataframe, list_files, ensure_dir


def process_file(
    file_path: Path,
    logger: AuditLogger,
) -> Dict:
    """Process a single data file and calculate metrics"""
    start_time = time.time()

    # Load data
    data = load_json(str(file_path))

    task_id = data.get('task_id')
    prompt_type = data.get('prompt_type')
    model = data.get('model')
    responses = data.get('responses', [])
    task_description = data.get('task_description', '')
    prompt = data.get('prompt', '')

    logger.log_step(
        step_name=f"Processing task {task_id}",
        step_type='metrics_calculation',
        parameters={
            'file': str(file_path),
            'task_id': task_id,
            'n_responses': len(responses),
        }
    )

    # Calculate entropy metrics
    entropy_metrics = calculate_all_entropies(responses)

    # Calculate MI metrics
    mi_metrics = estimate_mutual_information(prompt, task_description)

    # Combine results
    results = {
        'task_id': task_id,
        'prompt_type': prompt_type,
        'model': model,
        'n_responses': len(responses),
        **{f'entropy_{k}': v for k, v in entropy_metrics.items()},
        **{f'mi_{k}': v for k, v in mi_metrics.items()},
        'source_file': str(file_path),
    }

    duration = time.time() - start_time

    logger.log_metrics_calculation(
        input_file=str(file_path),
        metrics=results,
        metric_type='entropy_and_mi',
        duration=duration,
    )

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Calculate metrics for collected data'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        required=True,
        help='Experiment name for audit logging'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/raw',
        help='Input directory with raw data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Output directory for processed metrics'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='task_*.json',
        help='File pattern to match'
    )

    args = parser.parse_args()

    # Initialize logger
    logger = AuditLogger(experiment_name=args.experiment)

    print(f"\n{'='*60}")
    print(f"Metrics Calculation: {args.experiment}")
    print(f"{'='*60}\n")

    # Find data files
    logger.log_step(
        step_name='Find data files',
        step_type='initialization',
        parameters={
            'input_dir': args.input_dir,
            'pattern': args.pattern,
        }
    )

    data_files = list_files(args.input_dir, pattern=args.pattern)

    print(f"Found {len(data_files)} data files\n")

    if not data_files:
        print("No data files found. Run data collection first.")
        return

    # Ensure output directory
    output_dir = ensure_dir(args.output_dir)

    # Process each file
    all_results = []

    for i, file_path in enumerate(data_files, 1):
        try:
            print(f"[{i}/{len(data_files)}] Processing: {file_path.name}")

            results = process_file(file_path, logger)
            all_results.append(results)

            print(f"  ✓ Entropy: {results.get('entropy_token_entropy', 0):.3f}")
            print(f"  ✓ MI: {results.get('mi_mi_combined', 0):.3f}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            logger.log_error(
                step_name=f"Process {file_path.name}",
                error_message=str(e),
            )
            continue

    # Create DataFrame and save
    if all_results:
        df = pd.DataFrame(all_results)

        output_file = output_dir / 'metrics_summary.csv'
        save_dataframe(df, str(output_file), format='csv')

        logger.log_file_output(
            operation='save',
            file_path=str(output_file),
            file_type='csv',
            metadata={
                'n_records': len(df),
                'columns': list(df.columns),
            }
        )

        print(f"\n✓ Saved metrics to: {output_file}")
        print(f"  Total records: {len(df)}")
        print(f"  Columns: {', '.join(df.columns)}")

        # Print summary statistics
        print(f"\n{'='*60}")
        print("Summary Statistics:")
        print(f"{'='*60}")

        if 'entropy_token_entropy' in df.columns:
            print(f"\nToken Entropy:")
            print(f"  Mean: {df['entropy_token_entropy'].mean():.3f}")
            print(f"  Std:  {df['entropy_token_entropy'].std():.3f}")
            print(f"  Min:  {df['entropy_token_entropy'].min():.3f}")
            print(f"  Max:  {df['entropy_token_entropy'].max():.3f}")

        if 'mi_mi_combined' in df.columns:
            print(f"\nMutual Information:")
            print(f"  Mean: {df['mi_mi_combined'].mean():.3f}")
            print(f"  Std:  {df['mi_mi_combined'].std():.3f}")
            print(f"  Min:  {df['mi_mi_combined'].min():.3f}")
            print(f"  Max:  {df['mi_mi_combined'].max():.3f}")

    # Finalize logging
    print(f"\n{'='*60}")
    summary = logger.finalize()
    print(f"{'='*60}\n")

    print(f"Metrics calculation complete!")
    print(f"Processed: {len(all_results)}/{len(data_files)} files")


if __name__ == '__main__':
    main()
