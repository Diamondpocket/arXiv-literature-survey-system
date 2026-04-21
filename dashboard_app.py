from __future__ import annotations

import socket
import webbrowser
from threading import Timer

from http.server import ThreadingHTTPServer

from serve_frontend import SurveyHandler


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def choose_port(host: str = "127.0.0.1", start: int = 8765, attempts: int = 20) -> int:
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
    port = choose_port(host=host, start=8765)
    httpd = ReusableThreadingHTTPServer((host, port), SurveyHandler)
    url = f"http://{host}:{port}"
    print(f"[dashboard_app] Opening dashboard at {url}")
    Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
