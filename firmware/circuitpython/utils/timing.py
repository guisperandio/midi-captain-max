"""
MIDI Captain MAX - Timing and Performance Utilities

Provides timing measurement tools for performance monitoring and optimization.

Author: Max Cascone
Date: 2026-04-04
"""

import time


def measure_time(func, name, threshold_ms=10):
    """Measure function execution time and warn if over threshold.
    
    Args:
        func: Callable to measure
        name: Descriptive name for logging
        threshold_ms: Threshold in milliseconds for warning (default: 10ms)
    
    Returns:
        Result of func()
    
    Example:
        def slow_operation():
            time.sleep(0.015)
            return "done"
        
        result = measure_time(slow_operation, "slow_op", threshold_ms=10)
        # Output: ⚠️  slow_op took 15.2ms
    """
    start = time.monotonic()
    result = func()
    elapsed = (time.monotonic() - start) * 1000  # Convert to ms
    
    if elapsed > threshold_ms:
        print(f"⚠️  {name} took {elapsed:.1f}ms")
    
    return result


class PerformanceMonitor:
    """Context manager for monitoring operation timing.
    
    Usage:
        with PerformanceMonitor("MIDI processing", threshold_ms=5):
            handle_midi()
        # Automatically logs if operation exceeds threshold
    """
    
    def __init__(self, name, threshold_ms=10, enabled=True):
        """Initialize performance monitor.
        
        Args:
            name: Operation name for logging
            threshold_ms: Warning threshold in milliseconds
            enabled: Whether monitoring is active (allows easy enable/disable)
        """
        self.name = name
        self.threshold_ms = threshold_ms
        self.enabled = enabled
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        if self.enabled:
            self.start_time = time.monotonic()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log if over threshold."""
        if self.enabled and self.start_time is not None:
            elapsed = (time.monotonic() - self.start_time) * 1000
            if elapsed > self.threshold_ms:
                print(f"⚠️  {self.name} took {elapsed:.1f}ms")
        return False  # Don't suppress exceptions


class AverageTimer:
    """Track average execution time over multiple samples.
    
    Useful for monitoring loop iteration times and detecting performance degradation.
    
    Usage:
        timer = AverageTimer("Main Loop", samples=100)
        
        while True:
            with timer:
                # ... main loop operations ...
                pass
            
            if timer.sample_count >= 100:
                avg_ms = timer.average_ms()
                print(f"Average loop time: {avg_ms:.2f}ms")
                timer.reset()
    """
    
    def __init__(self, name, samples=100):
        """Initialize average timer.
        
        Args:
            name: Timer name for logging
            samples: Number of samples to track for moving average
        """
        if not isinstance(samples, int) or samples <= 0:
            raise ValueError(f"samples must be a positive integer, got {samples}")
        self.name = name
        self.samples = samples
        self.times = []
        self._write_index = 0  # Ring buffer write position
        self._is_full = False  # Track if buffer has wrapped
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.monotonic()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record timing sample."""
        if self.start_time is not None:
            elapsed = (time.monotonic() - self.start_time) * 1000
            
            # Use ring buffer for O(1) insertion instead of O(n) pop(0)
            if self._is_full:
                # Overwrite oldest sample
                self.times[self._write_index] = elapsed
            else:
                # Still filling buffer
                self.times.append(elapsed)
                if len(self.times) >= self.samples:
                    self._is_full = True
            
            # Advance write index with wrapping
            self._write_index = (self._write_index + 1) % self.samples
        
        return False  # Don't suppress exceptions
    
    @property
    def sample_count(self):
        """Get number of recorded samples."""
        return len(self.times)
    
    def average_ms(self):
        """Calculate average time in milliseconds."""
        if not self.times:
            return 0.0
        return sum(self.times) / len(self.times)
    
    def max_ms(self):
        """Get maximum time in milliseconds."""
        if not self.times:
            return 0.0
        return max(self.times)
    
    def min_ms(self):
        """Get minimum time in milliseconds."""
        if not self.times:
            return 0.0
        return min(self.times)
    
    def reset(self):
        """Clear all recorded samples."""
        self.times = []
        self._write_index = 0
        self._is_full = False
    
    def report(self):
        """Print performance summary."""
        if not self.times:
            print(f"{self.name}: No samples")
            return
        
        avg = self.average_ms()
        minimum = self.min_ms()
        maximum = self.max_ms()
        
        print(f"{self.name} ({len(self.times)} samples):")
        print(f"  Average: {avg:.2f}ms")
        print(f"  Min: {minimum:.2f}ms")
        print(f"  Max: {maximum:.2f}ms")


def format_duration(ms):
    """Format milliseconds as human-readable string.
    
    Args:
        ms: Duration in milliseconds
    
    Returns:
        Formatted string (e.g., "5.2ms", "1.2s")
    
    Examples:
        >>> format_duration(5.234)
        '5.2ms'
        >>> format_duration(1234.5)
        '1.2s'
    """
    if ms < 1000:
        return f"{ms:.1f}ms"
    else:
        return f"{ms/1000:.1f}s"
