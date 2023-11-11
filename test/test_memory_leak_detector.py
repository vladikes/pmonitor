import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from memory_leak_detector import MemoryLeakDetector


def test_memory_leak_detection_no_increase():
    memory_usage = [100, 100, 100]
    assert not MemoryLeakDetector.detect(memory_usage)


def test_memory_leak_detection_simple_increase():
    memory_usage = [100, 150, 200]
    assert MemoryLeakDetector.detect(memory_usage)


def test_memory_leak_detection_with_fluctuations():
    memory_usage = [100, 200, 150, 250, 300]
    assert MemoryLeakDetector.detect(memory_usage)


def test_memory_leak_detection_empty_data():
    memory_usage = []
    assert not MemoryLeakDetector.detect(memory_usage)
