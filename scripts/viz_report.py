"""
Produces simple charts from /metrics and saves PNG charts for README.
"""
import requests, time, os, pathlib
import matplotlib.pyplot as plt

ASSETS = pathlib.Path("docs/README_assets"); ASSETS.mkdir(parents=True, exist_ok=True)

def snapshot_metrics():
    try:
        r = requests.get("http://127.0.0.1:8000/metrics", timeout=1.0)
        return r.json()
    except Exception:
        return {"q_count": 0, "latency_p95_ms": 0}

def main():
    xs, p95 = [], []
    for i in range(20):
        m = snapshot_metrics()
        xs.append(i); p95.append(m.get("latency_p95_ms", 0))
        time.sleep(0.2)

    plt.figure()
    plt.plot(xs, p95)
    plt.title("Latency P95 (ms)")
    plt.xlabel("tick"); plt.ylabel("ms")
    out = ASSETS / "latency_p95.png"
    plt.savefig(out, bbox_inches="tight")
    print("Saved", out)

if __name__ == "__main__":
    main()
