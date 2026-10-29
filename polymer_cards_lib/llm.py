"""Live model calls using local AutoSchema configuration, without printing secrets."""
from __future__ import annotations

import os
from pathlib import Path

from polymer_cards_lib.io import parse_json
from polymer_cards_lib.prompt import build_system_prompt, build_user_prompt


class ModelSetupError(ValueError):
    pass


class ModelRequestError(RuntimeError):
    pass


def create_client(env_file=None):
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
            client = OpenAI(api_key=key, timeout=120, max_retries=0)
            model = cfg.chat_model
        else:
            client = AzureOpenAI(api_key=key, azure_endpoint=cfg.chat_endpoint,
                                 api_version=cfg.chat_version, timeout=120, max_retries=0)
            model = cfg.chat_deployment
    except Exception:
        raise ModelSetupError("The configured model client could not be initialized; check local provider settings") from None
    return client, model, provider


def extract_document(client, model, document, max_output_tokens=10000):
    """One bounded request; no hidden model retries or raw provider errors in logs."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": build_system_prompt()},
                      {"role": "user", "content": build_user_prompt(document)}],
            response_format={"type": "json_object"},
            max_completion_tokens=max_output_tokens,
        )
    except Exception as exc:
        status = getattr(exc, "status_code", None)
        detail = f" (HTTP {status})" if isinstance(status, int) else ""
        raise ModelRequestError("Live model request failed" + detail + "; no provider error text was logged") from None
    choice = response.choices[0]
    if getattr(choice, "finish_reason", None) == "length":
        raise ModelRequestError("Model response reached the output limit; no partial cards accepted")
    raw_text = choice.message.content or ""
    try:
        parsed = parse_json(raw_text)
    except (ValueError, TypeError):
        raise ModelRequestError("Model returned invalid strict JSON; no fabricated or partial records accepted") from None
    usage = getattr(response, "usage", None)
    safe_usage = {name: getattr(usage, name, None) for name in ("prompt_tokens", "completion_tokens", "total_tokens")}
    return parsed, {"raw_response_text": raw_text, "usage": safe_usage,
                    "finish_reason": getattr(choice, "finish_reason", None)}
