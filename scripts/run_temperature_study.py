#!/usr/bin/env python3
"""
Multi-temperature experimental study

This script runs the complete experiment across multiple temperature values
to validate that the MI-entropy relationship is robust across sampling regimes.

Usage:
    python scripts/run_temperature_study.py --experiment temp_study
    make run-temperature-study EXPERIMENT=temp_study
"""

import argparse
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import AuditLogger


def run_experiment_at_temperature(
    experiment_base: str,
    temperature: float,
    config: str,
    models: str,
    prompt_types: str,
    n_samples: int,
    logger: AuditLogger,
) -> bool:
    """
    Run complete experiment at a specific temperature

    Returns:
        True if successful, False otherwise
    """
    exp_name = f"{experiment_base}_temp_{temperature:.1f}"

    logger.log_step(
        step_name=f"Temperature {temperature}",
        step_type="temperature_study",
        parameters={
            'temperature': temperature,
            'experiment': exp_name,
            'config': config,
            'models': models,
            'n_samples': n_samples,
        }
    )

    print(f"\n{'='*70}")
    print(f"Running experiment at temperature={temperature}")
    print(f"{'='*70}\n")

    # Run data collection
    cmd = [
        'python', 'scripts/collect_data.py',
        '--experiment', exp_name,
        '--config', config,
        '--models', *models.split(),
        '--prompt-types', *prompt_types.split(),
        '--n-samples', str(n_samples),
        '--temperature', str(temperature),
    ]

    try:
        result = subprocess.run(cmd, check=True)

        # Run metrics calculation
        cmd = [
            'python', 'scripts/calculate_metrics.py',
            '--experiment', f"{exp_name}_metrics",
        ]

        subprocess.run(cmd, check=True)

        logger.log_step(
            step_name=f"Completed temperature {temperature}",
            step_type="temperature_study",
            metadata={'success': True}
        )

        return True

    except subprocess.CalledProcessError as e:
        logger.log_error(
            step_name=f"Temperature {temperature}",
            error_message=str(e)
        )
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Run multi-temperature experimental study'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        required=True,
        help='Base experiment name'
    )
    parser.add_argument(
        '--temperatures',
        nargs='+',
        type=float,
        default=[0.5, 0.7, 1.0, 1.2],
        help='Temperature values to test (default: 0.5 0.7 1.0 1.2)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/tasks.example.json',
        help='Task configuration file'
    )
    parser.add_argument(
        '--models',
        type=str,
        default='gpt-4 claude-3.5-sonnet',
        help='Space-separated model names'
    )
    parser.add_argument(
        '--prompt-types',
        type=str,
        default='specification vague',
        help='Space-separated prompt types'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=30,
        help='Samples per condition'
    )

    args = parser.parse_args()

    # Initialize logger
    logger = AuditLogger(experiment_name=f"{args.experiment}_temperature_study")

    print(f"\n{'='*70}")
    print(f"  Multi-Temperature Experimental Study")
    print(f"{'='*70}")
    print(f"\nBase experiment: {args.experiment}")
    print(f"Temperatures: {args.temperatures}")
    print(f"Models: {args.models}")
    print(f"Samples per condition: {args.n_samples}")
    print(f"\nTotal conditions: {len(args.temperatures)} temperatures")
    print(f"Estimated time: {len(args.temperatures) * 2} hours")
    print(f"\n{'='*70}\n")

    # Log study parameters
    logger.log_step(
        step_name='Initialize temperature study',
        step_type='study_initialization',
        parameters={
            'temperatures': args.temperatures,
            'n_temperatures': len(args.temperatures),
            'models': args.models,
            'n_samples': args.n_samples,
        }
    )

    # Run experiment at each temperature
    results = {}

    for temp in args.temperatures:
        success = run_experiment_at_temperature(
            experiment_base=args.experiment,
            temperature=temp,
            config=args.config,
            models=args.models,
            prompt_types=args.prompt_types,
            n_samples=args.n_samples,
            logger=logger,
        )

        results[temp] = success

    # Summary
    print(f"\n{'='*70}")
    print(f"  Temperature Study Complete")
    print(f"{'='*70}\n")

    successful = sum(1 for s in results.values() if s)
    print(f"Successful: {successful}/{len(results)} temperatures")
    print(f"\nResults by temperature:")
    for temp, success in sorted(results.items()):
        status = "✓" if success else "✗"
        print(f"  {status} Temperature {temp:.1f}")

    print(f"\nMetrics files:")
    for temp in args.temperatures:
        exp_name = f"{args.experiment}_temp_{temp:.1f}"
        print(f"  data/processed/{exp_name}_metrics/metrics_summary.csv")

    # Finalize
    summary = logger.finalize()

    print(f"\n{'='*70}\n")

    # Return exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
