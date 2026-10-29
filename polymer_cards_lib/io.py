"""Strict JSON input shared by live extraction and reproducible replay."""
from __future__ import annotations

import json
import math
from pathlib import Path


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid(value):
    raise ValueError("Non-finite JSON number")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        _invalid(value)
    return result


def parse_json(text):
    return json.loads(text, object_pairs_hook=_object, parse_constant=_invalid, parse_float=_float)


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))
