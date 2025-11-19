"""
Utility functions for data processing and I/O
"""

from .io_utils import (
    save_json,
    load_json,
    save_pickle,
    load_pickle,
    save_csv,
    load_csv,
    save_dataframe,
    load_dataframe,
    ensure_dir,
    list_files,
)

from .data_utils import (
    normalize_text,
    tokenize_simple,
    remove_stopwords,
    compute_hash,
    batch_data,
    deduplicate,
    flatten_dict,
    calculate_percentiles,
    z_score_normalize,
    min_max_normalize,
    sliding_window,
    aggregate_by_key,
)

from .audit_logger import (
    AuditLogger,
    get_logger,
    set_logger,
)

__all__ = [
    # I/O utilities
    'save_json',
    'load_json',
    'save_pickle',
    'load_pickle',
    'save_csv',
    'load_csv',
    'save_dataframe',
    'load_dataframe',
    'ensure_dir',
    'list_files',
    # Data utilities
    'normalize_text',
    'tokenize_simple',
    'remove_stopwords',
    'compute_hash',
    'batch_data',
    'deduplicate',
    'flatten_dict',
    'calculate_percentiles',
    'z_score_normalize',
    'min_max_normalize',
    'sliding_window',
    'aggregate_by_key',
    # Audit logging
    'AuditLogger',
    'get_logger',
    'set_logger',
]
