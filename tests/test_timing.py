"""
Tests for performance monitoring and timing utilities.

Validates timing measurement tools work correctly and provide accurate measurements.
"""

import pytest
import sys
import time
from pathlib import Path

# Add the firmware directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "firmware" / "circuitpython"))

from utils.timing import (
    measure_time,
    PerformanceMonitor,
    AverageTimer,
    format_duration
)


class TestMeasureTime:
    """Test measure_time function."""

    def test_returns_function_result(self):
        """measure_time should return the function's result."""
        def returns_42():
            return 42
        
        result = measure_time(returns_42, "test", threshold_ms=1000)
        assert result == 42

    def test_warns_over_threshold(self, capsys, monkeypatch):
        """measure_time should print warning if over threshold."""
        # Mock time to avoid flaky tests on slow CI
        mock_times = iter([0.0, 0.015])  # 15ms elapsed
        monkeypatch.setattr(time, "monotonic", lambda: next(mock_times))
        
        def slow_func():
            return "done"
        
        result = measure_time(slow_func, "slow_op", threshold_ms=10)
        
        assert result == "done"
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "slow_op" in captured.out
        assert "ms" in captured.out

    def test_no_warning_under_threshold(self, capsys):
        """measure_time should not print if under threshold."""
        def fast_func():
            return "done"
        
        result = measure_time(fast_func, "fast_op", threshold_ms=100)
        
        assert result == "done"
        captured = capsys.readouterr()
        assert captured.out == ""


class TestPerformanceMonitor:
    """Test PerformanceMonitor context manager."""

    def test_context_manager_syntax(self):
        """PerformanceMonitor should work as context manager."""
        with PerformanceMonitor("test", threshold_ms=1000, enabled=False):
            time.sleep(0.001)
        # No assertion needed - just testing syntax works

    def test_warns_over_threshold(self, capsys, monkeypatch):
        """PerformanceMonitor should warn if operation exceeds threshold."""
        # Mock time to avoid flaky tests on slow CI
        mock_times = iter([0.0, 0.015])  # 15ms elapsed
        monkeypatch.setattr(time, "monotonic", lambda: next(mock_times))
        
        with PerformanceMonitor("slow_operation", threshold_ms=10, enabled=True):
            pass
        
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "slow_operation" in captured.out

    def test_no_warning_under_threshold(self, capsys):
        """PerformanceMonitor should not warn if under threshold."""
        with PerformanceMonitor("fast_operation", threshold_ms=100, enabled=True):
            time.sleep(0.001)  # 1ms
        
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_disabled_monitor_does_nothing(self, capsys):
        """PerformanceMonitor with enabled=False should not monitor."""
        with PerformanceMonitor("test", threshold_ms=1, enabled=False):
            time.sleep(0.010)  # 10ms (way over threshold)
        
        captured = capsys.readouterr()
        assert captured.out == ""  # No output when disabled

    def test_exception_propagation(self):
        """PerformanceMonitor should propagate exceptions."""
        with pytest.raises(ValueError, match="test error"):
            with PerformanceMonitor("test", enabled=True):
                raise ValueError("test error")


class TestAverageTimer:
    """Test AverageTimer class."""

    def test_tracks_multiple_samples(self):
        """AverageTimer should track multiple timing samples."""
        timer = AverageTimer("test", samples=10)
        
        for _ in range(5):
            with timer:
                time.sleep(0.001)
        
        assert timer.sample_count == 5

    def test_calculates_average(self):
        """AverageTimer should calculate correct average."""
        timer = AverageTimer("test", samples=10)
        
        # Simulate timing samples
        timer.times = [10.0, 20.0, 30.0]  # Manually set for predictability
        
        avg = timer.average_ms()
        assert avg == 20.0

    def test_tracks_max(self):
        """AverageTimer should track maximum time."""
        timer = AverageTimer("test", samples=10)
        timer.times = [10.0, 25.0, 15.0]
        
        assert timer.max_ms() == 25.0

    def test_tracks_min(self):
        """AverageTimer should track minimum time."""
        timer = AverageTimer("test", samples=10)
        timer.times = [10.0, 25.0, 15.0]
        
        assert timer.min_ms() == 10.0

    def test_limits_sample_count(self, monkeypatch):
        """AverageTimer should keep only most recent N samples."""
        timer = AverageTimer("test", samples=3)
        
        # Mock time to provide deterministic timing values
        clock_values = iter([
            0.000, 0.001,  # 1ms
            1.000, 1.002,  # 2ms
            2.000, 2.003,  # 3ms
            3.000, 3.004,  # 4ms
            4.000, 4.005,  # 5ms
        ])
        monkeypatch.setattr(time, "monotonic", lambda: next(clock_values))
        
        # Drive timer through context manager to test actual trimming behavior
        for i in range(5):
            with timer:
                pass
            # Verify length never exceeds sample limit
            assert len(timer.times) == min(i + 1, timer.samples)
        
        # After 5 iterations, should keep only last 3 samples (order doesn't matter in ring buffer)
        assert len(timer.times) == 3
        assert sorted(timer.times) == pytest.approx([3.0, 4.0, 5.0])

    def test_reset_clears_samples(self):
        """AverageTimer.reset() should clear all samples."""
        timer = AverageTimer("test", samples=10)
        timer.times = [1.0, 2.0, 3.0]
        
        timer.reset()
        
        assert len(timer.times) == 0
        assert timer.sample_count == 0

    def test_empty_timer_returns_zero(self):
        """AverageTimer should return 0 for empty statistics."""
        timer = AverageTimer("test", samples=10)
        
        assert timer.average_ms() == 0.0
        assert timer.max_ms() == 0.0
        assert timer.min_ms() == 0.0

    def test_report_output(self, capsys):
        """AverageTimer.report() should print summary."""
        timer = AverageTimer("Main Loop", samples=10)
        timer.times = [5.0, 10.0, 15.0]
        
        timer.report()
        
        captured = capsys.readouterr()
        assert "Main Loop" in captured.out
        assert "3 samples" in captured.out
        assert "Average" in captured.out
        assert "Min" in captured.out
        assert "Max" in captured.out
        assert "10.00ms" in captured.out  # Average
        assert "5.00ms" in captured.out   # Min
        assert "15.00ms" in captured.out  # Max

    def test_report_empty_timer(self, capsys):
        """AverageTimer.report() should handle empty timer."""
        timer = AverageTimer("Empty", samples=10)
        
        timer.report()
        
        captured = capsys.readouterr()
        assert "Empty" in captured.out
        assert "No samples" in captured.out


class TestFormatDuration:
    """Test format_duration function."""

    def test_formats_milliseconds(self):
        """format_duration should format values under 1000ms."""
        assert format_duration(5.234) == "5.2ms"
        assert format_duration(42.9) == "42.9ms"
        assert format_duration(999.9) == "999.9ms"

    def test_formats_seconds(self):
        """format_duration should format values over 1000ms as seconds."""
        assert format_duration(1000.0) == "1.0s"
        assert format_duration(1234.5) == "1.2s"
        assert format_duration(5678.9) == "5.7s"

    def test_handles_zero(self):
        """format_duration should handle zero."""
        assert format_duration(0.0) == "0.0ms"

    def test_handles_very_small(self):
        """format_duration should handle very small values."""
        assert format_duration(0.001) == "0.0ms"
        assert format_duration(0.1) == "0.1ms"


class TestRealWorldScenarios:
    """Test timing utilities in realistic scenarios."""

    def test_main_loop_monitoring(self, capsys):
        """Simulate monitoring a main loop."""
        timer = AverageTimer("Main Loop", samples=10)
        
        # Simulate 10 loop iterations
        for i in range(10):
            with timer:
                time.sleep(0.001)  # 1ms per iteration
        
        assert timer.sample_count == 10
        avg = timer.average_ms()
        assert 0.5 < avg < 5.0  # Should be around 1ms (with some tolerance)
        
        timer.report()
        captured = capsys.readouterr()
        assert "Main Loop" in captured.out

    def test_performance_budget_checking(self, capsys):
        """Simulate checking if operation stays within performance budget."""
        # Budget: MIDI processing should complete in <5ms
        with PerformanceMonitor("MIDI processing", threshold_ms=5, enabled=True):
            time.sleep(0.002)  # 2ms - under budget
        
        captured = capsys.readouterr()
        assert captured.out == ""  # No warning
        
        # Now exceed budget
        with PerformanceMonitor("MIDI flooding", threshold_ms=5, enabled=True):
            time.sleep(0.010)  # 10ms - over budget
        
        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "MIDI flooding" in captured.out

    def test_conditional_monitoring(self, capsys):
        """Simulate enabling/disabling monitoring based on flag."""
        ENABLE_MONITORING = False
        
        # Slow operation, but monitoring disabled
        with PerformanceMonitor("test", threshold_ms=1, enabled=ENABLE_MONITORING):
            time.sleep(0.100)  # 100ms
        
        captured = capsys.readouterr()
        assert captured.out == ""  # No output when disabled
        
        # Now enable monitoring
        ENABLE_MONITORING = True
        
        with PerformanceMonitor("test", threshold_ms=1, enabled=ENABLE_MONITORING):
            time.sleep(0.010)  # 10ms
        
        captured = capsys.readouterr()
        assert "⚠️" in captured.out  # Should warn now
