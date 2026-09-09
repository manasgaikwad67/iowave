"""Performance monitoring utilities."""

import time
import functools
from typing import Dict, Any, Callable, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class TimingResult:
    """Result of a timed operation."""

    name: str
    elapsed_seconds: float
    memory_delta_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Timer:
    """Simple timer for measuring execution time."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed = 0.0

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()
        return self

    def stop(self):
        """Stop the timer."""
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        return self

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time == 0:
            return time.perf_counter() - self.start_time
        return self.elapsed


class PerformanceMonitor:
    """Monitor performance of multiple operations."""

    def __init__(self):
        self.timings: Dict[str, TimingResult] = {}
        self.active_timers: Dict[str, Timer] = {}

    def start(self, name: str) -> Timer:
        """Start timing an operation."""
        timer = Timer(name)
        self.active_timers[name] = timer
        return timer.start()

    def stop(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> TimingResult:
        """Stop timing an operation."""
        if name not in self.active_timers:
            raise KeyError(f"Timer '{name}' not started")
        timer = self.active_timers.pop(name)
        timer.stop()
        result = TimingResult(
            name=name,
            elapsed_seconds=timer.elapsed,
            metadata=metadata or {},
        )
        self.timings[name] = result
        return result

    @contextmanager
    def measure(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for measuring an operation."""
        self.start(name)
        try:
            yield
        finally:
            self.stop(name, metadata)

    def get_result(self, name: str) -> Optional[TimingResult]:
        """Get timing result for an operation."""
        return self.timings.get(name)

    def get_total_time(self) -> float:
        """Get total time of all completed operations."""
        return sum(t.elapsed_seconds for t in self.timings.values())

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "operations": {name: result.elapsed_seconds for name, result in self.timings.items()},
            "total_time": self.get_total_time(),
            "count": len(self.timings),
        }

    def clear(self):
        """Clear all timing results."""
        self.timings.clear()
        self.active_timers.clear()


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _performance_monitor


def timed(name: Optional[str] = None, monitor: Optional[PerformanceMonitor] = None):
    """Decorator for timing a function."""
    if monitor is None:
        monitor = _performance_monitor

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer_name = name or func.__name__
            monitor.start(timer_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.stop(timer_name)

        return wrapper

    return decorator