"""Memory monitoring utilities."""

import psutil
import numpy as np
from typing import Optional


def get_available_memory_mb() -> float:
    """Get available system memory in MB."""
    return psutil.virtual_memory().available / (1024 * 1024)


def get_total_memory_mb() -> float:
    """Get total system memory in MB."""
    return psutil.virtual_memory().total / (1024 * 1024)


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def estimate_array_memory(shape: tuple, dtype: np.dtype) -> float:
    """Estimate memory required for a numpy array in MB."""
    itemsize = np.dtype(dtype).itemsize
    total_bytes = np.prod(shape) * itemsize
    return total_bytes / (1024 * 1024)


def check_memory_requirement(required_mb: float, max_mb: Optional[float] = None) -> bool:
    """Check if memory requirement can be satisfied."""
    if max_mb is None:
        max_mb = get_available_memory_mb() * 0.8  # Use 80% of available
    return required_mb <= max_mb


def get_optimal_chunk_size(
    total_samples: int,
    sample_size_bytes: int,
    max_memory_mb: float = 100,
) -> int:
    """Calculate optimal chunk size for processing large arrays."""
    max_bytes = max_memory_mb * 1024 * 1024
    chunk_size = max_bytes // sample_size_bytes
    return min(chunk_size, total_samples)


class MemoryMonitor:
    """Context manager for monitoring memory usage."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_memory = 0.0
        self.peak_memory = 0.0

    def __enter__(self):
        self.start_memory = get_memory_usage_mb()
        self.peak_memory = self.start_memory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        current = get_memory_usage_mb()
        self.peak_memory = max(self.peak_memory, current)
        delta = self.peak_memory - self.start_memory
        return False

    def update_peak(self):
        """Update peak memory usage."""
        current = get_memory_usage_mb()
        self.peak_memory = max(self.peak_memory, current)

    def get_delta_mb(self) -> float:
        """Get memory delta from start."""
        return get_memory_usage_mb() - self.start_memory

    def get_peak_delta_mb(self) -> float:
        """Get peak memory delta from start."""
        return self.peak_memory - self.start_memory