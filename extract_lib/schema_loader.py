from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class SchemaField:
    name: str
    description: str
    value_type: str            # "string" | "array" | "enum" | (fallback) "string"
    scope: str                 # "subdomain" | "global" | ...
    aliases: List[str] = field(default_factory=list)
    member_field_names: List[str] = field(default_factory=list)
    evidence_snippets: List[str] = field(default_factory=list)

    def is_array(self) -> bool:
        return self.value_type.lower() == "array"

    def is_multi_valued(self) -> bool:
        return self.value_type.lower() in {"array", "enum"}

    def all_search_terms(self) -> List[str]:
        pool: List[str] = []
        seen = set()
        candidates = [self.name] + list(self.aliases) + list(self.member_field_names)
        for raw in candidates:
            if not raw:
                continue
            for variant in (raw, raw.replace("_", " "), raw.replace("_", "-")):
                v = variant.strip().lower()
                if v and v not in seen:
                    seen.add(v)
                    pool.append(v)
        return pool

def _str_list(value) -> List[str]:
    return [str(v) for v in (value or []) if isinstance(v, (str, int, float)) and str(v).strip()]


def load_schema(schema_path: Path) -> List[SchemaField]:
    """Read final_schema.json (list of fields OR dict with 'fields' key).

    Accepts both key conventions:
      * Phase II style: aliases / member_field_names / evidence_snippets / value_type
      * Phase I output (schema_lib): evidence_examples / merged_from, no value_type
    Phase I schemas used to load with no evidence snippets, no member names and
    value_type "string", so passage retrieval matched on the field name alone
    and every field was cut to a single value. A field with no ``value_type``
    key now loads as "array" (multi-valued, as the paper describes); an
    explicit ``value_type`` is always respected.
    """
    obj = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    if isinstance(obj, list):
        raw_fields = obj
    elif isinstance(obj, dict) and "fields" in obj:
        raw_fields = obj["fields"]
    else:
        raise ValueError(f"Unsupported schema format in {schema_path}")

    out: List[SchemaField] = []
    for f in raw_fields:
        if not isinstance(f, dict) or "name" not in f:
            continue
        if "value_type" in f:
            value_type = str(f.get("value_type") or "string")
        else:
            value_type = "array"
        out.append(
            SchemaField(
                name=str(f["name"]),
                description=str(f.get("description", "") or ""),
                value_type=value_type,
                scope=str(f.get("scope", "") or ""),
                aliases=_str_list(f.get("aliases")),
                member_field_names=_str_list(
                    f.get("member_field_names") or f.get("merged_from")),
                evidence_snippets=_str_list(
                    f.get("evidence_snippets") or f.get("evidence_examples")),
            )
        )
    return out

def schema_field_names(fields: List[SchemaField]) -> List[str]:
    return [f.name for f in fields]
