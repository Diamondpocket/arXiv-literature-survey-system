from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List

from ..analyses.clusters import run_analysis
from ..analyses.weeklies import generate_weekly_digest
from ..cards.generators import generate_cards
from ..fetchers.arxivs import DEFAULT_QUERY, fetch_papers
from ..metas.paths import CARD_PMTS_DIR, CARDS_DIR, DIGEST_PMTS_DIR, DIGESTS_DIR, OUTS_DIR, RAWS_DIR, STATS_DIR, TAXON_PMTS_DIR, WEEKLIES_DIR
from ..metas.workflows import build_initial_stage_entries


STATUS_PATH = STATS_DIR / "pipeline_status.json"
HISTORY_PATH = STATS_DIR / "pipeline_history.json"
MAX_EVENTS = 36
MAX_HISTORY = 24
MAX_NEW_PAPERS = 20


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_layout() -> None:
    RAWS_DIR.mkdir(parents=True, exist_ok=True)
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    WEEKLIES_DIR.mkdir(parents=True, exist_ok=True)


def write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def read_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        text = path.read_text(encoding="utf-8").strip()
        return json.loads(text) if text else default
    except json.JSONDecodeError:
        return default


def count_json_list(path: Path) -> int:
    data = read_json_file(path, [])
    return len(data) if isinstance(data, list) else 0


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        return max(sum(1 for _ in f) - 1, 0)


def build_status(args: argparse.Namespace) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "run_id": run_id,
        "topic": args.topic,
        "query": args.query,
        "max_results": args.max_results,
        "years": args.years,
        "status": "idle",
        "current_stage": None,
        "started_at": None,
        "updated_at": iso_now(),
        "finished_at": None,
        "message": "Waiting to start pipeline.",
        "recent_events": [],
        "recent_new_papers": [],
        "history_preview": read_history()[:8],
        "stats": {
            "fetch": {},
            "cards": {},
            "analysis": {},
            "weekly": {},
        },
        "stages": build_initial_stage_entries(),
    }


def read_history() -> List[dict]:
    data = read_json_file(HISTORY_PATH, [])
    return data if isinstance(data, list) else []


def write_history(history: List[dict]) -> None:
    write_json_atomic(HISTORY_PATH, history[:MAX_HISTORY])


def write_status(status: dict) -> None:
    status["history_preview"] = read_history()[:8]
    write_json_atomic(STATUS_PATH, status)


def find_stage(status: dict, stage_id: str) -> dict | None:
    for stage in status["stages"]:
        if stage["id"] == stage_id:
            return stage
    return None


def append_event(status: dict, stage_id: str, message: str, payload: dict | None = None) -> None:
    stage = find_stage(status, stage_id)
    event = {
        "time": iso_now(),
        "stage_id": stage_id,
        "stage_label_zh": stage["label_zh"] if stage else stage_id,
        "stage_label_en": stage["label_en"] if stage else stage_id,
        "message": message,
        "payload": payload or {},
    }
    status["recent_events"] = [event] + list(status.get("recent_events", []))
    status["recent_events"] = status["recent_events"][:MAX_EVENTS]
    status["updated_at"] = event["time"]
    write_status(status)


def set_pipeline_status(status: dict, *, state: str, current_stage: str | None, message: str) -> None:
    status["status"] = state
    status["current_stage"] = current_stage
    status["message"] = message
    status["updated_at"] = iso_now()
    if state == "running" and not status.get("started_at"):
        status["started_at"] = status["updated_at"]
    if state in {"completed", "failed"}:
        status["finished_at"] = status["updated_at"]
    write_status(status)


def set_stage_progress(
    status: dict,
    stage_id: str,
    *,
    current: int | None = None,
    total: int | None = None,
    detail: str | None = None,
) -> None:
    stage = find_stage(status, stage_id)
    if stage is None:
        return
    if current is not None:
        stage["progress_current"] = current
    if total is not None:
        stage["progress_total"] = total

    total_value = stage.get("progress_total")
    current_value = stage.get("progress_current") or 0
    if isinstance(total_value, int) and total_value > 0:
        stage["progress_percent"] = min(100, round(current_value * 100 / total_value))
    elif stage.get("status") == "completed":
        stage["progress_percent"] = 100
    else:
        stage["progress_percent"] = 0

    if detail is not None:
        stage["detail"] = detail
    status["updated_at"] = iso_now()
    write_status(status)


def mark_stage(
    status: dict,
    stage_id: str,
    stage_state: str,
    detail: str = "",
    *,
    current: int | None = None,
    total: int | None = None,
) -> None:
    now = iso_now()
    stage = find_stage(status, stage_id)
    if stage is None:
        return

    stage["status"] = stage_state
    if detail:
        stage["detail"] = detail
    if current is not None:
        stage["progress_current"] = current
    if total is not None:
        stage["progress_total"] = total

    if stage_state == "running":
        stage["started_at"] = now
        stage["finished_at"] = None
    elif stage_state in {"completed", "failed", "skipped"}:
        if not stage["started_at"]:
            stage["started_at"] = now
        stage["finished_at"] = now
        if stage_state == "completed":
            stage["progress_percent"] = 100
            if stage["progress_total"] is not None:
                stage["progress_current"] = stage["progress_total"]
        elif stage_state == "skipped":
            stage["progress_percent"] = 0

    status["updated_at"] = now
    write_status(status)


def set_stage_stats(status: dict, stage_id: str, stats: dict) -> None:
    status["stats"][stage_id] = stats
    status["updated_at"] = iso_now()
    write_status(status)


def append_history_entry(status: dict) -> None:
    entry = {
        "run_id": status.get("run_id"),
        "topic": status.get("topic"),
        "query": status.get("query"),
        "max_results": status.get("max_results"),
        "years": status.get("years"),
        "status": status.get("status"),
        "message": status.get("message"),
        "started_at": status.get("started_at"),
        "finished_at": status.get("finished_at"),
        "updated_at": status.get("updated_at"),
        "fetch_stats": status.get("stats", {}).get("fetch", {}),
        "cards_stats": status.get("stats", {}).get("cards", {}),
        "analysis_stats": status.get("stats", {}).get("analysis", {}),
        "weekly_stats": status.get("stats", {}).get("weekly", {}),
        "recent_new_papers": list(status.get("recent_new_papers", []))[:10],
        "stage_statuses": [
            {
                "id": stage.get("id"),
                "label_zh": stage.get("label_zh"),
                "label_en": stage.get("label_en"),
                "status": stage.get("status"),
                "detail": stage.get("detail"),
                "started_at": stage.get("started_at"),
                "finished_at": stage.get("finished_at"),
                "progress_current": stage.get("progress_current"),
                "progress_total": stage.get("progress_total"),
                "progress_percent": stage.get("progress_percent"),
            }
            for stage in status.get("stages", [])
        ],
    }
    history = [entry] + [item for item in read_history() if item.get("run_id") != entry["run_id"]]
    write_history(history)
    status["history_preview"] = history[:8]
    write_status(status)


def fetch_progress_handler(status: dict) -> Callable[[dict], None]:
    def handle(payload: dict) -> None:
        event = payload.get("event")
        if event == "start":
            total_hint = payload.get("max_results")
            set_stage_progress(
                status,
                "fetch",
                current=0,
                total=total_hint if isinstance(total_hint, int) else None,
                detail="开始从 arXiv 拉取近两年的论文元数据。",
            )
            append_event(status, "fetch", payload.get("message", "Started fetching from arXiv."), payload)
            return

        if event == "paper":
            current = int(payload.get("fetched_count") or 0)
            total = payload.get("max_results")
            new_count = int(payload.get("new_count") or 0)
            reused_count = int(payload.get("reused_count") or 0)
            detail = f"已扫描 {current}/{total} 篇候选论文；新增 {new_count}，已有 {reused_count}。"
            set_stage_progress(
                status,
                "fetch",
                current=current,
                total=total if isinstance(total, int) else None,
                detail=detail,
            )
            if payload.get("new"):
                status["recent_new_papers"] = list(payload.get("new_papers_preview", []))[-MAX_NEW_PAPERS:]
                append_event(
                    status,
                    "fetch",
                    f"发现新论文：{payload.get('paper', {}).get('title', 'unknown')}",
                    payload.get("paper"),
                )
            elif current <= 3 or current % 10 == 0:
                append_event(status, "fetch", detail, {"checkpoint": True})
            return

        if event == "complete":
            report = payload.get("report", {})
            set_stage_stats(status, "fetch", report)
            status["recent_new_papers"] = list(report.get("new_papers_preview", []))[:MAX_NEW_PAPERS]
            detail = f"抓取完成：保留 {report.get('saved_count', 0)} 篇，本轮新增 {report.get('new_count', 0)} 篇。"
            set_stage_progress(
                status,
                "fetch",
                current=report.get("fetched_count"),
                total=report.get("max_results"),
                detail=detail,
            )
            append_event(status, "fetch", payload.get("message", detail), report)

    return handle


def cards_progress_handler(status: dict) -> Callable[[dict], None]:
    def handle(payload: dict) -> None:
        event = payload.get("event")
        if event == "start":
            candidate_count = int(payload.get("candidate_count") or 0)
            detail = f"准备处理 {candidate_count} 篇新增论文并生成结构化卡片。"
            set_stage_progress(status, "cards", current=0, total=candidate_count, detail=detail)
            append_event(status, "cards", payload.get("message", detail), payload)
            return

        if event == "card":
            processed = int(payload.get("processed_count") or 0)
            total = int(payload.get("candidate_count") or 0)
            card = payload.get("card", {})
            detail = f"已生成 {processed}/{total} 张新卡片。"
            set_stage_progress(status, "cards", current=processed, total=total, detail=detail)
            append_event(status, "cards", f"卡片生成完成：{card.get('title', 'unknown')}", card)
            return

        if event == "complete":
            report = payload.get("report", {})
            set_stage_stats(status, "cards", report)
            detail = f"结构化卡片已更新：总计 {report.get('total_cards_after', 0)} 张，本轮新增 {report.get('generated_count', 0)} 张。"
            set_stage_progress(
                status,
                "cards",
                current=report.get("candidate_count"),
                total=report.get("candidate_count"),
                detail=detail,
            )
            append_event(status, "cards", payload.get("message", detail), report)

    return handle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full arXiv weekly survey pipeline.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="arXiv query.")
    parser.add_argument("--max_results", type=int, default=100, help="Maximum arXiv results.")
    parser.add_argument("--years", type=int, default=2, help="Recent time window in years.")
    parser.add_argument("--topic", default="Retrieval-Augmented Generation, RAG", help="Survey topic label.")
    parser.add_argument(
        "--skip_fetch",
        action="store_true",
        help="Skip arXiv fetching and reuse dats/raws/papers_raw.json. Useful for local smoke tests.",
    )
    parser.add_argument(
        "--card_limit",
        type=int,
        default=None,
        help="Optional limit for newly generated cards. Leave unset for the full pipeline.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Number of papers per LLM extraction call. Use 3-5 for faster full runs.",
    )
    parser.add_argument(
        "--no_llm_taxonomy",
        action="store_true",
        help="Skip optional LLM taxonomy synthesis and use deterministic statistics.",
    )
    parser.add_argument(
        "--no_llm_weekly",
        action="store_true",
        help="Skip LLM weekly digest synthesis and use deterministic template output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_layout()
    status = build_status(args)
    write_status(status)
    set_pipeline_status(
        status,
        state="running",
        current_stage="fetch",
        message="Starting literature survey pipeline.",
    )

    raw_path = RAWS_DIR / "papers_raw.json"
    cards_path = CARDS_DIR / "paper_cards.jsonl"

    try:
        if not args.skip_fetch:
            mark_stage(
                status,
                "fetch",
                "running",
                f"Querying arXiv with max_results={args.max_results}.",
                current=0,
                total=args.max_results,
            )
            try:
                papers, fetch_report = fetch_papers(
                    query=args.query,
                    max_results=args.max_results,
                    years=args.years,
                    output_path=raw_path,
                    progress_callback=fetch_progress_handler(status),
                    return_report=True,
                )
                set_stage_stats(status, "fetch", fetch_report)
                mark_stage(
                    status,
                    "fetch",
                    "completed",
                    f"Saved {len(papers)} recent raw papers; new this run: {fetch_report.get('new_count', 0)}.",
                    current=fetch_report.get("fetched_count"),
                    total=fetch_report.get("max_results"),
                )
            except Exception as exc:
                if raw_path.exists():
                    reused_count = count_json_list(raw_path)
                    detail = f"Fetch failed but reused existing raw data: {exc}"
                    print(
                        f"[run_pipeline] Fetch failed, but existing {raw_path} will be reused: {exc}",
                        file=sys.stderr,
                    )
                    set_stage_stats(
                        status,
                        "fetch",
                        {
                            "query": args.query,
                            "years": args.years,
                            "max_results": args.max_results,
                            "saved_count": reused_count,
                            "new_count": 0,
                            "reused_count": reused_count,
                            "reused_existing_file": True,
                        },
                    )
                    mark_stage(status, "fetch", "completed", detail, current=0, total=args.max_results)
                    append_event(status, "fetch", detail, {"error": str(exc)})
                else:
                    mark_stage(status, "fetch", "failed", str(exc), current=0, total=args.max_results)
                    raise
        else:
            if not raw_path.exists():
                raw_path.write_text("[]\n", encoding="utf-8")
            reused_count = count_json_list(raw_path)
            print(f"[run_pipeline] Skipping fetch; using {raw_path}")
            set_stage_stats(
                status,
                "fetch",
                {
                    "query": args.query,
                    "years": args.years,
                    "max_results": args.max_results,
                    "saved_count": reused_count,
                    "new_count": 0,
                    "reused_count": reused_count,
                    "skipped": True,
                },
            )
            mark_stage(status, "fetch", "skipped", f"Reused existing file: {raw_path.name}", current=0, total=args.max_results)
            append_event(status, "fetch", f"Skipped fetch and reused {raw_path.name}.", {"saved_count": reused_count})

        set_pipeline_status(
            status,
            state="running",
            current_stage="cards",
            message="Generating or reusing structured paper cards.",
        )
        mark_stage(status, "cards", "running", f"Batch size={args.batch_size}.", current=0, total=0)
        cards, cards_report = generate_cards(
            raw_path=raw_path,
            cards_path=cards_path,
            prompt_path=CARD_PMTS_DIR / "card_extraction.txt",
            limit=args.card_limit,
            batch_size=args.batch_size,
            progress_callback=cards_progress_handler(status),
            return_report=True,
        )
        set_stage_stats(status, "cards", cards_report)
        mark_stage(
            status,
            "cards",
            "completed",
            f"Structured cards available: {len(cards)}. Newly generated: {cards_report.get('generated_count', 0)}.",
            current=cards_report.get("candidate_count"),
            total=cards_report.get("candidate_count"),
        )

        set_pipeline_status(
            status,
            state="running",
            current_stage="analysis",
            message="Building taxonomy, comparison table, and trend analysis.",
        )
        mark_stage(
            status,
            "analysis",
            "running",
            "Generating taxonomy.md, comparison_table.csv, and trend_analysis.md.",
            current=0,
            total=3,
        )
        append_event(status, "analysis", "Started cluster analysis and artifact generation.", {})
        run_analysis(
            cards_path=cards_path,
            outputs_dir=OUTS_DIR,
            taxonomy_prompt_path=TAXON_PMTS_DIR / "taxonomy_generation.txt",
            use_llm_taxonomy=not args.no_llm_taxonomy,
        )
        analysis_stats = {
            "taxonomy_path": str(OUTS_DIR / "taxons" / "taxonomy.md"),
            "comparison_path": str(OUTS_DIR / "tables" / "comparison_table.csv"),
            "trend_path": str(OUTS_DIR / "trends" / "trend_analysis.md"),
            "comparison_rows": count_csv_rows(OUTS_DIR / "tables" / "comparison_table.csv"),
        }
        set_stage_stats(status, "analysis", analysis_stats)
        mark_stage(
            status,
            "analysis",
            "completed",
            "Analysis artifacts refreshed in outs/.",
            current=3,
            total=3,
        )
        append_event(status, "analysis", "Updated taxonomy, comparison table, and trend analysis.", analysis_stats)

        set_pipeline_status(
            status,
            state="running",
            current_stage="weekly",
            message="Generating the latest weekly digest.",
        )
        mark_stage(status, "weekly", "running", "Writing weekly_digest_latest.md and weekly archive.", current=0, total=1)
        append_event(status, "weekly", "Started weekly digest generation.", {})
        digest = generate_weekly_digest(
            cards_path=cards_path,
            outputs_dir=OUTS_DIR,
            prompt_path=DIGEST_PMTS_DIR / "weekly_digest.txt",
            topic=args.topic,
            force_deterministic=args.no_llm_weekly,
        )
        today = datetime.now().date().isoformat()
        weekly_stats = {
            "latest_path": str(DIGESTS_DIR / "weekly_digest_latest.md"),
            "archive_path": str(WEEKLIES_DIR / f"{today}.md"),
            "digest_chars": len(digest),
        }
        set_stage_stats(status, "weekly", weekly_stats)
        mark_stage(status, "weekly", "completed", "Weekly digest generated successfully.", current=1, total=1)
        append_event(status, "weekly", "Weekly digest written to latest and dated archive.", weekly_stats)

        set_pipeline_status(
            status,
            state="completed",
            current_stage=None,
            message="Pipeline finished successfully.",
        )
        append_history_entry(status)
        print("[run_pipeline] Pipeline finished.")
    except Exception as exc:
        current_stage = status.get("current_stage")
        if current_stage:
            mark_stage(status, current_stage, "failed", str(exc))
            append_event(status, current_stage, f"Stage failed: {exc}", {"error": str(exc)})
        set_pipeline_status(
            status,
            state="failed",
            current_stage=current_stage,
            message=f"Pipeline failed: {exc}",
        )
        append_history_entry(status)
        raise


if __name__ == "__main__":
    main()
