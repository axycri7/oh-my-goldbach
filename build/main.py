r"""哥德巴赫猜想：有限范围的分解核验

题目要求证明：任一大于 2 的偶数都可以写成两个素数之和。本提交给出部分结果：
Euclid 引理、Bertrand 引理的证明，以及 [4, 200000] 上的可复现分解核验，
详见 build/hw-8.md。一般情形的配对引理尚未完成，本文件不声称完整证明。

本文件用 Eratosthenes 筛构造素性表，对 [4, 200000] 内每个偶数 n 寻找最小的
素数 p，使 n - p 也是素数，并复核 p、q 的素性与 p + q = n。任一偶数缺失
见证即以非零状态退出；全部见证逐行写入 SHA-256 证书，成功时输出 RESULT: PASS。

运行方式：

    python build/main.py
"""

from __future__ import annotations

import hashlib
import sys
import time

import sitecustomize  # noqa: F401  — local module

LIMIT = 200_000


def prime_sieve(limit: int) -> bytearray:
    """Build a sieve where flags[i] == 1 exactly when i is prime."""
    flags = bytearray(limit + 1)
    for value in range(2, limit + 1):
        flags[value] = 1
    factor = 2
    while factor * factor <= limit:
        if flags[factor]:
            start = factor * factor
            flags[start:limit + 1:factor] = b"\x00" * (((limit - start) // factor) + 1)
        factor += 1
    return flags


def find_decomposition(n: int, flags: bytearray) -> tuple[int, int] | None:
    """Return the smallest prime p for which n - p is also prime."""
    for p in range(2, n // 2 + 1):
        if flags[p] and flags[n - p]:
            return p, n - p
    return None


def format_witness(n: int, p: int, q: int) -> str:
    """Serialize one decomposition as it appears in the certificate."""
    return f"{n} = {p} + {q}"


def is_ordered_pair(n: int, p: int, q: int) -> bool:
    """Check ordering and the sum invariant; primality is checked by the caller."""
    return p >= 2 and q >= p and p + q == n


def verify_certificate(limit: int) -> tuple[int, int, str, str, str]:
    """Verify every even number up to limit and return certificate stats."""
    flags = prime_sieve(limit)
    digest = hashlib.sha256()
    checked = 0
    largest_prime = 0
    first = ""
    last = ""
    for n in range(4, limit + 1, 2):
        pair = find_decomposition(n, flags)
        if pair is None:
            raise SystemExit(f"missing witness for n = {n}")
        p, q = pair
        if not (flags[p] and flags[q] and is_ordered_pair(n, p, q)):
            raise SystemExit(f"invalid witness for n = {n}: {p} + {q}")
        line = format_witness(n, p, q)
        digest.update(line.encode("utf-8") + b"\n")
        checked += 1
        largest_prime = max(largest_prime, p, q)
        if not first:
            first = line
        last = line
    return checked, largest_prime, digest.hexdigest(), first, last


def main() -> int:
    started = time.perf_counter()
    checked, largest_prime, digest, first, last = verify_certificate(LIMIT)
    elapsed = time.perf_counter() - started
    print("Goldbach certificate")
    print(f"range: 4..{LIMIT} (even numbers)")
    print(f"verified decompositions: {checked}")
    print(f"largest prime used: {largest_prime}")
    print(f"certificate sha256: {digest}")
    print(f"first witness: {first}")
    print(f"last witness:  {last}")
    print(f"verification time: {elapsed:.3f}s")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
