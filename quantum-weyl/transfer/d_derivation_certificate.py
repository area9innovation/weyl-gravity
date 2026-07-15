"""Emit or check the ND1 selected residual D-derivation certificate."""

from __future__ import annotations

import argparse

from d_derivation_defect import OUTPUT_PATH, build_certificate, render_certificate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render_certificate(build_certificate())
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"ND1 selected residual D-derivation certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("ND1 D-DERIVATION: SELECTED RESIDUAL Q2 DEFECT ZERO, FULL LOCAL INPUT BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
