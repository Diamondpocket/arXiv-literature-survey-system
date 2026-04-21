from __future__ import annotations

import argparse
import csv
import json
import mimetypes
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from ..metas.paths import runtime_dats_dir, runtime_outs_dir, runtime_uis_dir
from ..metas.workflows import STAGE_SEQUENCE, build_stage_entry


UIS_DIR = runtime_uis_dir()
ASSETS_DIR = UIS_DIR / "assets"
DASHBOARDS_DIR = UIS_DIR / "dashboards"
DATS_DIR = runtime_dats_dir()
OUTS_DIR = runtime_outs_dir()

RAWS_PATH = DATS_DIR / "raws" / "papers_raw.json"
CARDS_PATH = DATS_DIR / "cards" / "paper_cards.jsonl"
STATUS_PATH = OUTS_DIR / "stats" / "pipeline_status.json"
HISTORY_PATH = OUTS_DIR / "stats" / "pipeline_history.json"
TAXON_PATH = OUTS_DIR / "taxons" / "taxonomy.md"
TREND_PATH = OUTS_DIR / "trends" / "trend_analysis.md"
TABLE_PATH = OUTS_DIR / "tables" / "comparison_table.csv"
WEEKLY_PATH = OUTS_DIR / "digests" / "weekly_digest_latest.md"
WEEKLIES_DIR = OUTS_DIR / "digests" / "weeklies"


def read_json(path: Path) -> object:
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8").strip()
        return json.loads(text) if text else []
    except json.JSONDecodeError:
        return []


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def comparison_category_lookup(comparison: list[dict]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for row in comparison:
        title = str(row.get("title") or "").strip()
        category = str(row.get("category_bilingual") or row.get("category") or "").strip()
        if title and category:
            lookup[title] = category
    return lookup


def latest_weekly_files() -> list[dict]:
    if not WEEKLIES_DIR.exists():
        return []
    files = []
    for path in sorted(WEEKLIES_DIR.glob("*.md"), reverse=True):
        files.append({"name": path.name, "date": path.stem, "size": path.stat().st_size})
    return files


def read_pipeline_history() -> list[dict]:
    data = read_json(HISTORY_PATH)
    return data if isinstance(data, list) else []


def build_fallback_pipeline_status() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    stages = []
    for stage in STAGE_SEQUENCE:
        if stage["id"] == "fetch":
            artifact = RAWS_PATH
            detail = "Derived from existing raw paper file."
        elif stage["id"] == "cards":
            artifact = CARDS_PATH
            detail = "Derived from existing structured cards."
        elif stage["id"] == "analysis":
            artifact = TABLE_PATH
            detail = "Derived from current analysis artifacts."
        else:
            artifact = WEEKLY_PATH
            detail = "Derived from the latest weekly digest."
        completed = artifact.exists()
        stages.append(
            build_stage_entry(
                stage["id"],
                status="completed" if completed else "pending",
                detail=detail,
                progress_percent=100 if completed else 0,
            )
        )

    return {
        "run_id": None,
        "topic": "Retrieval-Augmented Generation, RAG",
        "status": "completed" if all(stage["status"] == "completed" for stage in stages) else "idle",
        "current_stage": None,
        "started_at": None,
        "updated_at": now,
        "finished_at": None,
        "message": "Monitoring is derived from current local files.",
        "recent_events": [],
        "recent_new_papers": [],
        "history_preview": read_pipeline_history()[:8],
        "stats": {"fetch": {}, "cards": {}, "analysis": {}, "weekly": {}},
        "stages": stages,
    }


def read_pipeline_status() -> dict:
    if not STATUS_PATH.exists():
        return build_fallback_pipeline_status()
    data = read_json(STATUS_PATH)
    if isinstance(data, dict) and isinstance(data.get("stages"), list):
        if "history_preview" not in data:
            data["history_preview"] = read_pipeline_history()[:8]
        return data
    return build_fallback_pipeline_status()


def api_summary() -> dict:
    papers = read_json(RAWS_PATH)
    cards = read_jsonl(CARDS_PATH)
    comparison = read_csv(TABLE_PATH)

    category_counts = Counter(row.get("category_bilingual") or row.get("category") or "unknown" for row in comparison)
    if not category_counts:
        category_counts = Counter(card.get("best_fit_category") or "unknown" for card in cards)
    innovation_counts = Counter(card.get("innovation_type") or "unknown" for card in cards)
    confidence_counts = Counter(card.get("confidence_level") or "unknown" for card in cards)
    model_counts = Counter(card.get("model") or "unknown" for card in cards)
    data_driven_counts = Counter(row.get("data_driven") or "unknown" for row in comparison)

    latest_generated = ""
    for card in cards:
        generated_at = str(card.get("generated_at") or "")
        if generated_at > latest_generated:
            latest_generated = generated_at

    latest_papers = []
    if isinstance(papers, list):
        for item in papers[:8]:
            if not isinstance(item, dict):
                continue
            latest_papers.append(
                {
                    "arxiv_id": item.get("arxiv_id", "unknown"),
                    "title": item.get("title", "unknown"),
                    "published": item.get("published", "unknown"),
                    "entry_url": item.get("entry_url") or f"https://arxiv.org/abs/{item.get('arxiv_id', 'unknown')}",
                }
            )

    return {
        "papers_count": len(papers) if isinstance(papers, list) else 0,
        "cards_count": len(cards),
        "comparison_rows": len(comparison),
        "category_counts": category_counts.most_common(),
        "innovation_counts": innovation_counts.most_common(),
        "confidence_counts": confidence_counts.most_common(),
        "model_counts": model_counts.most_common(),
        "data_driven_counts": data_driven_counts.most_common(),
        "latest_generated": latest_generated,
        "weekly_files": latest_weekly_files(),
        "latest_papers": latest_papers,
    }


def filter_cards(cards: list[dict], query: dict[str, list[str]], category_lookup: dict[str, str]) -> list[dict]:
    text = (query.get("q") or [""])[0].strip().lower()
    category = (query.get("category") or [""])[0].strip()
    confidence = (query.get("confidence") or [""])[0].strip()
    limit = int((query.get("limit") or ["200"])[0])

    filtered = []
    for card in cards:
        macro_category = category_lookup.get(str(card.get("title") or "").strip())
        if category and (macro_category or card.get("best_fit_category")) != category:
            continue
        if confidence and card.get("confidence_level") != confidence:
            continue
        if text:
            haystack = " ".join(
                str(card.get(key) or "")
                for key in [
                    "title",
                    "problem",
                    "key_idea",
                    "method",
                    "dataset_or_scenario",
                    "results_summary",
                    "limitations",
                    "summary",
                ]
            ).lower()
            if text not in haystack:
                continue
        enriched = dict(card)
        if macro_category:
            enriched["macro_category"] = macro_category
        filtered.append(enriched)
        if len(filtered) >= limit:
            break
    return filtered


class SurveyHandler(BaseHTTPRequestHandler):
    server_version = "SurveyDashboard/2.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_static(DASHBOARDS_DIR, "index.html")
            return
        if path.startswith("/api/"):
            self.send_api(path, parse_qs(parsed.query))
            return
        if path.startswith("/assets/"):
            self.send_static(ASSETS_DIR, path.removeprefix("/assets/"))
            return
        if path.startswith("/dashboards/"):
            self.send_static(DASHBOARDS_DIR, path.removeprefix("/dashboards/"))
            return
        if path.startswith("/viewers/"):
            self.send_static(UIS_DIR / "viewers", path.removeprefix("/viewers/"))
            return
        self.send_error(404, "Not found")

    def send_api(self, path: str, query: dict[str, list[str]]) -> None:
        if path == "/api/summary":
            self.send_json(api_summary())
        elif path == "/api/cards":
            comparison = read_csv(TABLE_PATH)
            self.send_json(filter_cards(read_jsonl(CARDS_PATH), query, comparison_category_lookup(comparison)))
        elif path == "/api/comparison":
            self.send_json(read_csv(TABLE_PATH))
        elif path == "/api/pipeline_status":
            self.send_json(read_pipeline_status())
        elif path == "/api/pipeline_history":
            self.send_json(read_pipeline_history())
        elif path == "/api/taxonomy":
            self.send_text(read_text(TAXON_PATH))
        elif path == "/api/trend":
            self.send_text(read_text(TREND_PATH))
        elif path == "/api/weekly":
            self.send_text(read_text(WEEKLY_PATH))
        else:
            self.send_error(404, "Unknown API endpoint")

    def send_static(self, base_dir: Path, relative_path: str) -> None:
        safe_path = (base_dir / relative_path).resolve()
        if base_dir.resolve() not in safe_path.parents and safe_path != base_dir.resolve():
            self.send_error(403, "Forbidden")
            return
        if safe_path.is_dir():
            safe_path = safe_path / "index.html"
        if not safe_path.exists():
            self.send_error(404, "Static file not found")
            return
        content_type = mimetypes.guess_type(safe_path.name)[0] or "application/octet-stream"
        payload = safe_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, data: object) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[dashboard] {self.address_string()} - {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local literature survey dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if not (DASHBOARDS_DIR / "index.html").exists():
        raise SystemExit("uis/dashboards/index.html not found")

    httpd = ThreadingHTTPServer((args.host, args.port), SurveyHandler)
    print(f"[dashboard] Dashboard: http://{args.host}:{args.port}")
    httpd.serve_forever()
