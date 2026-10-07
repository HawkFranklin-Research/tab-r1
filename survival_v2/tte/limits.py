"""Process resource limits (threads, memory) and device selection.

Mirrors paper/analysis/resource_limits.py (12 threads / 12 GB for local work) but is self-contained and relaxes the
address-space limit on CUDA, where the driver legitimately reserves a very large virtual range.
"""

from __future__ import annotations

import os
import resource
import sys
from contextlib import contextmanager
from typing import Iterator

THREAD_ENV_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                   "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")


def resolve_device(device: str) -> str:
    if device in ("cpu", "cuda"):
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:  # torch missing or broken: classical models still work
        return "cpu"


def configure(threads: int, memory_gb: int, device: str, allow_cpu_large: bool = True) -> str:
    """Apply ceilings and return the resolved device.

    ``TABR1_MAX_THREADS`` / ``TABR1_MAX_MEMORY_GB`` (the paper pipeline's variables) raise the ceilings on a cloud VM.
    ``memory_gb <= 0`` disables the address-space limit.
    """
    max_threads = int(os.environ.get("TABR1_MAX_THREADS", 12))
    max_memory = int(os.environ.get("TABR1_MAX_MEMORY_GB", 12))
    if not 1 <= threads <= max_threads:
        raise ValueError(f"threads must be in [1, {max_threads}] (raise TABR1_MAX_THREADS on a larger machine), got {threads}")
    if memory_gb > max_memory:
        raise ValueError(f"memory_gb must be <= {max_memory} (raise TABR1_MAX_MEMORY_GB on a larger machine), got {memory_gb}")
    for name in THREAD_ENV_VARS:
        os.environ[name] = str(threads)
    resolved = resolve_device(device)
    if allow_cpu_large:
        os.environ["TABPFN_ALLOW_CPU_LARGE_DATASET"] = "1"
    if memory_gb > 0 and resolved != "cuda":
        limit = memory_gb * 1024**3
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (limit if soft == resource.RLIM_INFINITY else min(soft, limit),
                                                limit if hard == resource.RLIM_INFINITY else min(hard, limit)))
    elif memory_gb > 0:
        print("note: CUDA device selected; address-space limit not applied", file=sys.stderr)
    return resolved


@contextmanager
def thread_limit(threads: int) -> Iterator[None]:
    try:
        from threadpoolctl import threadpool_limits
    except ImportError:
        yield
        return
    with threadpool_limits(limits=threads):
        yield


def clear_accelerator_cache() -> None:
    try:
        import gc

        gc.collect()
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        return
