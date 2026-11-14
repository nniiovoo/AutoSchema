"""Seed-snapshot text for the query-generation prompt.

The earlier code built the snapshot as ``json.dumps(all_seeds)[:8000]``. That
cut the JSON mid-string, and because the cut always fell at the end, the last
seeds (in alphabetical file order) silently lost most or all of their summary.
This helper drops empty values first and then gives every seed an equal share
of the character budget, marking any entry it has to shorten.
"""
from __future__ import annotations

import json
from typing import Any, Iterable, List

TRUNCATION_MARK = " ...[truncated]"


def _drop_empty(value: Any) -> Any:
    """Recursively remove None, empty strings and empty containers."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            v2 = _drop_empty(v)
            if v2 is None or v2 == "" or v2 == [] or v2 == {}:
                continue
            out[k] = v2
        return out
    if isinstance(value, list):
        items = [_drop_empty(v) for v in value]
        return [v for v in items if not (v is None or v == "" or v == [] or v == {})]
    return value


def compact_snapshot(extracted: Iterable[Any], budget: int = 8000) -> str:
    """Return one JSON line per seed snapshot, fitted into ``budget`` characters.

    Every seed keeps a share of the budget, so no seed is dropped entirely
    because of its position. Entries that exceed their share are shortened and
    end with ``TRUNCATION_MARK``.
    """
    entries: List[str] = [
        json.dumps(_drop_empty(e), ensure_ascii=False, separators=(",", ":"))
        for e in extracted
    ]
    if not entries:
        return ""
    joined = "\n".join(entries)
    if len(joined) <= budget:
        return joined

    # Equal share per entry; short entries hand their unused share to the rest.
    remaining = budget - (len(entries) - 1)          # newlines between entries
    order = sorted(range(len(entries)), key=lambda i: len(entries[i]))
    shares = [0] * len(entries)
    for pos, i in enumerate(order):
        fair = max(0, remaining // (len(entries) - pos))
        shares[i] = min(len(entries[i]), fair)
        remaining -= shares[i]

    fitted: List[str] = []
    for text, share in zip(entries, shares):
        if len(text) <= share:
            fitted.append(text)
        elif share > len(TRUNCATION_MARK):
            fitted.append(text[:share - len(TRUNCATION_MARK)] + TRUNCATION_MARK)
        else:
            fitted.append(text[:share])
    return "\n".join(fitted)
