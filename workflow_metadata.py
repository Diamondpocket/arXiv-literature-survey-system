from __future__ import annotations

from typing import Any, Dict, List


STAGE_SEQUENCE: List[Dict[str, str]] = [
    {"id": "fetch", "label_zh": "抓取 arXiv", "label_en": "Fetch arXiv"},
    {"id": "cards", "label_zh": "结构化抽取", "label_en": "Generate Cards"},
    {"id": "analysis", "label_zh": "分类与对比分析", "label_en": "Cluster Analysis"},
    {"id": "weekly", "label_zh": "生成每周综述", "label_en": "Weekly Digest"},
]

STAGE_LOOKUP: Dict[str, Dict[str, str]] = {stage["id"]: stage for stage in STAGE_SEQUENCE}


def build_stage_entry(
    stage_id: str,
    *,
    status: str = "pending",
    detail: str = "",
    started_at: str | None = None,
    finished_at: str | None = None,
    progress_current: int = 0,
    progress_total: int | None = None,
    progress_percent: int = 0,
) -> Dict[str, Any]:
    meta = STAGE_LOOKUP[stage_id]
    return {
        "id": stage_id,
        "label_zh": meta["label_zh"],
        "label_en": meta["label_en"],
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "detail": detail,
        "progress_current": progress_current,
        "progress_total": progress_total,
        "progress_percent": progress_percent,
    }


def build_initial_stage_entries() -> List[Dict[str, Any]]:
    return [build_stage_entry(stage["id"]) for stage in STAGE_SEQUENCE]
