#!/usr/bin/env python3
"""Independently verify the fail-closed Berger branch-projection importer."""

import json

from d_quotient_classical.backreacted_clock import berger_mixed_ell3_branch_projection_importer as result


def main() -> int:
    stored = json.loads(result.OUTPUT.read_text())
    result.verify(stored)
    if stored != result.build():
        raise ValueError("branch-projection importer certificate drifted")
    if stored["input_contract"]["status"] != "MISSING":
        raise ValueError("scientific input unexpectedly appeared during the blocked preflight")
    print("BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
