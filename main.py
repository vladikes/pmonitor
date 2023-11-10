import argparse
import logging
from datetime import datetime
from process_monitor import ProcessMonitor


def setup_logging(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    setup_logging(logging.INFO)
    parser = argparse.ArgumentParser(description="Process Monitor")
    parser.add_argument(
        "identifier", type=str, help="Name or PID of the process to monitor"
    )
    parser.add_argument("duration", type=int, help="Duration of monitoring in seconds")
    parser.add_argument(
        "--interval", type=int, default=5, help="Sampling interval in seconds"
    )
    parser.add_argument(
        "--by_pid", action="store_true", help="Specify if the identifier is a PID"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output report file name",
    )
    args = parser.parse_args()

    monitor = ProcessMonitor(args.identifier, args.duration, args.interval, args.by_pid)
    monitor.monitor()
    monitor.generate_report(args.output)


if __name__ == "__main__":
    main()
