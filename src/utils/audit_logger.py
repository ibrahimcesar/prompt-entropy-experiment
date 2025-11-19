"""
Audit logging utilities for experimental reproducibility
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import hashlib
import platform


class AuditLogger:
    """
    Audit logger for tracking experimental steps and ensuring reproducibility

    Creates detailed logs of all experimental operations including:
    - Data collection parameters
    - Model versions and settings
    - Metrics calculations
    - Statistical analyses
    - Git commit hashes
    - System information
    """

    def __init__(self, log_dir: str = "logs", experiment_name: Optional[str] = None):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for log files
            experiment_name: Name of experiment (auto-generated if None)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if experiment_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            experiment_name = f"experiment_{timestamp}"

        self.experiment_name = experiment_name
        self.log_file = self.log_dir / f"{experiment_name}.jsonl"
        self.summary_file = self.log_dir / f"{experiment_name}_summary.json"

        self.session_start = time.time()
        self.entries: List[Dict[str, Any]] = []

        # Log session start
        self._log_session_start()

    def _log_session_start(self):
        """Log session initialization"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'session_start',
            'experiment_name': self.experiment_name,
            'system_info': self._get_system_info(),
            'git_info': self._get_git_info(),
            'environment': self._get_environment_info(),
        }
        self._write_entry(entry)

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'machine': platform.machine(),
        }

    def _get_git_info(self) -> Dict[str, Any]:
        """Get git repository information"""
        import subprocess

        try:
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            # Check for uncommitted changes
            status = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                stderr=subprocess.DEVNULL
            ).decode().strip()

            return {
                'commit_hash': commit_hash,
                'branch': branch,
                'has_uncommitted_changes': bool(status),
                'dirty': bool(status),
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {'error': 'Git information unavailable'}

    def _get_environment_info(self) -> Dict[str, str]:
        """Get relevant environment variables (excluding secrets)"""
        relevant_vars = [
            'PYTHONPATH',
            'VIRTUAL_ENV',
            'CONDA_DEFAULT_ENV',
        ]
        return {
            var: os.environ.get(var, '')
            for var in relevant_vars
            if os.environ.get(var)
        }

    def _write_entry(self, entry: Dict[str, Any]):
        """Write entry to log file"""
        # Add to in-memory list
        self.entries.append(entry)

        # Append to JSONL file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def log_step(self,
                 step_name: str,
                 step_type: str,
                 parameters: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Log an experimental step

        Args:
            step_name: Name of the step
            step_type: Type of step (data_collection, metrics, analysis, etc.)
            parameters: Step parameters
            metadata: Additional metadata
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'step',
            'step_name': step_name,
            'step_type': step_type,
            'parameters': parameters or {},
            'metadata': metadata or {},
        }
        self._write_entry(entry)

        print(f"[AUDIT] {step_type}: {step_name}")

    def log_data_collection(self,
                           task_id: int,
                           prompt_type: str,
                           model: str,
                           n_samples: int,
                           temperature: float,
                           output_file: str,
                           duration: float,
                           success: bool = True,
                           error: Optional[str] = None):
        """Log data collection operation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_collection',
            'task_id': task_id,
            'prompt_type': prompt_type,
            'model': model,
            'n_samples': n_samples,
            'temperature': temperature,
            'output_file': output_file,
            'output_hash': self._compute_file_hash(output_file) if success else None,
            'duration_seconds': duration,
            'success': success,
            'error': error,
        }
        self._write_entry(entry)

        status = "✓" if success else "✗"
        print(f"[AUDIT] {status} Data Collection: task={task_id}, model={model}, n={n_samples}")

    def log_metrics_calculation(self,
                               input_file: str,
                               metrics: Dict[str, float],
                               metric_type: str,
                               duration: float):
        """Log metrics calculation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'metrics_calculation',
            'metric_type': metric_type,
            'input_file': input_file,
            'input_hash': self._compute_file_hash(input_file),
            'metrics': metrics,
            'duration_seconds': duration,
        }
        self._write_entry(entry)

        print(f"[AUDIT] ✓ Metrics: {metric_type} ({len(metrics)} metrics)")

    def log_statistical_analysis(self,
                                 analysis_type: str,
                                 data_files: List[str],
                                 results: Dict[str, Any],
                                 duration: float):
        """Log statistical analysis"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'statistical_analysis',
            'analysis_type': analysis_type,
            'data_files': data_files,
            'results': results,
            'duration_seconds': duration,
        }
        self._write_entry(entry)

        print(f"[AUDIT] ✓ Analysis: {analysis_type}")

    def log_error(self,
                  step_name: str,
                  error_message: str,
                  traceback: Optional[str] = None):
        """Log an error"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'step_name': step_name,
            'error_message': error_message,
            'traceback': traceback,
        }
        self._write_entry(entry)

        print(f"[AUDIT] ✗ Error in {step_name}: {error_message}")

    def log_file_output(self,
                       operation: str,
                       file_path: str,
                       file_type: str,
                       metadata: Optional[Dict[str, Any]] = None):
        """Log file output"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'file_output',
            'operation': operation,
            'file_path': file_path,
            'file_type': file_type,
            'file_hash': self._compute_file_hash(file_path),
            'file_size': Path(file_path).stat().st_size if Path(file_path).exists() else None,
            'metadata': metadata or {},
        }
        self._write_entry(entry)

    def _compute_file_hash(self, file_path: str) -> Optional[str]:
        """Compute SHA256 hash of file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (FileNotFoundError, PermissionError):
            return None

    def finalize(self):
        """Finalize logging session and write summary"""
        session_duration = time.time() - self.session_start

        # Count events by type
        event_counts = {}
        for entry in self.entries:
            event_type = entry.get('event_type', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Create summary
        summary = {
            'experiment_name': self.experiment_name,
            'session_start': datetime.fromtimestamp(self.session_start).isoformat(),
            'session_end': datetime.now().isoformat(),
            'total_duration_seconds': session_duration,
            'total_events': len(self.entries),
            'event_counts': event_counts,
            'log_file': str(self.log_file),
            'git_info': self._get_git_info(),
        }

        # Write summary
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n[AUDIT] Session complete: {len(self.entries)} events logged")
        print(f"[AUDIT] Duration: {session_duration:.2f}s")
        print(f"[AUDIT] Log: {self.log_file}")
        print(f"[AUDIT] Summary: {self.summary_file}")

        return summary


# Global logger instance
_global_logger: Optional[AuditLogger] = None


def get_logger(experiment_name: Optional[str] = None) -> AuditLogger:
    """Get or create global audit logger"""
    global _global_logger

    if _global_logger is None:
        _global_logger = AuditLogger(experiment_name=experiment_name)

    return _global_logger


def set_logger(logger: AuditLogger):
    """Set global audit logger"""
    global _global_logger
    _global_logger = logger
