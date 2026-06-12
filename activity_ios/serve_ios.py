"""
iPhoneから同じWi-Fiでアクセスできる簡易サーバー

使い方:
  python serve_ios.py

表示されたURLをiPhoneのSafariで開き、
「共有」→「ホーム画面に追加」でアプリのように使えます。
"""

import http.server
import socket
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080
DIR = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)


def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> None:
    ip = local_ip()
    url = f"http://{ip}:{PORT}"
    print("=" * 50)
    print("iPhone用 活動量計算アプリ サーバー")
    print("=" * 50)
    print(f"PCで開く      : http://127.0.0.1:{PORT}")
    print(f"iPhoneで開く  : {url}")
    print()
    print("iPhoneの手順:")
    print("  1. iPhoneをPCと同じWi-Fiに接続")
    print("  2. Safariで上のURLを開く")
    print("  3. 共有ボタン → ホーム画面に追加")
    print("=" * 50)

    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        try:
            webbrowser.open(f"http://127.0.0.1:{PORT}")
        except Exception:
            pass
        httpd.serve_forever()


if __name__ == "__main__":
    main()
