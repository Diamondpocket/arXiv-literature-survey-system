from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from ..clients.llms import LLMClient
from ..metas.paths import CARD_PMTS_DIR, CARDS_DIR, RAWS_DIR


CARD_FIELDS = [
    "title",
    "problem",
    "key_idea",
    "method",
    "dataset_or_scenario",
    "metrics",
    "results_summary",
    "innovation_type",
    "limitations",
    "best_fit_category",
    "confidence_level",
]

UNKNOWN_VALUES = {"", "n/a", "na", "none", "null", "unknown.", "not mentioned"}
ProgressCallback = Callable[[Dict[str, Any]], None]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_jsonl_atomic(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    ensure_parent(path)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")
    temp_path.replace(path)


def load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list.")
    return data


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            print(f"[generate_cards] Skip invalid JSONL line {line_no} in {path}", file=sys.stderr)
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def emit(progress_callback: ProgressCallback | None, payload: Dict[str, Any]) -> None:
    if progress_callback is None:
        return
    try:
        progress_callback(payload)
    except Exception as exc:  # pragma: no cover - progress reporting must not break extraction
        print(f"[generate_cards] Progress callback failed: {exc}", file=sys.stderr)


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in UNKNOWN_VALUES or not value.strip()
    return False


def normalize_card(card: Dict[str, Any], paper: Dict[str, Any], model: str) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    missing_core = False

    for field in CARD_FIELDS:
        value = card.get(field)
        if is_missing(value):
            value = "unknown"
            missing_core = True
        normalized[field] = value

    normalized["title"] = paper.get("title") or normalized["title"] or "unknown"
    confidence = str(normalized.get("confidence_level", "low")).strip().lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    if missing_core:
        confidence = "low"
    normalized["confidence_level"] = confidence

    arxiv_id = paper.get("arxiv_id", "unknown")
    normalized.update(
        {
            "arxiv_id": arxiv_id,
            "source_url": paper.get("entry_url") or f"https://arxiv.org/abs/{arxiv_id}",
            "published": paper.get("published", "unknown"),
            "summary": paper.get("summary", ""),
            "evidence_source": "arxiv_abstract",
            "model": model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "authors": paper.get("authors", []),
            "categories": paper.get("categories", []),
            "pdf_url": paper.get("pdf_url", ""),
        }
    )
    return normalized


def card_preview(card: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "arxiv_id": card.get("arxiv_id", "unknown"),
        "title": card.get("title", "unknown"),
        "published": card.get("published", "unknown"),
        "confidence_level": card.get("confidence_level", "unknown"),
        "best_fit_category": card.get("best_fit_category", "unknown"),
    }


def generate_cards(
    raw_path: Path | str = RAWS_DIR / "papers_raw.json",
    cards_path: Path | str = CARDS_DIR / "paper_cards.jsonl",
    prompt_path: Path | str = CARD_PMTS_DIR / "card_extraction.txt",
    limit: int | None = None,
    batch_size: int = 1,
    progress_callback: ProgressCallback | None = None,
    return_report: bool = False,
) -> List[Dict[str, Any]] | tuple[List[Dict[str, Any]], Dict[str, Any]]:
    raw_path = Path(raw_path)
    cards_path = Path(cards_path)
    prompt_path = Path(prompt_path)

    papers = load_json(raw_path)
    existing_rows = read_jsonl(cards_path)
    existing_by_id: Dict[str, Dict[str, Any]] = {}
    for row in existing_rows:
        arxiv_id = row.get("arxiv_id")
        if arxiv_id and arxiv_id not in existing_by_id:
            existing_by_id[arxiv_id] = row

    prompt = prompt_path.read_text(encoding="utf-8")
    client = LLMClient(temperature=0.0)

    candidates = [paper for paper in papers if paper.get("arxiv_id") not in existing_by_id]
    if limit is not None:
        candidates = candidates[:limit]
    batch_size = max(1, batch_size)

    print(
        f"[generate_cards] Existing cards: {len(existing_by_id)}; "
        f"new papers to process: {len(candidates)}"
    )

    emit(
        progress_callback,
        {
            "event": "start",
            "existing_count": len(existing_by_id),
            "candidate_count": len(candidates),
            "batch_size": batch_size,
            "message": f"Preparing to generate {len(candidates)} new paper cards.",
        },
    )

    new_rows: List[Dict[str, Any]] = []
    recent_cards: List[Dict[str, Any]] = []
    processed = 0
    cursor = 0
    while cursor < len(candidates):
        batch = candidates[cursor : cursor + batch_size]
        cursor += batch_size

        if batch_size > 1 and len(batch) > 1 and not client.mock:
            try:
                batch_cards = generate_batch_cards(client, prompt, batch)
            except Exception as exc:
                print(f"[generate_cards] Batch failed; falling back to single-card calls: {exc}", file=sys.stderr)
                batch_cards = {}
        else:
            batch_cards = {}

        for paper in batch:
            processed += 1
            raw_card = batch_cards.get(str(paper.get("arxiv_id")))
            if raw_card is None:
                raw_card = generate_one_card(client, prompt, paper)
            model_used = client.model or "unknown"
            if client.last_call_used_mock and not model_used.startswith("mock:"):
                model_used = f"mock-fallback:{model_used}"
            normalized = normalize_card(raw_card, paper, model=model_used)
            arxiv_id = normalized.get("arxiv_id")
            if arxiv_id:
                existing_by_id[arxiv_id] = normalized
            new_rows.append(normalized)
            recent_cards.append(card_preview(normalized))
            recent_cards = recent_cards[-12:]
            write_jsonl_atomic(cards_path, existing_by_id.values())
            print(f"[generate_cards] ({processed}/{len(candidates)}) {paper.get('arxiv_id')} -> card")

            emit(
                progress_callback,
                {
                    "event": "card",
                    "processed_count": processed,
                    "candidate_count": len(candidates),
                    "generated_count": len(new_rows),
                    "card": card_preview(normalized),
                    "recent_cards_preview": recent_cards,
                    "message": f"Generated card {processed}/{len(candidates)}: {normalized.get('title', 'unknown')}",
                },
            )

    all_rows = list(existing_by_id.values())
    write_jsonl_atomic(cards_path, all_rows)

    report = {
        "existing_count_before": len(existing_rows),
        "candidate_count": len(candidates),
        "generated_count": len(new_rows),
        "total_cards_after": len(all_rows),
        "recent_cards_preview": recent_cards,
        "output_path": str(cards_path),
    }

    emit(
        progress_callback,
        {
            "event": "complete",
            "report": report,
            "message": f"Saved {len(all_rows)} cards. Newly generated this run: {len(new_rows)}.",
        },
    )

    print(f"[generate_cards] Saved {len(all_rows)} cards to {cards_path}")
    if return_report:
        return all_rows, report
    return all_rows


def generate_one_card(client: LLMClient, prompt: str, paper: Dict[str, Any]) -> Dict[str, Any]:
    input_data = {
        "arxiv_id": paper.get("arxiv_id"),
        "title": paper.get("title"),
        "abstract": paper.get("summary"),
        "published": paper.get("published"),
        "categories": paper.get("categories", []),
    }
    try:
        return client.chat_json(prompt, input_data)
    except Exception as exc:
        if os.getenv("LLM_STRICT", "").strip().lower() in {"1", "true", "yes", "y", "on"}:
            raise
        print(
            f"[generate_cards] Failed to generate card for {paper.get('arxiv_id')}: {exc}",
            file=sys.stderr,
        )
        return {}


def generate_batch_cards(
    client: LLMClient,
    single_prompt: str,
    papers: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    batch_prompt = (
        single_prompt
        + "\n\nYou will now receive multiple arXiv papers. Return exactly one JSON object with a key "
        "`cards`, whose value is an array. Create one card per input paper. Each card must include "
        "`arxiv_id` plus all required extraction fields. Use only each paper's own title and abstract. "
        "If evidence is missing, write unknown or not specified. Do not merge evidence across papers."
    )
    input_data = {
        "papers": [
            {
                "arxiv_id": paper.get("arxiv_id"),
                "title": paper.get("title"),
                "abstract": paper.get("summary"),
                "published": paper.get("published"),
                "categories": paper.get("categories", []),
            }
            for paper in papers
        ]
    }
    response = client.chat_json(batch_prompt, input_data)
    cards = response.get("cards")
    if not isinstance(cards, list):
        raise ValueError("batch response did not contain a cards array")

    by_id: Dict[str, Dict[str, Any]] = {}
    for item in cards:
        if not isinstance(item, dict):
            continue
        arxiv_id = str(item.get("arxiv_id") or "").strip()
        if arxiv_id:
            by_id[arxiv_id] = item
    if not by_id:
        raise ValueError("batch response contained no usable card objects")
    return by_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate structured JSONL cards for arXiv papers.")
    parser.add_argument("--raw_path", default=str(RAWS_DIR / "papers_raw.json"))
    parser.add_argument("--cards_path", default=str(CARDS_DIR / "paper_cards.jsonl"))
    parser.add_argument("--prompt_path", default=str(CARD_PMTS_DIR / "card_extraction.txt"))
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of new papers to process.")
    parser.add_argument("--batch_size", type=int, default=1, help="Number of papers per LLM extraction call.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_cards(
        raw_path=Path(args.raw_path),
        cards_path=Path(args.cards_path),
        prompt_path=Path(args.prompt_path),
        limit=args.limit,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
