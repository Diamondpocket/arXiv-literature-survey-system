from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..clients.llms import LLMClient
from ..metas.paths import CARDS_DIR, DIGEST_PMTS_DIR, DIGESTS_DIR, TABLES_DIR, TAXONS_DIR, TRENDS_DIR, WEEKLIES_DIR


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            rows.append(item)
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_csv_rows(path: Path, limit: int | None = None) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows if limit is None else rows[:limit]


def clean(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    text = " ".join(str(value).split())
    return text or default


def truncate(text: str, max_chars: int = 12000) -> str:
    return text if len(text) <= max_chars else text[: max_chars - 100].rstrip() + "\n\n[truncated]\n"


def category_lookup_from_comparison(comparison_rows: List[Dict[str, str]]) -> Dict[str, str]:
    return {
        clean(row.get("title")): clean(row.get("category_bilingual") or row.get("category"))
        for row in comparison_rows
        if clean(row.get("title"), "") and clean(row.get("category_bilingual") or row.get("category"), "")
    }


def card_category(card: Dict[str, Any], lookup: Dict[str, str] | None = None) -> str:
    title = clean(card.get("title"))
    if lookup and title in lookup:
        return lookup[title]
    return clean(card.get("best_fit_category"))


def compact_cards(
    cards: List[Dict[str, Any]],
    comparison_lookup: Dict[str, str] | None = None,
    limit: int = 80,
) -> List[Dict[str, str]]:
    sorted_cards = sorted(cards, key=lambda c: clean(c.get("published"), ""), reverse=True)
    compacted: List[Dict[str, str]] = []
    for card in sorted_cards[:limit]:
        compacted.append(
            {
                "arxiv_id": clean(card.get("arxiv_id")),
                "title": clean(card.get("title")),
                "published": clean(card.get("published")),
                "category": card_category(card, comparison_lookup),
                "source_category": clean(card.get("best_fit_category")),
                "innovation_type": clean(card.get("innovation_type")),
                "problem": clean(card.get("problem")),
                "key_idea": clean(card.get("key_idea")),
                "method": clean(card.get("method")),
                "dataset_or_scenario": clean(card.get("dataset_or_scenario")),
                "metrics": clean(card.get("metrics")),
                "results_summary": clean(card.get("results_summary")),
                "limitations": clean(card.get("limitations")),
                "confidence_level": clean(card.get("confidence_level")),
            }
        )
    return compacted


def deterministic_digest(
    cards: List[Dict[str, Any]],
    comparison_rows: List[Dict[str, str]],
    topic: str,
    today: str,
    mock_notice: bool = False,
) -> str:
    comparison_lookup = category_lookup_from_comparison(comparison_rows)
    category_counts = Counter(
        clean(row.get("category_bilingual") or row.get("category"))
        for row in comparison_rows
        if clean(row.get("category_bilingual") or row.get("category"), "")
    )
    if not category_counts:
        category_counts = Counter(card_category(card, comparison_lookup) for card in cards)
    innovation_counts = Counter(clean(card.get("innovation_type")) for card in cards)
    latest = sorted(cards, key=lambda c: clean(c.get("published"), ""), reverse=True)[:5]

    lines = [
        f"# 每周文献综述 Weekly Survey Digest - {topic}",
        "",
        f"Date / 日期: {today}",
        f"Evidence base / 证据基础: {len(cards)} structured arXiv paper cards / {len(cards)} 张结构化 arXiv 论文卡片。",
    ]
    if mock_notice:
        lines.append("Notice: generated in mock mode. Regenerate with a real LLM API before final submission.")

    lines.extend(
        [
            "",
            "## 本周概览 Weekly Overview",
            f"本次周报基于已留存的 JSON 卡片生成，覆盖 {len(cards)} 篇论文。最新样本包括：",
        ]
    )
    if latest:
        for card in latest:
            lines.append(
                f"- {clean(card.get('title'))} ({clean(card.get('published'))[:10]}, {card_category(card, comparison_lookup)})"
            )
    else:
        lines.append("- 暂无论文卡片。请先运行抓取与卡片生成步骤。")

    lines.extend(["", "## 分类体系摘要 Taxonomy Summary"])
    if category_counts:
        for category, count in category_counts.most_common(6):
            lines.append(f"- {category}: {count} 篇。")
    else:
        lines.append("- 暂无分类。")

    lines.extend(["", "## 方法对比摘要 Method Comparison"])
    for row in comparison_rows[:8]:
        lines.append(
            f"- {clean(row.get('title'))}: 方法={clean(row.get('method'))}; "
            f"复杂度={clean(row.get('complexity'))}; 场景={clean(row.get('scenario'))}; "
            f"数据驱动={clean(row.get('data_driven'))}。"
        )
    if not comparison_rows:
        lines.append("- 暂无对比表条目。")

    top_innovation = innovation_counts.most_common(1)[0][0] if innovation_counts else "unknown"
    lines.extend(
        [
            "",
            "## 趋势分析 Trend Analysis",
            f"当前最常见的创新类型是 **{top_innovation}**。结合结构化卡片，RAG 研究正从通用流水线转向评测、领域化、结构化知识、多模态与可靠性等更细粒度方向。",
            "",
            "## 研究空白与未来方向 Research Gaps and Future Directions",
            "- 仅靠摘要很难统一比较数据集、指标、成本和失败模式，后续可对代表性论文补充全文级证据。",
            "- 未来综述应把 RAG 拆成检索、重排、生成、校验和运行治理五个环节分别评估，而不是只比较最终回答质量。",
            "- 原创判断：更有价值的 RAG 系统不只是“检索更多”，而是能判断何时不检索、何时压缩证据、何时触发外部工具，以及何时拒答。",
            "",
            "## 证据来源 Provenance",
            "- This digest is generated from `paper_cards.jsonl`, `taxonomy.md`, `comparison_table.csv`, and `trend_analysis.md`.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_weekly_digest(
    cards_path: Path | str = CARDS_DIR / "paper_cards.jsonl",
    outputs_dir: Path | str = Path(DIGESTS_DIR).parent,
    prompt_path: Path | str = DIGEST_PMTS_DIR / "weekly_digest.txt",
    topic: str = "Retrieval-Augmented Generation, RAG",
    force_deterministic: bool = False,
) -> str:
    cards_path = Path(cards_path)
    outputs_dir = Path(outputs_dir)
    prompt_path = Path(prompt_path)
    weekly_dir = outputs_dir / "digests" / "weeklies"
    ensure_dir(outputs_dir / "digests")
    ensure_dir(weekly_dir)

    cards = read_jsonl(cards_path)
    taxonomy_md = read_text(outputs_dir / "taxons" / "taxonomy.md")
    comparison_rows = read_csv_rows(outputs_dir / "tables" / "comparison_table.csv")
    trend_analysis_md = read_text(outputs_dir / "trends" / "trend_analysis.md")
    today = datetime.now().date().isoformat()
    comparison_lookup = category_lookup_from_comparison(comparison_rows)

    client = LLMClient(temperature=0.0)
    prompt = prompt_path.read_text(encoding="utf-8")
    input_data = {
        "topic": topic,
        "date": today,
        "cards_count": len(cards),
        "paper_cards": compact_cards(cards, comparison_lookup),
        "taxonomy_md": truncate(taxonomy_md, 10000),
        "comparison_table": comparison_rows[:80],
        "trend_analysis_md": truncate(trend_analysis_md, 10000),
        "required_sections": [
            "本周概览",
            "分类体系摘要",
            "方法对比摘要",
            "趋势分析",
            "研究空白与未来方向",
        ],
    }

    if force_deterministic:
        digest = deterministic_digest(cards, comparison_rows, topic=topic, today=today, mock_notice=False)
    elif client.mock:
        digest = deterministic_digest(cards, comparison_rows, topic=topic, today=today, mock_notice=True)
    else:
        digest = client.chat_text(prompt, input_data).strip()
        if client.last_call_used_mock or not digest:
            digest = deterministic_digest(cards, comparison_rows, topic=topic, today=today, mock_notice=True)

    latest_path = outputs_dir / "digests" / "weekly_digest_latest.md"
    dated_path = weekly_dir / f"{today}.md"
    latest_path.write_text(digest + "\n", encoding="utf-8")
    dated_path.write_text(digest + "\n", encoding="utf-8")
    print(f"[weekly_survey_generator] Wrote {latest_path}")
    print(f"[weekly_survey_generator] Wrote {dated_path}")
    return digest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the weekly survey digest.")
    parser.add_argument("--cards_path", default=str(CARDS_DIR / "paper_cards.jsonl"))
    parser.add_argument("--outputs_dir", default=str(Path(DIGESTS_DIR).parent))
    parser.add_argument("--prompt_path", default=str(DIGEST_PMTS_DIR / "weekly_digest.txt"))
    parser.add_argument("--topic", default="Retrieval-Augmented Generation, RAG")
    parser.add_argument("--deterministic", action="store_true", help="Skip LLM text generation and use a deterministic digest template.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_weekly_digest(
        cards_path=Path(args.cards_path),
        outputs_dir=Path(args.outputs_dir),
        prompt_path=Path(args.prompt_path),
        topic=args.topic,
        force_deterministic=args.deterministic,
    )


if __name__ == "__main__":
    main()
