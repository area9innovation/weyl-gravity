"""Emit/check the HT1 residual cubic-block certificate."""

from __future__ import annotations

import argparse

from residual_cubic_block import (
    OUTPUT_PATH,
    build_certificate,
    render_certificate,
    validate_certificate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--max-energy", type=int, default=4)
    args = parser.parse_args()
    certificate = build_certificate(args.max_energy)
    validate_certificate(certificate)
    content = render_certificate(certificate)
    if args.emit:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding="utf-8")
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != content:
            raise SystemExit(f"HT1 residual cubic certificate is stale: {OUTPUT_PATH}")
    if not args.emit and not args.check:
        print(content, end="")
    else:
        print("HT1 RESIDUAL CUBIC BLOCK: SELECTED RESIDUAL BRACKET COMPUTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
