# Process Monitor

This Python script monitors specific processes on your system, collecting metrics such as CPU usage, memory usage, and file descriptor count. It's designed to run on systems with the `psutil` library installed and provides insights into process performance and potential memory leaks.

## Features

- Monitor specific processes by name or PID.
- Collect metrics including CPU usage, memory usage, and file descriptor count.
- Generate a report in CSV format.
- Detect potential memory leaks based on memory usage patterns.
- Configurable monitoring duration and sampling interval.

## Installation

1. **Clone the Repository or Download the Script**: Get the script onto your local machine.

2. **Install Required Libraries**: Navigate to the script's directory in your terminal and run the following command to install the required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

    This command will automatically install `psutil`, which is required for the script to function properly.

## Usage

Run the script from the command line, providing the necessary arguments. Here's how you can use it:

```bash
python main.py <identifier> <duration> [--interval INTERVAL] [--by_pid] [--output OUTPUT]
```

Example:

```
python main.py "nginx" 60 --interval 10
```

## Output

The script generates a CSV report with the collected metrics. The default output file is named 'process_report_<timestamp>.csv'.

## Running Unit Tests
This project uses pytest for unit testing. you can run the tests from the project's root directory:
```
pytest tests/
```
This command will discover and execute all the test cases in the tests/ directory.
