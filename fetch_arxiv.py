from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List


DEFAULT_QUERY = (
    'abs:"retrieval augmented generation" OR '
    'abs:"retrieval-augmented generation" OR '
    'ti:"retrieval augmented generation" OR '
    'ti:"retrieval-augmented generation"'
)

ProgressCallback = Callable[[Dict[str, Any]], None]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json_atomic(path: Path, data: Any) -> None:
    ensure_parent(path)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_existing_papers(path: Path, cutoff: datetime) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, list):
        return {}

    existing: Dict[str, Dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        arxiv_id = item.get("arxiv_id")
        published = parse_datetime(item.get("published"))
        if arxiv_id and (published is None or published >= cutoff):
            existing[str(arxiv_id)] = item
    return existing


def paper_to_dict(paper: Any) -> Dict[str, Any]:
    arxiv_id = paper.get_short_id()
    return {
        "arxiv_id": arxiv_id,
        "title": " ".join((paper.title or "").split()),
        "authors": [str(author) for author in paper.authors],
        "published": paper.published.isoformat() if paper.published else None,
        "updated": paper.updated.isoformat() if paper.updated else None,
        "summary": " ".join((paper.summary or "").split()),
        "categories": list(paper.categories or []),
        "pdf_url": paper.pdf_url,
        "entry_url": paper.entry_id or f"https://arxiv.org/abs/{arxiv_id}",
    }


def paper_preview(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "arxiv_id": item.get("arxiv_id", "unknown"),
        "title": item.get("title", "unknown"),
        "published": item.get("published", "unknown"),
        "entry_url": item.get("entry_url") or f"https://arxiv.org/abs/{item.get('arxiv_id', 'unknown')}",
        "pdf_url": item.get("pdf_url", ""),
        "categories": item.get("categories", []),
    }


def emit(progress_callback: ProgressCallback | None, payload: Dict[str, Any]) -> None:
    if progress_callback is None:
        return
    try:
        progress_callback(payload)
    except Exception as exc:  # pragma: no cover - progress reporting must not break the fetch
        print(f"[fetch_arxiv] Progress callback failed: {exc}", file=sys.stderr)


def fetch_papers(
    query: str = DEFAULT_QUERY,
    max_results: int = 100,
    years: int = 2,
    output_path: Path | str = Path("data/papers_raw.json"),
    progress_callback: ProgressCallback | None = None,
    return_report: bool = False,
) -> List[Dict[str, Any]] | tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Fetch recent arXiv papers, deduplicate by arxiv_id, and save metadata."""
    try:
        import arxiv
    except ImportError as exc:
        raise RuntimeError(
            "Package `arxiv` is not installed. Run `pip install -r requirements.txt` first."
        ) from exc

    output_path = Path(output_path)
    ensure_parent(output_path)
    cutoff = datetime.now(timezone.utc) - timedelta(days=365 * years)

    existing_before = load_existing_papers(output_path, cutoff)
    dedup = dict(existing_before)
    new_papers: List[Dict[str, Any]] = []
    fetched_count = 0
    skipped_old = 0

    emit(
        progress_callback,
        {
            "event": "start",
            "query": query,
            "max_results": max_results,
            "years": years,
            "cutoff": cutoff.isoformat(),
            "existing_in_window": len(existing_before),
            "message": "Started querying arXiv.",
        },
    )

    client = arxiv.Client(page_size=min(max_results, 100), delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    for paper in client.results(search):
        published = parse_datetime(paper.published)
        if published and published < cutoff:
            skipped_old += 1
            continue

        item = paper_to_dict(paper)
        arxiv_id = item["arxiv_id"]
        fetched_count += 1
        is_new = arxiv_id not in dedup
        if is_new:
            dedup[arxiv_id] = item
            new_papers.append(paper_preview(item))

        emit(
            progress_callback,
            {
                "event": "paper",
                "paper": paper_preview(item),
                "new": is_new,
                "fetched_count": fetched_count,
                "new_count": len(new_papers),
                "reused_count": max(fetched_count - len(new_papers), 0),
                "saved_count": len(dedup),
                "max_results": max_results,
                "message": (
                    f"Scanned {fetched_count}/{max_results} recent results; "
                    f"new={len(new_papers)}, existing={max(fetched_count - len(new_papers), 0)}."
                ),
                "new_papers_preview": new_papers[-10:],
            },
        )

    papers = sorted(dedup.values(), key=lambda row: row.get("published") or "", reverse=True)
    write_json_atomic(output_path, papers)

    report = {
        "query": query,
        "years": years,
        "max_results": max_results,
        "cutoff": cutoff.isoformat(),
        "existing_in_window_before": len(existing_before),
        "fetched_count": fetched_count,
        "saved_count": len(papers),
        "new_count": len(new_papers),
        "reused_count": max(fetched_count - len(new_papers), 0),
        "skipped_old_count": skipped_old,
        "new_papers_preview": new_papers[:20],
        "output_path": str(output_path),
    }

    emit(
        progress_callback,
        {
            "event": "complete",
            "report": report,
            "message": (
                f"Saved {len(papers)} unique papers. "
                f"New this run: {len(new_papers)}."
            ),
        },
    )

    if len(papers) < 50:
        print(
            f"[fetch_arxiv] Warning: only fetched {len(papers)} papers. "
            "Try increasing --max_results or broadening --query to satisfy the >=50 requirement.",
            file=sys.stderr,
        )
    print(
        f"[fetch_arxiv] Fetched {fetched_count} recent results; "
        f"saved {len(papers)} unique papers to {output_path}"
    )

    if return_report:
        return papers, report
    return papers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch recent RAG papers from arXiv.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="arXiv search query.")
    parser.add_argument("--max_results", type=int, default=100, help="Maximum arXiv results to request.")
    parser.add_argument("--years", type=int, default=2, help="Only keep papers from the last N years.")
    parser.add_argument("--output", default="data/papers_raw.json", help="Output JSON path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fetch_papers(
        query=args.query,
        max_results=args.max_results,
        years=args.years,
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()
