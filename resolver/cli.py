"""Convert recorded player evidence into a provider-by-kind audit report."""
import argparse
import json
from pathlib import Path
from .model import classify

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        parser.error("input must be a JSON array of observations")
    report = {"schema_version": 1, "results": classify(raw)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(report['results'])} provider/kind results to {args.output}")

if __name__ == "__main__":
    main()
