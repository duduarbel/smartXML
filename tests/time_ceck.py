import atexit
import time
import functools
from collections import defaultdict
from typing import Callable, Any, TypeVar

ReturnType = TypeVar("ReturnType")


class TimingRegistry:
    def __init__(self) -> None:
        self._stats: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])

    # index 0 -> total time
    # index 1 -> call count

    def record(self, function_name: str, elapsed_seconds: float) -> None:
        stats = self._stats[function_name]
        stats[0] += elapsed_seconds
        stats[1] += 1.0

    def report(self, *, sort_by_total: bool = True) -> None:
        print("\n=== Timing Summary ===")
        print(f"{'Function':40} {'Calls':>8} {'Total(s)':>12} {'Avg(ms)':>12}")
        print("-" * 78)

        items = self._stats.items()
        if sort_by_total:
            items = sorted(items, key=lambda item: item[1][0], reverse=True)

        for function_name, (total_time, call_count) in items:
            avg_ms = (total_time / call_count) * 1000.0
            print(f"{function_name:40} {int(call_count):8d} {total_time:12.6f} {avg_ms:12.3f}")

    def clear(self) -> None:
        self._stats.clear()


timing_registry = TimingRegistry()


def timeit(func: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_seconds = time.perf_counter() - start_time
        timing_registry.record(func.__qualname__, elapsed_seconds)
        return result

    return wrapper


atexit.register(timing_registry.report)
