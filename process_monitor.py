import psutil
import logging
import time
import csv
from memory_leak_detector import MemoryLeakDetector
from error_handler import error_handler


class ProcessMonitor:
    """
    A class to monitor specific processes on a system, collecting metrics like CPU usage, memory usage,
    and file descriptor count.

    Attributes
    ----------
    identifier : str
        Name or PID of the process to be monitored.
    duration : int
        The duration for which to monitor the process, in seconds.
    interval : int
        The interval between each sampling, in seconds.
    by_pid : bool
        Flag to indicate if the identifier is a PID.

    Methods
    -------
    find_process()
        Finds the process(es) based on the identifier and returns them.

    gather_metrics(process)
        Gathers and returns the metrics (CPU usage, memory usage, file descriptors) for a given process.

    monitor()
        Monitors the specified processes, gathering metrics at each interval.

    generate_report(report_name)
        Generates a CSV report with the collected metrics.
    """

    def __init__(self, identifier, duration, interval=5, by_pid=False):
        self.identifier = identifier
        self.duration = duration
        self.interval = interval
        self.by_pid = by_pid
        self.metrics = []
        self.memory_usage = []
        self.logger = logging.getLogger(str(self.identifier))

    @error_handler
    def find_process(self):
        found_processes = []
        if self.by_pid:
            return [psutil.Process(self.identifier)]
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] == self.identifier:
                found_processes.append(proc)
        return found_processes

    @error_handler
    def gather_metrics(self, process):
        self.logger.info(f"Gathering metrics for process: {process.pid}")
        cpu_percent = process.cpu_percent(interval=1)
        memory_info = process.memory_full_info()
        memory_usage = memory_info.uss
        num_fds = process.num_fds() if hasattr(process, "num_fds") else 0
        return cpu_percent, memory_usage, num_fds

    def monitor(self):
        processes = self.find_process()
        if not processes:
            self.logger.warning("No matching processes found to monitor.")
            return

        self.logger.info(f"Found {len(processes)} process(es) to monitor.")
        end_time = time.time() + self.duration
        while time.time() < end_time:
            for process in processes:
                data = self.gather_metrics(process)
                if data:
                    self.metrics.append(data)
                    self.memory_usage.append(data[1])
            time.sleep(self.interval)

    def generate_report(self, report_name):
        if not self.metrics:
            self.logger.warning("No data collected. Unable to generate report.")
            return

        with open(report_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["CPU %", "Memory Usage", "File Descriptors"])
            writer.writerows(self.metrics)

        avg_cpu = sum(m[0] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m[1] for m in self.metrics) / len(self.metrics)
        avg_fds = sum(m[2] for m in self.metrics) / len(self.metrics)

        self.logger.info(f"Average CPU Usage: {avg_cpu}%")
        self.logger.info(f"Average Memory Usage: {avg_memory} bytes")
        self.logger.info(f"Average Number of File Descriptors: {avg_fds}")

        if MemoryLeakDetector.detect(self.memory_usage):
            self.logger.warning("Possible memory leak detected.")
