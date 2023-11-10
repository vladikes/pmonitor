import psutil
import time
import csv
import argparse
import logging
import sys
from functools import wraps
from datetime import datetime


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psutil.NoSuchProcess:
            logging.error(f"No process found: {args[0].identifier}")
            sys.exit(1)
        except psutil.AccessDenied:
            logging.error(f"Access denied to process: {args[0].identifier}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            sys.exit(1)

    return wrapper


class MemoryLeakDetector:
    """
       A class used to detect memory leaks in a process based on its memory usage.

       Methods
       -------
       detect(memory_usage)
           Determines if there is a potential memory leak based on the memory usage list.

       simple_increase(memory_usage)
           Checks if there is a simple increase in memory usage over time.

       standard_deviation_method(memory_usage, threshold=5)
           Uses standard deviation to detect significant changes in memory usage that might indicate a leak.

       percentage_increase_method(memory_usage, threshold=0.1)
           Checks if the percentage increase in memory usage over time exceeds a given threshold.
       """
    @staticmethod
    def detect(memory_usage):
        if len(memory_usage) < 3:
            return False
        return memory_usage[-1] > memory_usage[0]


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
            try:
                return [psutil.Process(self.identifier)]
            except psutil.NoSuchProcess:
                self.logger.error(f"No process found with PID: {self.identifier}")
                return []
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == self.identifier:
                    found_processes.append(proc)
            if not found_processes:
                self.logger.error(f"No process found with name: {self.identifier}")
            return found_processes

    @error_handler
    def gather_metrics(self, process):
        self.logger.info(f"Gathering metrics for process: {process.pid}")
        cpu_percent = process.cpu_percent(interval=1)
        memory_info = process.memory_full_info()
        memory_usage = memory_info.uss
        num_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
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
                else:
                    self.logger.warning(f"Process {process.pid} exited during monitoring.")
            time.sleep(self.interval)

    def generate_report(self, report_name):
        if not self.metrics:
            self.logger.warning("No data collected. Unable to generate report.")
            return

        with open(report_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['CPU %', 'Memory Usage', 'File Descriptors'])
            writer.writerows(self.metrics)

        avg_cpu = sum(m[0] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m[1] for m in self.metrics) / len(self.metrics)
        avg_fds = sum(m[2] for m in self.metrics) / len(self.metrics)

        self.logger.info(f"Average CPU Usage: {avg_cpu}%")
        self.logger.info(f"Average Memory Usage: {avg_memory} bytes")
        self.logger.info(f"Average Number of File Descriptors: {avg_fds}")

        if MemoryLeakDetector.detect(self.memory_usage):
            self.logger.warning("Possible memory leak detected.")


def main():
    """
    The main function which parses command line arguments and initiates the monitoring process.

    This function sets up the logging, parses command-line arguments, creates an instance of ProcessMonitor,
    and invokes its monitoring and report generation functionalities.
    """
    setup_logging()  # Set up logging configuration

    parser = argparse.ArgumentParser(description="Process Monitor")
    parser.add_argument("identifier", type=str, help="Name or PID of the process to monitor")
    parser.add_argument("duration", type=int, help="Duration of monitoring in seconds")
    parser.add_argument("--interval", type=int, default=5, help="Sampling interval in seconds")
    parser.add_argument("--by_pid", action="store_true", help="Specify if the identifier is a PID")
    parser.add_argument("--output", type=str, default=f"process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        help="Output report file name")
    args = parser.parse_args()

    monitor = ProcessMonitor(args.identifier, args.duration, args.interval, args.by_pid)
    monitor.monitor()
    monitor.generate_report(args.output)


if __name__ == "__main__":
    main()
