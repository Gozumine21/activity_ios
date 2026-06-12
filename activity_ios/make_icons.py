"""PWA用アイコンを生成（Pillow不要・最小PNG）"""

from pathlib import Path
import struct
import zlib


def png(size: int, path: Path) -> None:
    """シンプルな単色＋アクセントのPNGを生成"""
    bg = (26, 26, 46)
    accent = (0, 212, 170)
    rows = []
    cx, cy, r = size // 2, size // 2, size // 3
    for y in range(size):
        row = b"\x00"
        for x in range(size):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                row += bytes(accent)
            else:
                row += bytes(bg)
        rows.append(row)
    raw = b"".join(rows)
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png_data = b"\x89PNG\r\n\x1a\n"
    png_data += chunk(b"IHDR", ihdr)
    png_data += chunk(b"IDAT", compressed)
    png_data += chunk(b"IEND", b"")
    path.write_bytes(png_data)


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    png(192, base / "icon-192.png")
    png(512, base / "icon-512.png")
    print("icon-192.png, icon-512.png を作成しました")
