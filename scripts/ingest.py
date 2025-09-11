"""
Ingest pipeline:
- If DATA_MODE=SYNTH: generates synthetic exchange docs into data/processed/*.txt
- If DATA_MODE=REAL: converts any .md/.html in data/raw_docs/ to clean .txt in data/processed/
"""
import os, pathlib, re
from bs4 import BeautifulSoup
from markdownify import markdownify as md

DATA_MODE = os.getenv("DATA_MODE", "SYNTH")
RAW = pathlib.Path("data/raw_docs")
PROC = pathlib.Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)

def write_txt(name: str, text: str):
    (PROC / f"{name}.txt").write_text(text.strip() + "\n", encoding="utf-8")

def synth():
    # minimal, but realistic snippets
    write_txt("binance_rate_limits", """
Binance API may return HTTP 429 (Too Many Requests) when request weight exceeds the per-minute limit.
Handling: implement an exponential backoff (e.g., base=500ms) and respect 'X-MBX-USED-WEIGHT-1M'.
Order endpoint /api/v3/order default recvWindow is 5000 ms; retry on 5xx with idempotency keys.
""")
    write_txt("okx_order_rules", """
OKX order filters include minQty, stepSize. Orders failing precision return code 51004.
REST /api/v5/trade/order supports client-supplied IDs for idempotency. Rate limit resets every second.
""")
    write_txt("common_errors", """
HTTP 429: backoff + jitter; HTTP 418: IP banned temporarily.
Recommended: central rate-limit middleware + per-exchange adapters with circuit breaker.
""")

def real():
    for p in RAW.glob("*"):
        text = ""
        if p.suffix.lower() in {".md"}:
            text = p.read_text(encoding="utf-8")
        elif p.suffix.lower() in {".html", ".htm"}:
            soup = BeautifulSoup(p.read_text(encoding="utf-8"), "lxml")
            text = md(str(soup))
        elif p.suffix.lower() in {".txt"}:
            text = p.read_text(encoding="utf-8")
        else:
            continue
        # cleanup
        text = re.sub(r"\n{3,}", "\n\n", text)
        write_txt(p.stem, text)

if __name__ == "__main__":
    (synth if DATA_MODE.upper()=="SYNTH" else real)()
    print(f"Processed docs → {PROC.resolve()}")
