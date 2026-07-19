"""Emit or check the product S2 x S2 full-BV join-boundary certificate."""

from __future__ import annotations

import argparse

from .product_s2_s2_full_bv_join_boundary import OUTPUT, REPORT, build, report_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    certificate = __import__("json").dumps(result, indent=2, sort_keys=True) + "\n"
    report = report_text(result)
    if args.check:
        if OUTPUT.read_text() != certificate:
            raise SystemExit("stale product full-BV join-boundary certificate")
        if REPORT.read_text() != report:
            raise SystemExit("stale product full-BV join-boundary report")
    else:
        OUTPUT.write_text(certificate)
        REPORT.write_text(report)
    print("PRODUCT S2xS2 FULL-BV JOIN BOUNDARY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
