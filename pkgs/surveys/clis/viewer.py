from __future__ import annotations

import csv
import json
import mimetypes
import socket
import sys
import webbrowser
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from urllib.parse import urlparse

try:
    from pkgs.surveys.metas.paths import runtime_imports_dir, runtime_uis_dir
except ImportError:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from pkgs.surveys.metas.paths import runtime_imports_dir, runtime_uis_dir


VIEWER_FILE_HINTS = {
    "papersRaw": ["dats/raws/papers_raw.json", "papers_raw.json"],
    "cards": ["dats/cards/paper_cards.jsonl", "paper_cards.jsonl"],
    "comparison": ["outs/tables/comparison_table.csv", "comparison_table.csv"],
    "taxonomy": ["outs/taxons/taxonomy.md", "taxonomy.md"],
    "trend": ["outs/trends/trend_analysis.md", "trend_analysis.md"],
    "weekly": ["outs/digests/weekly_digest_latest.md", "weekly_digest_latest.md"],
    "pipelineStatus": ["outs/stats/pipeline_status.json", "pipeline_status.json"],
    "pipelineHistory": ["outs/stats/pipeline_history.json", "pipeline_history.json"],
}


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


UIS_DIR = runtime_uis_dir()
VIEWERS_DIR = UIS_DIR / "viewers"
ASSETS_DIR = UIS_DIR / "assets"
IMPORTS_DIR = runtime_imports_dir()


def normalize_path(value: str | Path) -> str:
    return str(value).replace("\\", "/")


def safe_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-") or "batch"


def detect_kind(path: str) -> str | None:
    lower = normalize_path(path).lower()
    for kind, candidates in VIEWER_FILE_HINTS.items():
        for candidate in candidates:
            if lower.endswith(candidate.lower()):
                return kind
    return None


def parse_json_text(text: str, fallback: object) -> object:
    try:
        payload = json.loads(text.strip()) if text.strip() else fallback
    except json.JSONDecodeError:
        return fallback
    return payload


def parse_jsonl_text(text: str) -> list[dict]:
    rows: list[dict] = []
    for line in text.splitlines():
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


def parse_csv_text(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    return list(csv.DictReader(lines))


def decode_bytes(payload: bytes) -> str:
    return payload.decode("utf-8", errors="ignore")


def build_empty_batch(label: str, batch_id: str, source_type: str, source_path: str) -> dict:
    return {
        "id": batch_id,
        "label": label,
        "source": "dropbox",
        "sourceType": source_type,
        "sourcePath": source_path,
        "loadedFiles": [],
        "rawPapers": [],
        "cards": [],
        "comparison": [],
        "taxonomy": "",
        "trend": "",
        "weekly": "",
        "pipelineStatus": None,
        "pipelineHistory": [],
        "updatedAt": datetime.now().astimezone().isoformat(),
    }


def apply_batch_payload(batch: dict, kind: str, text: str) -> None:
    if kind == "papersRaw":
        payload = parse_json_text(text, [])
        batch["rawPapers"] = payload if isinstance(payload, list) else []
        return
    if kind == "cards":
        batch["cards"] = [{**item, "__batch_label": batch["label"]} for item in parse_jsonl_text(text)]
        return
    if kind == "comparison":
        batch["comparison"] = [{**item, "__batch_label": batch["label"]} for item in parse_csv_text(text)]
        return
    if kind == "taxonomy":
        batch["taxonomy"] = text
        return
    if kind == "trend":
        batch["trend"] = text
        return
    if kind == "weekly":
        batch["weekly"] = text
        return
    if kind == "pipelineStatus":
        payload = parse_json_text(text, None)
        batch["pipelineStatus"] = payload if isinstance(payload, dict) else None
        return
    if kind == "pipelineHistory":
        payload = parse_json_text(text, [])
        batch["pipelineHistory"] = payload if isinstance(payload, list) else []


def batch_from_directory(path: Path) -> dict:
    batch = build_empty_batch(
        label=path.name,
        batch_id=f"dir-{safe_slug(path.name)}-{int(path.stat().st_mtime)}",
        source_type="directory",
        source_path=str(path.resolve()),
    )
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        relative_path = normalize_path(file_path.relative_to(path))
        kind = detect_kind(relative_path) or "unused"
        batch["loadedFiles"].append(
            {
                "name": file_path.name,
                "relativePath": relative_path,
                "size": file_path.stat().st_size,
                "kind": kind,
            }
        )
        if kind == "unused":
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        apply_batch_payload(batch, kind, text)
    return batch


def batch_from_zip(path: Path) -> dict:
    batch = build_empty_batch(
        label=path.name,
        batch_id=f"zip-{safe_slug(path.stem)}-{int(path.stat().st_mtime)}",
        source_type="zip",
        source_path=str(path.resolve()),
    )
    with zipfile.ZipFile(path) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            relative_path = normalize_path(info.filename)
            kind = detect_kind(relative_path) or "unused"
            batch["loadedFiles"].append(
                {
                    "name": Path(relative_path).name,
                    "relativePath": relative_path,
                    "size": info.file_size,
                    "kind": kind,
                }
            )
            if kind == "unused":
                continue
            text = decode_bytes(archive.read(info))
            apply_batch_payload(batch, kind, text)
    return batch


def batch_from_loose_files(paths: list[Path]) -> dict | None:
    if not paths:
        return None
    folder = IMPORTS_DIR.resolve()
    batch = build_empty_batch(
        label="Loose Files",
        batch_id=f"loose-files-{int(datetime.now().timestamp())}",
        source_type="files",
        source_path=str(folder),
    )
    for file_path in sorted(paths):
        relative_path = normalize_path(file_path.relative_to(folder))
        kind = detect_kind(relative_path) or "unused"
        batch["loadedFiles"].append(
            {
                "name": file_path.name,
                "relativePath": relative_path,
                "size": file_path.stat().st_size,
                "kind": kind,
            }
        )
        if kind == "unused":
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        apply_batch_payload(batch, kind, text)
    return batch


def collect_import_entries() -> list[Path]:
    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(IMPORTS_DIR.iterdir(), key=lambda item: item.name.lower())


def load_import_batches() -> list[dict]:
    batches: list[dict] = []
    loose_files: list[Path] = []
    for entry in collect_import_entries():
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            batches.append(batch_from_directory(entry))
            continue
        if entry.is_file() and entry.suffix.lower() == ".zip":
            try:
                batches.append(batch_from_zip(entry))
            except zipfile.BadZipFile:
                continue
            continue
        if entry.is_file():
            loose_files.append(entry)
    loose_batch = batch_from_loose_files(loose_files)
    if loose_batch:
        batches.append(loose_batch)
    return batches


def imports_meta() -> dict:
    entries = []
    for entry in collect_import_entries():
        if entry.name.startswith("."):
            continue
        entry_type = "directory" if entry.is_dir() else "zip" if entry.suffix.lower() == ".zip" else "file"
        entries.append(
            {
                "name": entry.name,
                "type": entry_type,
                "size": entry.stat().st_size if entry.is_file() else 0,
                "updatedAt": datetime.fromtimestamp(entry.stat().st_mtime).astimezone().isoformat(),
            }
        )
    return {
        "importsDir": str(IMPORTS_DIR.resolve()),
        "entryCount": len(entries),
        "entries": entries,
    }


class ViewerHandler(BaseHTTPRequestHandler):
    server_version = "SurveyViewer/2.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/", "/viewers/viewer.html"}:
            self.send_static(VIEWERS_DIR, "viewer.html")
            return
        if path == "/api/imports/meta":
            self.send_json(imports_meta())
            return
        if path == "/api/imports/load":
            self.send_json({"meta": imports_meta(), "batches": load_import_batches()})
            return
        if path.startswith("/assets/"):
            self.send_static(ASSETS_DIR, path.removeprefix("/assets/"))
            return
        if path.startswith("/viewers/"):
            self.send_static(VIEWERS_DIR, path.removeprefix("/viewers/"))
            return
        self.send_error(404, "Not found")

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
        payload = safe_path.read_bytes()
        content_type = mimetypes.guess_type(safe_path.name)[0] or "application/octet-stream"
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

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[viewer] {self.address_string()} - {fmt % args}")


def choose_port(host: str = "127.0.0.1", start: int = 8877, attempts: int = 20) -> int:
    for port in range(start, start + attempts):
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind((host, port))
        except OSError:
            continue
        finally:
            probe.close()
        return port
    raise OSError(f"No free port found in range {start}-{start + attempts - 1}.")


def main() -> None:
    host = "127.0.0.1"
    port = choose_port(host=host, start=8877)
    if not UIS_DIR.exists():
        raise FileNotFoundError(f"UI directory not found: {UIS_DIR}")

    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ReusableThreadingHTTPServer((host, port), ViewerHandler)
    url = f"http://{host}:{port}/viewers/viewer.html"
    print(f"[viewer_app] Import drop folder: {IMPORTS_DIR.resolve()}")
    print(f"[viewer_app] Opening standalone viewer at {url}")
    Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
