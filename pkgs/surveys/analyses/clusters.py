from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

from ..clients.llms import LLMClient
from ..metas.paths import CARDS_DIR, TABLES_DIR, TAXONS_DIR, TAXON_PMTS_DIR, TRENDS_DIR


UNKNOWN_MARKERS = {"", "unknown", "not specified", "n/a", "na", "none", "null"}
COMPARISON_COLUMNS = [
    "title",
    "method",
    "complexity",
    "scenario",
    "advantages",
    "limitations",
    "data_driven",
    "category",
    "category_zh",
    "category_bilingual",
    "source_category",
]

MACRO_CATEGORY_DESCRIPTIONS = {
    "Core Retrieval and Ranking Methods": (
        "Retriever, reranker, query routing, indexing, chunking, embedding, and evidence-selection methods."
    ),
    "Agentic and Multi-Agent RAG": (
        "RAG systems that use agents, planning, tool use, memory navigation, or multi-agent collaboration."
    ),
    "Knowledge Graph and Structured Knowledge RAG": (
        "Methods that organize evidence as graphs, triplets, hypergraphs, symbolic structures, or explicit memory."
    ),
    "Multimodal and Visual RAG": (
        "RAG for images, videos, long visual documents, segmentation, visual QA, and other multimodal inputs."
    ),
    "Evaluation, Benchmarks, and Diagnostics": (
        "Benchmarks, metrics, diagnostic frameworks, performance predictors, and evaluation protocols."
    ),
    "Reliability, Safety, Privacy, and Security": (
        "Work on hallucination, faithfulness, robustness, poisoning, privacy leakage, bias, and safe deployment."
    ),
    "Domain-Specific RAG Applications": (
        "RAG adapted to concrete domains such as medicine, law, education, finance, software, science, and cities."
    ),
    "Efficiency, Deployment, and On-Device RAG": (
        "Systems focused on latency, compression, edge or on-device use, deployment constraints, and operational cost."
    ),
    "Survey, Theory, and Governance": (
        "Survey papers, theoretical analyses, governance, compliance, and socio-technical framing."
    ),
    "General or Unspecified RAG": (
        "Papers whose abstracts do not provide enough evidence for a more specific macro category."
    ),
}

MACRO_CATEGORY_ZH = {
    "Core Retrieval and Ranking Methods": "核心检索与排序方法",
    "Agentic and Multi-Agent RAG": "智能体与多智能体 RAG",
    "Knowledge Graph and Structured Knowledge RAG": "知识图谱与结构化知识 RAG",
    "Multimodal and Visual RAG": "多模态与视觉 RAG",
    "Evaluation, Benchmarks, and Diagnostics": "评测、基准与诊断",
    "Reliability, Safety, Privacy, and Security": "可靠性、安全、隐私与防护",
    "Domain-Specific RAG Applications": "领域应用型 RAG",
    "Efficiency, Deployment, and On-Device RAG": "效率、部署与端侧 RAG",
    "Survey, Theory, and Governance": "综述、理论与治理",
    "General or Unspecified RAG": "通用或未明确 RAG",
}

MACRO_CATEGORY_DESCRIPTIONS_ZH = {
    "Core Retrieval and Ranking Methods": "关注检索器、重排序、查询路由、索引、分块、嵌入与证据选择等核心方法。",
    "Agentic and Multi-Agent RAG": "关注带有规划、工具调用、记忆导航或多智能体协作的 RAG 系统。",
    "Knowledge Graph and Structured Knowledge RAG": "关注图谱、三元组、超图、符号结构或显式记忆组织方式。",
    "Multimodal and Visual RAG": "关注图像、视频、长视觉文档、分割、视觉问答等多模态场景。",
    "Evaluation, Benchmarks, and Diagnostics": "关注基准、指标、诊断框架、性能预测和评测协议。",
    "Reliability, Safety, Privacy, and Security": "关注幻觉、忠实性、鲁棒性、投毒、隐私泄露、偏见和安全部署。",
    "Domain-Specific RAG Applications": "关注医疗、法律、教育、金融、软件、科学、城市等具体领域适配。",
    "Efficiency, Deployment, and On-Device RAG": "关注延迟、压缩、端侧部署、运行成本和工程约束。",
    "Survey, Theory, and Governance": "关注综述、理论分析、治理、合规和社会技术视角。",
    "General or Unspecified RAG": "摘要证据不足，暂时无法归入更具体的宏观类别。",
}


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


def clean(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if text else default


def is_unknown(value: Any) -> bool:
    return clean(value).lower() in UNKNOWN_MARKERS


def compact(text: Any, limit: int = 220) -> str:
    value = clean(text, default="not specified")
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def category_zh(category: str) -> str:
    return MACRO_CATEGORY_ZH.get(category, "通用或未明确 RAG")


def bilingual_category(category: str) -> str:
    return f"{category_zh(category)} ({category})"


def card_text(card: Dict[str, Any]) -> str:
    return " ".join(
        clean(card.get(field), "")
        for field in [
            "title",
            "summary",
            "problem",
            "key_idea",
            "method",
            "dataset_or_scenario",
            "metrics",
            "results_summary",
            "innovation_type",
            "limitations",
            "best_fit_category",
        ]
    ).lower()


def has_any(text: str, terms: Iterable[str]) -> bool:
    for term in terms:
        normalized = term.strip().lower()
        if not normalized:
            continue
        pattern = rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])"
        if re.search(pattern, text):
            return True
    return False


def infer_macro_category(card: Dict[str, Any]) -> str:
    text = card_text(card)
    source_text = " ".join(clean(card.get(field), "") for field in ["title", "best_fit_category"]).lower()
    innovation = clean(card.get("innovation_type"), "").lower()

    if innovation in {"survey", "theoretical_analysis"} or has_any(
        source_text,
        ["survey", "systematic review", "literature review", "governance", "compliance", "economic analysis", "socio-technical"],
    ):
        return "Survey, Theory, and Governance"

    if has_any(
        source_text,
        ["multimodal", "multi-modal", "visual", "vision", "video", "image", "segmentation", "vqa", "deepfake", "docvqa", "visual document"],
    ):
        return "Multimodal and Visual RAG"

    if has_any(source_text, ["agent", "multi-agent", "tool", "planning", "navigation", "memory", "workflow"]):
        return "Agentic and Multi-Agent RAG"

    if has_any(source_text, ["knowledge graph", "graphrag", "triplet", "hypergraph", "symbolic", "structured", "ontology"]):
        return "Knowledge Graph and Structured Knowledge RAG"

    if has_any(
        source_text,
        ["hallucination", "faithfulness", "groundedness", "robustness", "attack", "poison", "privacy", "security", "bias", "fairness", "safety"],
    ):
        return "Reliability, Safety, Privacy, and Security"

    if has_any(source_text, ["benchmark", "evaluation", "metric", "diagnostic", "leaderboard", "performance prediction"]):
        return "Evaluation, Benchmarks, and Diagnostics"

    if has_any(source_text, ["on-device", "edge", "latency", "efficient", "efficiency", "compression", "deployment", "cost", "runtime"]):
        return "Efficiency, Deployment, and On-Device RAG"

    if has_any(source_text, ["medical", "clinical", "legal", "education", "finance", "software", "urban", "scientific", "biology"]):
        return "Domain-Specific RAG Applications"

    if has_any(source_text, ["rerank", "retriever", "query routing", "hybrid retrieval", "bandit", "chunking", "indexing", "embedding"]):
        return "Core Retrieval and Ranking Methods"

    if innovation in {"reliability_or_safety"}:
        return "Reliability, Safety, Privacy, and Security"
    if innovation in {"benchmark_or_evaluation"}:
        return "Evaluation, Benchmarks, and Diagnostics"
    if innovation in {"application_or_domain_adaptation"}:
        return "Domain-Specific RAG Applications"
    if innovation in {"generation_method", "system_or_architecture"}:
        return "Core Retrieval and Ranking Methods"

    return "General or Unspecified RAG"


def infer_complexity(card: Dict[str, Any]) -> str:
    text = " ".join(
        clean(card.get(field), "")
        for field in ["method", "key_idea", "innovation_type", "results_summary"]
    ).lower()
    high_terms = ["training", "fine-tuning", "large-scale", "multi-stage", "multi-agent", "optimization"]
    medium_terms = ["framework", "pipeline", "rerank", "graph", "index", "retrieval", "architecture"]
    if any(term in text for term in high_terms):
        return "high"
    if any(term in text for term in medium_terms):
        return "medium"
    if is_unknown(card.get("method")):
        return "unknown"
    return "low"


def infer_data_driven(card: Dict[str, Any]) -> str:
    dataset_known = not is_unknown(card.get("dataset_or_scenario"))
    metrics_known = not is_unknown(card.get("metrics"))
    results_known = not is_unknown(card.get("results_summary"))
    if dataset_known and (metrics_known or results_known):
        return "yes"
    if dataset_known:
        return "partly"
    return "unknown"


def build_comparison_rows(cards: Iterable[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for card in cards:
        source_category = clean(card.get("best_fit_category"))
        category = infer_macro_category(card)
        rows.append(
            {
                "title": clean(card.get("title")),
                "method": compact(card.get("method")),
                "complexity": infer_complexity(card),
                "scenario": compact(card.get("dataset_or_scenario")),
                "advantages": compact(card.get("key_idea") or card.get("results_summary")),
                "limitations": compact(card.get("limitations")),
                "data_driven": infer_data_driven(card),
                "category": category,
                "category_zh": category_zh(category),
                "category_bilingual": bilingual_category(category),
                "source_category": source_category,
            }
        )
    return rows


def top_keywords(cards: List[Dict[str, Any]], top_n: int = 12) -> List[tuple[str, int]]:
    vocabulary = [
        "retrieval",
        "reranking",
        "indexing",
        "chunking",
        "graph",
        "knowledge graph",
        "multimodal",
        "long-context",
        "agent",
        "tool",
        "benchmark",
        "evaluation",
        "hallucination",
        "faithfulness",
        "domain",
        "medical",
        "legal",
        "scientific",
        "privacy",
        "efficiency",
    ]
    counter: Counter[str] = Counter()
    for card in cards:
        text = " ".join(
            clean(card.get(field), "")
            for field in ["title", "summary", "problem", "key_idea", "method", "innovation_type"]
        ).lower()
        for keyword in vocabulary:
            if keyword in text:
                counter[keyword] += 1
    return counter.most_common(top_n)


def month_distribution(cards: List[Dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for card in cards:
        published = clean(card.get("published"), "")
        month = published[:7] if len(published) >= 7 else "unknown"
        counter[month] += 1
    return counter


def representative_titles(cards: List[Dict[str, Any]], category: str, limit: int = 3) -> List[str]:
    titles: List[str] = []
    for card in cards:
        if infer_macro_category(card) == category:
            titles.append(clean(card.get("title")))
        if len(titles) >= limit:
            break
    return titles


def fine_category_examples(cards: List[Dict[str, Any]], category: str, limit: int = 5) -> str:
    counter: Counter[str] = Counter()
    for card in cards:
        if infer_macro_category(card) == category:
            counter[clean(card.get("best_fit_category"))] += 1
    examples = [name for name, _ in counter.most_common(limit) if name.lower() not in UNKNOWN_MARKERS]
    return "; ".join(examples) if examples else "not specified"


def compact_cards_for_taxonomy(cards: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, str]]:
    compacted: List[Dict[str, str]] = []
    for card in cards[:limit]:
        compacted.append(
            {
                "arxiv_id": clean(card.get("arxiv_id")),
                "title": compact(card.get("title"), 180),
                "best_fit_category": clean(card.get("best_fit_category")),
                "innovation_type": clean(card.get("innovation_type")),
                "problem": compact(card.get("problem"), 180),
                "key_idea": compact(card.get("key_idea"), 180),
                "method": compact(card.get("method"), 180),
                "dataset_or_scenario": compact(card.get("dataset_or_scenario"), 120),
                "metrics": compact(card.get("metrics"), 120),
                "limitations": compact(card.get("limitations"), 120),
                "confidence_level": clean(card.get("confidence_level")),
            }
        )
    return compacted


def generate_llm_taxonomy(cards: List[Dict[str, Any]], prompt_path: Path | None) -> str | None:
    if not cards or prompt_path is None or not prompt_path.exists():
        return None

    client = LLMClient(temperature=0.0)
    if client.mock:
        return None

    prompt = prompt_path.read_text(encoding="utf-8")
    input_data = {
        "cards_count": len(cards),
        "paper_cards": compact_cards_for_taxonomy(cards),
    }
    text = client.chat_text(prompt, input_data).strip()
    if client.last_call_used_mock or not text:
        return None
    return (
        text
        + "\n\n---\n\n"
        + f"Generated from {len(cards)} structured paper cards. Model: {client.model}. "
        + f"Generated at: {datetime.now(timezone.utc).isoformat()}.\n"
    )


def generate_taxonomy(cards: List[Dict[str, Any]]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    if not cards:
        return (
            "# Taxonomy\n\n"
            f"Generated at: {generated_at}\n\n"
            "No paper cards are available yet. Run the fetch and card-generation steps first.\n"
        )

    category_counts = Counter(infer_macro_category(card) for card in cards)
    innovation_counts = Counter(clean(card.get("innovation_type")) for card in cards)
    keyword_counts = top_keywords(cards)

    lines = [
        "# Taxonomy",
        "",
        f"Generated at: {generated_at}",
        f"Evidence base: {len(cards)} structured paper cards derived from arXiv abstracts.",
        "",
        "## 高层分类 High-Level Categories",
    ]
    for category, count in category_counts.most_common():
        examples = "; ".join(representative_titles(cards, category))
        description = MACRO_CATEGORY_DESCRIPTIONS.get(category, "not specified")
        description_zh = MACRO_CATEGORY_DESCRIPTIONS_ZH.get(category, "暂无说明。")
        fine_labels = fine_category_examples(cards, category)
        lines.append(f"- **{bilingual_category(category)}** ({count} papers / {count} 篇):")
        lines.append(f"  中文说明: {description_zh}")
        lines.append(f"  English note: {description}")
        lines.append(f"  Representative papers / 代表论文: {examples or 'not specified'}.")
        lines.append(f"  Fine-grained signals from cards / 卡片细粒度信号: {fine_labels}.")

    lines.extend(["", "## 创新类型 Innovation Types"])
    for innovation, count in innovation_counts.most_common():
        lines.append(f"- **{innovation}**: {count} papers.")

    lines.extend(["", "## 关键词信号 Keyword Signals"])
    if keyword_counts:
        for keyword, count in keyword_counts:
            lines.append(f"- `{keyword}` appears in {count} cards.")
    else:
        lines.append("- No stable keyword signal was detected.")

    lines.extend(
        [
            "",
            "## 证据说明 Evidence Note",
            "This taxonomy is generated from intermediate JSON cards, not directly from free-form summarization. "
            "Categories should be reviewed when many cards have `unknown` or `not specified` fields.",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_trend_analysis(cards: List[Dict[str, Any]]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    if not cards:
        return "# Trend Analysis\n\n" f"Generated at: {generated_at}\n\nNo paper cards are available yet.\n"

    category_counts = Counter(infer_macro_category(card) for card in cards)
    innovation_counts = Counter(clean(card.get("innovation_type")) for card in cards)
    confidence_counts = Counter(clean(card.get("confidence_level")) for card in cards)
    months = month_distribution(cards)
    missing_dataset = sum(1 for card in cards if is_unknown(card.get("dataset_or_scenario")))
    missing_metrics = sum(1 for card in cards if is_unknown(card.get("metrics")))
    data_driven = Counter(infer_data_driven(card) for card in cards)
    keywords = top_keywords(cards, top_n=8)

    recent_months = sorted((month for month in months if month != "unknown"), reverse=True)[:6]
    top_category = category_counts.most_common(1)[0][0]
    top_innovation = innovation_counts.most_common(1)[0][0]

    lines = [
        "# Trend Analysis",
        "",
        f"Generated at: {generated_at}",
        f"Evidence base: {len(cards)} structured paper cards.",
        "",
        "## 分布观察 Observed Distribution",
        f"- Largest category / 最大类别: **{bilingual_category(top_category)}** ({category_counts[top_category]} papers / {category_counts[top_category]} 篇).",
        f"- Most frequent innovation type: **{top_innovation}** ({innovation_counts[top_innovation]} papers).",
        f"- Confidence levels: {dict(confidence_counts)}.",
        f"- Data-driven signal: {dict(data_driven)}.",
        "",
        "## 近期发文量 Recent Publication Volume",
    ]
    for month in recent_months:
        lines.append(f"- {month}: {months[month]} papers.")

    lines.extend(["", "## 主题信号 Topic Signals"])
    for keyword, count in keywords:
        lines.append(f"- `{keyword}`: {count} cards.")

    lines.extend(
        [
            "",
            "## 研究趋势 Research Trends",
            "- RAG work is moving from generic retrieval pipelines toward specialized variants: evaluation, domain adaptation, graph or structured knowledge, multimodal settings, and reliability-oriented designs.",
            "- The method layer is increasingly modular: retriever, reranker, generator, evaluator, and sometimes agent or tool components are treated as separable optimization targets.",
            "- Evaluation and benchmarking appear as a central pressure point because many abstracts emphasize performance claims but do not always expose enough metrics in the abstract alone.",
            "",
            "## 研究空白与未来方向 Research Gaps and Future Directions",
            f"- **Abstract-level evidence gap:** {missing_dataset}/{len(cards)} cards do not specify datasets or scenarios, and {missing_metrics}/{len(cards)} do not specify metrics. A stronger future survey can add full-text extraction for high-impact papers only, while keeping the abstract-only MVP reproducible.",
            "- **Comparable evaluation gap:** RAG papers often optimize different stages and report different metrics. A useful future direction is a unified comparison matrix that separates retrieval quality, answer faithfulness, latency, and cost.",
            "- **Operational deployment gap:** Many methods describe accuracy or quality, but production constraints such as freshness, privacy, index maintenance, and failure recovery are less consistently visible in abstracts.",
            "- **Original viewpoint:** The next wave of RAG research is likely to be less about adding another retrieval step and more about deciding when retrieval should be avoided, compressed, audited, or escalated to tools. This suggests adaptive RAG controllers as a promising organizing direction.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_analysis(
    cards_path: Path | str = CARDS_DIR / "paper_cards.jsonl",
    outputs_dir: Path | str = Path(TAXONS_DIR).parent,
    taxonomy_prompt_path: Path | str | None = TAXON_PMTS_DIR / "taxonomy_generation.txt",
    use_llm_taxonomy: bool = True,
) -> None:
    cards_path = Path(cards_path)
    outputs_dir = Path(outputs_dir)
    ensure_dir(outputs_dir)

    cards = read_jsonl(cards_path)
    prompt_path = Path(taxonomy_prompt_path) if taxonomy_prompt_path is not None else None
    taxonomy = None
    if use_llm_taxonomy:
        taxonomy = generate_llm_taxonomy(cards, prompt_path)
    if taxonomy is None:
        taxonomy = generate_taxonomy(cards)
    trend_analysis = generate_trend_analysis(cards)
    comparison_rows = build_comparison_rows(cards)

    (outputs_dir / "taxons").mkdir(parents=True, exist_ok=True)
    (outputs_dir / "tables").mkdir(parents=True, exist_ok=True)
    (outputs_dir / "trends").mkdir(parents=True, exist_ok=True)

    (outputs_dir / "taxons" / "taxonomy.md").write_text(taxonomy, encoding="utf-8")
    pd.DataFrame(comparison_rows, columns=COMPARISON_COLUMNS).to_csv(
        outputs_dir / "tables" / "comparison_table.csv",
        index=False,
        encoding="utf-8",
    )
    (outputs_dir / "trends" / "trend_analysis.md").write_text(trend_analysis, encoding="utf-8")

    print(f"[cluster_analysis] Wrote {outputs_dir / 'taxons' / 'taxonomy.md'}")
    print(f"[cluster_analysis] Wrote {outputs_dir / 'tables' / 'comparison_table.csv'}")
    print(f"[cluster_analysis] Wrote {outputs_dir / 'trends' / 'trend_analysis.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate taxonomy, comparison table, and trend analysis.")
    parser.add_argument("--cards_path", default=str(CARDS_DIR / "paper_cards.jsonl"))
    parser.add_argument("--outputs_dir", default=str(Path(TAXONS_DIR).parent))
    parser.add_argument("--taxonomy_prompt_path", default=str(TAXON_PMTS_DIR / "taxonomy_generation.txt"))
    parser.add_argument("--no_llm_taxonomy", action="store_true", help="Disable optional LLM taxonomy synthesis.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_analysis(
        cards_path=Path(args.cards_path),
        outputs_dir=Path(args.outputs_dir),
        taxonomy_prompt_path=Path(args.taxonomy_prompt_path),
        use_llm_taxonomy=not args.no_llm_taxonomy,
    )


if __name__ == "__main__":
    main()
