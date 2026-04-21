from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


if load_dotenv:
    load_dotenv()


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str) -> float | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    try:
        return float(value)
    except ValueError:
        print(f"[llm_client] Ignore invalid {name}={value!r}; expected a number.", file=sys.stderr)
        return None


def _temperature_fallback(exc: Exception) -> float | None:
    text = str(exc).lower()
    if "invalid temperature" not in text:
        return None
    match = re.search(r"only\s+([0-9]+(?:\.[0-9]+)?)\s+is\s+allowed", text)
    if match:
        return float(match.group(1))
    if "only 1" in text:
        return 1.0
    return None


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def loads_json_object(text: str) -> Dict[str, Any]:
    cleaned = _strip_json_fence(text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("LLM JSON response must be a JSON object.")
    return data


@dataclass
class LLMClient:
    """Small OpenAI-compatible client with deterministic mock fallback."""

    model: Optional[str] = None
    temperature: float = 0.0
    mock: Optional[bool] = None

    def __post_init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        requested_model = self.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        env_temperature = _env_float("LLM_TEMPERATURE")
        if env_temperature is not None:
            self.temperature = env_temperature

        force_mock = _env_flag("LLM_MOCK", default=False)
        if self.mock is None:
            self.mock = force_mock or not bool(self.api_key)

        self.last_call_used_mock = bool(self.mock)
        self._client = None

        if self.mock:
            self.model = requested_model if requested_model.startswith("mock:") else f"mock:{requested_model}"
            return

        try:
            from openai import OpenAI

            request_timeout = _env_float("LLM_REQUEST_TIMEOUT_SECONDS")
            max_retries = _env_float("OPENAI_MAX_RETRIES")
            kwargs: Dict[str, Any] = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            if request_timeout is not None:
                kwargs["timeout"] = request_timeout
            else:
                kwargs["timeout"] = 60.0
            if max_retries is not None:
                kwargs["max_retries"] = int(max_retries)
            self._client = OpenAI(**kwargs)
            self.model = requested_model
        except Exception as exc:  # pragma: no cover - environment dependent
            print(f"[llm_client] OpenAI client init failed; using mock mode: {exc}", file=sys.stderr)
            self.mock = True
            self.model = f"mock:{requested_model}"

    def chat_json(self, prompt: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a JSON object. Mock mode returns evidence-bounded placeholders."""
        if self.mock:
            self.last_call_used_mock = True
            return self._mock_card_json(input_data)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an evidence-grounded research extraction assistant. "
                    "Use only the supplied input. Do not invent datasets, metrics, results, or claims."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{prompt.strip()}\n\n"
                    "INPUT_JSON:\n"
                    f"{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\n"
                    "Return one valid JSON object only."
                ),
            },
        ]

        try:
            response = self._create_completion(messages, json_mode=True)
        except TypeError:
            response = self._create_completion(messages, json_mode=False)
        except Exception as exc:  # pragma: no cover - remote dependent
            if _env_flag("LLM_STRICT", default=False):
                raise
            print(f"[llm_client] LLM JSON call failed; using mock response: {exc}", file=sys.stderr)
            self.last_call_used_mock = True
            return self._mock_card_json(input_data)

        self.last_call_used_mock = False
        content = response.choices[0].message.content or "{}"
        try:
            return loads_json_object(content)
        except Exception as exc:
            if _env_flag("LLM_STRICT", default=False):
                raise
            print(f"[llm_client] Invalid JSON from LLM; using mock response: {exc}", file=sys.stderr)
            self.last_call_used_mock = True
            return self._mock_card_json(input_data)

    def chat_text(self, prompt: str, input_data: Dict[str, Any]) -> str:
        """Return Markdown/text. Mock mode returns an explicit placeholder."""
        if self.mock:
            self.last_call_used_mock = True
            topic = input_data.get("topic", "the selected topic")
            count = input_data.get("cards_count") or len(input_data.get("paper_cards", []))
            return (
                f"# Mock LLM Output\n\n"
                f"This placeholder was generated for `{topic}` from {count} structured cards. "
                "It proves the pipeline can run, but it is not suitable for final submission."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a careful scientific survey assistant. Base every claim on the "
                    "supplied structured inputs. Do not add external papers or facts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{prompt.strip()}\n\n"
                    "INPUT_JSON:\n"
                    f"{json.dumps(input_data, ensure_ascii=False, indent=2)}\n"
                ),
            },
        ]

        try:
            response = self._create_completion(messages, json_mode=False)
            self.last_call_used_mock = False
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover - remote dependent
            if _env_flag("LLM_STRICT", default=False):
                raise
            print(f"[llm_client] LLM text call failed; using mock response: {exc}", file=sys.stderr)
            self.last_call_used_mock = True
            topic = input_data.get("topic", "the selected topic")
            return (
                f"# Mock LLM Output After API Error\n\n"
                f"The text generation step for `{topic}` fell back to mock mode. "
                "Regenerate with a valid API key before final submission."
            )

    def _create_completion(self, messages: list[Dict[str, str]], json_mode: bool) -> Any:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            return self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            fallback_temperature = _temperature_fallback(exc)
            if fallback_temperature is None or fallback_temperature == self.temperature:
                raise
            print(
                f"[llm_client] Model rejected temperature={self.temperature}; "
                f"retrying with temperature={fallback_temperature}.",
                file=sys.stderr,
            )
            kwargs["temperature"] = fallback_temperature
            return self._client.chat.completions.create(**kwargs)

    def _mock_card_json(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        title = str(input_data.get("title") or "unknown")
        abstract = str(input_data.get("abstract") or input_data.get("summary") or "")
        sentences = _split_sentences(abstract)
        combined = f"{title} {abstract}"

        return {
            "title": title,
            "problem": _find_sentence(sentences, ["challenge", "problem", "issue", "difficulty", "hallucination"]),
            "key_idea": _find_sentence(sentences, ["propose", "present", "introduce", "develop", "we design"]),
            "method": _find_sentence(sentences, ["method", "framework", "pipeline", "retrieval", "rerank", "index"]),
            "dataset_or_scenario": _find_sentence(sentences, ["dataset", "benchmark", "corpus", "domain", "qa"]),
            "metrics": _find_sentence(sentences, ["accuracy", "f1", "recall", "precision", "mrr", "ndcg", "metric"]),
            "results_summary": _find_sentence(sentences, ["outperform", "improve", "achieve", "results", "experiments"]),
            "innovation_type": _infer_innovation_type(combined),
            "limitations": _find_sentence(sentences, ["limitation", "future work", "fail", "risk", "cost"]),
            "best_fit_category": _infer_category(combined),
            "confidence_level": "low",
        }


def _split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", compact) if part.strip()]


def _find_sentence(sentences: list[str], keywords: list[str]) -> str:
    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in keywords):
            return sentence[:700]
    return "not specified"


def _infer_category(text: str) -> str:
    lower = text.lower()
    rules = [
        ("Evaluation and Benchmarking", ["benchmark", "evaluate", "evaluation", "metric"]),
        ("Retrieval and Indexing", ["retrieval", "retriever", "index", "vector", "rerank"]),
        ("Knowledge Graph and Structured Knowledge", ["knowledge graph", "graph rag", "graph-based"]),
        ("Multimodal RAG", ["multimodal", "vision", "image", "video", "audio"]),
        ("Agentic and Tool-Augmented RAG", ["agent", "tool", "planning"]),
        ("Domain-Specific RAG", ["medical", "legal", "finance", "scientific", "clinical"]),
        ("Reliability, Safety, and Hallucination", ["hallucination", "faithful", "trust", "safety", "robust"]),
    ]
    for label, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return label
    return "General RAG Systems"


def _infer_innovation_type(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["survey", "review", "taxonomy"]):
        return "survey"
    if any(k in lower for k in ["benchmark", "dataset", "evaluation"]):
        return "benchmark_or_evaluation"
    if any(k in lower for k in ["framework", "architecture", "pipeline", "system"]):
        return "system_or_architecture"
    if any(k in lower for k in ["retriever", "rerank", "index", "chunk"]):
        return "retrieval_method"
    if any(k in lower for k in ["domain", "medical", "legal", "scientific", "clinical"]):
        return "application_or_domain_adaptation"
    return "not specified"
