#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument("--timings",type=Path,default=ROOT/"temp/timings.json"); p.add_argument("--output",type=Path,default=ROOT/"temp/drawing_plan.json"); a=p.parse_args()
data=json.loads(a.timings.read_text()); words=data.get("words",[])
if not words: raise SystemExit("No aligned words available.")
a.output.write_text(json.dumps({"duration":max(w["end"] for w in words),"words":words,"paths":[{"type":"line","points":[[180,760],[1740,760]]}]},indent=2))
print(f"[plan] Wrote {a.output}")
