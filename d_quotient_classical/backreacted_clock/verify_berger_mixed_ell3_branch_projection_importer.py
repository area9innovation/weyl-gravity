#!/usr/bin/env python3
"""Independently verify the fail-closed Berger branch-projection importer."""

import json

from d_quotient_classical.backreacted_clock import berger_mixed_ell3_branch_projection_importer as result


def main() -> int:
    stored = json.loads(result.OUTPUT.read_text())
    result.verify(stored)
    if stored != result.build():
        raise ValueError("branch-projection importer certificate drifted")
    status = stored["input_contract"]["status"]
    if status not in {"MISSING", "IMPORTED"}:
        raise ValueError("unknown branch-map import status")
    print(f"BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1 verification: PASS ({status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
