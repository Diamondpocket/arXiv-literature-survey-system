from __future__ import annotations

import functools
import socket
import sys
import webbrowser
from pathlib import Path
from threading import Timer

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    from pkgs.surveys.metas.paths import runtime_uis_dir
except ImportError:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from pkgs.surveys.metas.paths import runtime_uis_dir


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


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
    ui_root = runtime_uis_dir()
    if not ui_root.exists():
        raise FileNotFoundError(f"UI directory not found: {ui_root}")

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ui_root))
    httpd = ReusableThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{port}/viewers/viewer.html"
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
