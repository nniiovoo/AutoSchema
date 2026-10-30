"""Live model calls using local AutoSchema configuration, without printing secrets."""
from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path

from polymer_cards_lib.io import parse_json
from polymer_cards_lib.prompt import (build_response_format, build_system_prompt,
                                     build_user_prompt, extraction_profile)


class ModelSetupError(ValueError):
    pass


class ModelRequestError(RuntimeError):
    pass


def create_client(env_file=None, request_timeout=300):
    if not isinstance(request_timeout, (int, float)) or isinstance(request_timeout, bool) or not 0 < request_timeout <= 900:
        raise ModelSetupError("Request timeout must be positive and at most900 seconds")
    root = Path(__file__).resolve().parents[1]
    paths = [Path(env_file)] if env_file else [root / ".env.local", root / ".env"]
    if env_file and not paths[0].is_file():
        raise ModelSetupError("The selected local environment file does not exist")
    try:
        from dotenv import load_dotenv
    except ImportError:
        if any(p.is_file() for p in paths):
            raise ModelSetupError("Install the project's python-dotenv dependency to load local configuration") from None
    else:
        for path in paths:
            if path.is_file():
                try:
                    load_dotenv(path, override=False)
                except Exception:
                    raise ModelSetupError("The selected local environment configuration could not be loaded") from None
    try:
        from prompt_lib.llm_client import load_config
        cfg = load_config()
    except Exception:
        raise ModelSetupError("The local model configuration could not be loaded; check its format") from None
    key = cfg.chat_api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ModelSetupError("No local model credential is configured; use the approved local key or --records for explicitly labeled replay")
    provider = cfg.provider
    if not os.getenv("LLM_PROVIDER") and os.getenv("OPENAI_API_KEY") and not cfg.chat_endpoint:
        provider = "openai"
    if provider not in {"openai", "azure_openai"}:
        raise ModelSetupError("Supported configured providers are openai and azure_openai")
    if provider == "azure_openai" and not cfg.chat_endpoint:
        raise ModelSetupError("Azure configuration requires CHAT_ENDPOINT")
    try:
        from openai import OpenAI, AzureOpenAI
    except ImportError:
        raise ModelSetupError("Install the openai dependency listed in requirements.txt for live extraction") from None
    try:
        if provider == "openai":
            client = OpenAI(api_key=key, timeout=request_timeout, max_retries=0)
            model = cfg.chat_model
        else:
            client = AzureOpenAI(api_key=key, azure_endpoint=cfg.chat_endpoint,
                                 api_version=cfg.chat_version, timeout=request_timeout, max_retries=0)
            model = cfg.chat_deployment
    except Exception:
        raise ModelSetupError("The configured model client could not be initialized; check local provider settings") from None
    return client, model, provider


def extract_document(client, model, document, max_output_tokens=10000):
    """One bounded request; no hidden model retries or raw provider errors in logs."""
    return _request(client, model, build_user_prompt(document), max_output_tokens)


def revise_document(client, model, document, previous_response, max_output_tokens=24000):
    """One new, explicit model revision from primary sources and prior proposals.

    No checked card is read and no earlier response is edited. The caller must
    preserve the prior run and label this as a revision, not a fresh extraction.
    """
    from polymer_cards_lib.repair import build_revision_user_prompt
    user_prompt = build_revision_user_prompt(document, previous_response)
    parsed, trace = _request(client, model, user_prompt, max_output_tokens)
    previous_bytes = json.dumps(previous_response, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":"), allow_nan=False).encode("utf-8")
    trace.update({"request_mode": "source_grounded_model_revision",
                  "previous_response_sha256": hashlib.sha256(previous_bytes).hexdigest()})
    return parsed, trace


def _request(client, model, user_prompt, max_output_tokens):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": build_system_prompt()},
                      {"role": "user", "content": user_prompt}],
            response_format=build_response_format(),
            max_completion_tokens=max_output_tokens,
        )
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        detail = f" (HTTP {status})" if isinstance(status, int) else ""
        failure = {"APITimeoutError": "Live model request timed out", "TimeoutError": "Live model request timed out",
                   "APIConnectionError": "Live model connection failed"}.get(type(exc).__name__, "Live model request failed")
        schema_hint = "; this workflow requires a model/deployment supporting strict JSON-schema output" if status == 400 else ""
        raise ModelRequestError(failure + detail + schema_hint + "; no provider error text was logged") from None
    if not getattr(response, "choices", None):
        raise ModelRequestError("Model returned no completion; no cards accepted")
    choice = response.choices[0]
    if getattr(choice, "finish_reason", None) == "length":
        raise ModelRequestError("Model response reached the output limit; no partial cards accepted")
    if getattr(choice, "finish_reason", None) != "stop":
        raise ModelRequestError("Model response did not finish normally; no partial cards accepted")
    if getattr(choice.message, "refusal", None):
        raise ModelRequestError("Model declined the extraction request; no cards accepted")
    raw_text = choice.message.content or ""
    try:
        parsed = parse_json(raw_text)
    except (ValueError, TypeError):
        raise ModelRequestError("Model returned invalid strict JSON; no fabricated or partial records accepted") from None
    usage = getattr(response, "usage", None)
    safe_usage = {name: getattr(usage, name, None) for name in ("prompt_tokens", "completion_tokens", "total_tokens")}
    return parsed, {"raw_response_text": raw_text, "usage": safe_usage,
                    "extraction_profile": extraction_profile(),
                    "request_prompt_sha256": hashlib.sha256(user_prompt.encode("utf-8")).hexdigest(),
                    "finish_reason": getattr(choice, "finish_reason", None)}
