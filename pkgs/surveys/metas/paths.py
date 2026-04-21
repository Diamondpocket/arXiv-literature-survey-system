from __future__ import annotations

import sys
from pathlib import Path


def _find_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return current.parents[4]


ROOT_DIR = _find_root()
BUNDLES_DIR = Path(getattr(sys, "_MEIPASS")) if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else ROOT_DIR
RUNTIMES_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else ROOT_DIR

CFGS_DIR = ROOT_DIR / "cfgs"
ENVS_DIR = CFGS_DIR / "envs"
PKG_CFGS_DIR = CFGS_DIR / "pkgs"

DATS_DIR = ROOT_DIR / "dats"
RAWS_DIR = DATS_DIR / "raws"
CARDS_DIR = DATS_DIR / "cards"

OUTS_DIR = ROOT_DIR / "outs"
DIGESTS_DIR = OUTS_DIR / "digests"
WEEKLIES_DIR = DIGESTS_DIR / "weeklies"
STATS_DIR = OUTS_DIR / "stats"
TABLES_DIR = OUTS_DIR / "tables"
TAXONS_DIR = OUTS_DIR / "taxons"
TRENDS_DIR = OUTS_DIR / "trends"

PMTS_DIR = ROOT_DIR / "pmts"
CARD_PMTS_DIR = PMTS_DIR / "cards"
TAXON_PMTS_DIR = PMTS_DIR / "taxons"
DIGEST_PMTS_DIR = PMTS_DIR / "digests"

UIS_DIR = ROOT_DIR / "uis"
ASSETS_DIR = UIS_DIR / "assets"
DASHBOARDS_DIR = UIS_DIR / "dashboards"
VIEWERS_DIR = UIS_DIR / "viewers"

ARTS_DIR = ROOT_DIR / "arts"
BUILDS_DIR = ARTS_DIR / "builds"
DISTS_DIR = ARTS_DIR / "dists"
LOGS_DIR = ARTS_DIR / "logs"
RELEASES_DIR = ARTS_DIR / "releases"

DOCS_DIR = ROOT_DIR / "docs"
READMES_DIR = DOCS_DIR / "readmes"

SNPS_DIR = ROOT_DIR / "snps"
WEEKLY_SNPS_DIR = SNPS_DIR / "weeklies"
IMPORTS_DIR = SNPS_DIR / "imports"

TLS_DIR = ROOT_DIR / "tls"
BUILD_TLS_DIR = TLS_DIR / "builds"


def runtime_uis_dir() -> Path:
    return BUNDLES_DIR / "uis"


def runtime_dats_dir() -> Path:
    candidate = RUNTIMES_DIR / "dats"
    return candidate if candidate.exists() else BUNDLES_DIR / "dats"


def runtime_outs_dir() -> Path:
    candidate = RUNTIMES_DIR / "outs"
    return candidate if candidate.exists() else BUNDLES_DIR / "outs"


def runtime_snps_dir() -> Path:
    return RUNTIMES_DIR / "snps"


def runtime_imports_dir() -> Path:
    return runtime_snps_dir() / "imports"
