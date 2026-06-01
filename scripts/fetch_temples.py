from pathlib import Path
from urllib.request import urlopen, Request


SOURCE_URL = "https://religion.moi.gov.tw/Report/temple.xml"
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "temple.xml"


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    request = Request(SOURCE_URL, headers={"User-Agent": "temple-map-mvp/0.1"})
    with urlopen(request, timeout=60) as response:
        TARGET.write_bytes(response.read())
    print(f"Downloaded {TARGET} ({TARGET.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
