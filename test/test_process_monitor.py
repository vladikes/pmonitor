import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from process_monitor import ProcessMonitor
from unittest.mock import patch, Mock


@pytest.fixture
def mock_psutil_process():
    mock_process = Mock()
    mock_process.cpu_percent.return_value = 10.0
    mock_process.memory_full_info.return_value.uss = 1024
    mock_process.num_fds.return_value = 5
    return mock_process


@patch("psutil.process_iter")
def test_process_monitor_find_process(mock_process_iter, mock_psutil_process):
    mock_process_iter.return_value = [mock_psutil_process]
    monitor = ProcessMonitor("test_process", 10)
    found_processes = monitor.find_process()
    assert len(found_processes) == 1


@patch("psutil.Process")
def test_process_monitor_gather_metrics(mock_psutil_process_cls, mock_psutil_process):
    mock_psutil_process_cls.return_value = mock_psutil_process
    monitor = ProcessMonitor("test_process", 10)
    metrics = monitor.gather_metrics(mock_psutil_process)
    assert metrics == (10.0, 1024, 5)
