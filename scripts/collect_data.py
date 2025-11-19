#!/usr/bin/env python3
"""
Data collection script with full audit logging

Usage:
    python scripts/collect_data.py --experiment exp001 --config config.json
    make collect-data EXPERIMENT=exp001 CONFIG=config.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sampling import sample_responses
from src.utils import AuditLogger, save_json, ensure_dir


def load_tasks(config_file: str) -> List[Dict]:
    """Load task definitions from config file"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config.get('tasks', [])


def collect_for_task(
    task: Dict,
    task_id: int,
    prompt_type: str,
    model: str,
    n_samples: int,
    temperature: float,
    logger: AuditLogger,
    output_dir: Path,
) -> str:
    """
    Collect data for a single task

    Returns:
        Path to output file
    """
    start_time = time.time()

    # Get prompt
    prompt = task['prompts'][prompt_type]

    # Generate filename
    filename = f"task_{task_id:03d}_{prompt_type}_{model.replace('-', '_')}.json"
    output_file = output_dir / filename

    try:
        # Sample responses
        logger.log_step(
            step_name=f"Sampling task {task_id}",
            step_type="data_collection",
            parameters={
                'task_id': task_id,
                'task_description': task.get('description', ''),
                'prompt_type': prompt_type,
                'model': model,
                'n_samples': n_samples,
                'temperature': temperature,
            }
        )

        responses = sample_responses(
            prompt=prompt,
            model=model,
            n=n_samples,
            temperature=temperature,
            show_progress=True,
            delay_between_requests=0.5,
        )

        # Save data
        data = {
            'task_id': task_id,
            'task_description': task.get('description', ''),
            'task_domain': task.get('domain', ''),
            'prompt_type': prompt_type,
            'prompt': prompt,
            'model': model,
            'temperature': temperature,
            'n_samples': n_samples,
            'responses': responses,
            'timestamp': time.time(),
            'collection_duration': time.time() - start_time,
        }

        save_json(data, str(output_file))

        duration = time.time() - start_time

        # Log success
        logger.log_data_collection(
            task_id=task_id,
            prompt_type=prompt_type,
            model=model,
            n_samples=n_samples,
            temperature=temperature,
            output_file=str(output_file),
            duration=duration,
            success=True,
        )

        logger.log_file_output(
            operation='save',
            file_path=str(output_file),
            file_type='json',
            metadata={
                'n_responses': len(responses),
                'task_id': task_id,
            }
        )

        return str(output_file)

    except Exception as e:
        duration = time.time() - start_time

        # Log error
        logger.log_data_collection(
            task_id=task_id,
            prompt_type=prompt_type,
            model=model,
            n_samples=n_samples,
            temperature=temperature,
            output_file=str(output_file),
            duration=duration,
            success=False,
            error=str(e),
        )

        logger.log_error(
            step_name=f"Task {task_id} collection",
            error_message=str(e),
        )

        raise


def main():
    parser = argparse.ArgumentParser(
        description='Collect LLM responses for prompt entropy experiment'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        required=True,
        help='Experiment name for audit logging'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/tasks.json',
        help='Path to task configuration file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for raw data'
    )
    parser.add_argument(
        '--models',
        nargs='+',
        default=['gpt-4', 'claude-3-opus'],
        help='Models to use for data collection'
    )
    parser.add_argument(
        '--prompt-types',
        nargs='+',
        default=['specification', 'vague'],
        help='Prompt types to collect'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=30,
        help='Number of samples per condition'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=1.0,
        help='Sampling temperature'
    )
    parser.add_argument(
        '--task-ids',
        nargs='+',
        type=int,
        help='Specific task IDs to collect (default: all)'
    )

    args = parser.parse_args()

    # Initialize logger
    logger = AuditLogger(experiment_name=args.experiment)

    print(f"\n{'='*60}")
    print(f"Data Collection: {args.experiment}")
    print(f"{'='*60}\n")

    # Load tasks
    logger.log_step(
        step_name='Load task configuration',
        step_type='initialization',
        parameters={'config_file': args.config}
    )

    tasks = load_tasks(args.config)

    if args.task_ids:
        tasks = [t for t in tasks if t.get('id') in args.task_ids]

    print(f"Loaded {len(tasks)} tasks")
    print(f"Models: {', '.join(args.models)}")
    print(f"Prompt types: {', '.join(args.prompt_types)}")
    print(f"Samples per condition: {args.n_samples}")
    print(f"Temperature: {args.temperature}\n")

    # Ensure output directory
    output_dir = ensure_dir(args.output_dir)

    # Collection loop
    total_conditions = len(tasks) * len(args.models) * len(args.prompt_types)
    completed = 0

    for task in tasks:
        task_id = task.get('id', tasks.index(task))

        for prompt_type in args.prompt_types:
            for model in args.models:
                try:
                    print(f"\n[{completed+1}/{total_conditions}] Task {task_id} | {prompt_type} | {model}")

                    output_file = collect_for_task(
                        task=task,
                        task_id=task_id,
                        prompt_type=prompt_type,
                        model=model,
                        n_samples=args.n_samples,
                        temperature=args.temperature,
                        logger=logger,
                        output_dir=output_dir,
                    )

                    completed += 1
                    print(f"✓ Saved to: {output_file}")

                    # Rate limiting between conditions
                    if completed < total_conditions:
                        time.sleep(2)

                except Exception as e:
                    print(f"✗ Error: {e}")
                    # Continue with next condition
                    continue

    # Finalize logging
    print(f"\n{'='*60}")
    summary = logger.finalize()
    print(f"{'='*60}\n")

    print(f"Collection complete!")
    print(f"Total conditions collected: {completed}/{total_conditions}")
    print(f"Success rate: {completed/total_conditions*100:.1f}%")


if __name__ == '__main__':
    main()
