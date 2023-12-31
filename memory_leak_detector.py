from error_handler import error_handler


class MemoryLeakDetector:
    """
    A class used to detect memory leaks in a process based on its memory usage.

    Methods
    -------
    detect(memory_usage)
        The detect method considers there to be a potential memory leak if any one of these three methods returns True.

    simple_increase(memory_usage)
        checks if the last recorded memory usage is greater than the first recorded usage.

    standard_deviation_method(memory_usage, threshold=5)
        Uses standard deviation to detect significant changes in memory usage that might indicate a leak.

    percentage_increase_method(memory_usage, threshold=0.1)
        Checks if the percentage increase in memory usage over time exceeds a given threshold.
    """

    @staticmethod
    @error_handler
    def detect(memory_usage):
        return (
            MemoryLeakDetector.simple_increase(memory_usage)
            or MemoryLeakDetector.standard_deviation_method(memory_usage)
            or MemoryLeakDetector.percentage_increase_method(memory_usage)
        )

    @staticmethod
    def simple_increase(memory_usage):
        if len(memory_usage) < 3:
            return False
        return memory_usage[-1] > memory_usage[0]

    @staticmethod
    def standard_deviation_method(memory_usage, threshold=5):
        if len(memory_usage) < 3:
            return False
        mean = sum(memory_usage) / len(memory_usage)
        variance = sum((x - mean) ** 2 for x in memory_usage) / len(memory_usage)
        return (variance**0.5) < threshold

    @staticmethod
    def percentage_increase_method(memory_usage, threshold=0.1):
        if len(memory_usage) < 3:
            return False
        initial, final = memory_usage[0], memory_usage[-1]
        return ((final - initial) / initial) > threshold
