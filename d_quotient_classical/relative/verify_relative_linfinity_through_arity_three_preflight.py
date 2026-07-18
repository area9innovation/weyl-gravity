#!/usr/bin/env python3
"""Independently verify the compact-product relative L-infinity receiver."""

import json

from d_quotient_classical.relative import relative_linfinity_through_arity_three_preflight as result


def main() -> int:
    stored = json.loads(result.OUTPUT.read_text())
    result.verify(stored)
    if stored != result.build():
        raise ValueError("relative L-infinity preflight drifted")
    print("EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
