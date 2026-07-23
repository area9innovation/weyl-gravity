"""Negative mutations for the v5 terminal claim boundary."""
from __future__ import annotations

import copy
import json

from .produce import OUTPUT
from .verify import VerifyError, verify_data


def rejected(data: dict, text: str | None = None) -> bool:
    try:
        verify_data(data, text)
    except VerifyError:
        return True
    return False


def main() -> None:
    base = json.loads(OUTPUT.read_text())
    cases: list[tuple[dict, str | None]] = []

    m = copy.deepcopy(base)
    m["claim_flags"]["global_connection_certified"] = True
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["table_backed_runtime_gate"]["coefficient_table_materialized"] = False
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["table_backed_runtime_gate"]["carrier_flow_returned_within_20_minutes"] = True
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["chunk_successor"]["shared_generator"] = 999
    cases.append((m, None))

    m = copy.deepcopy(base)
    m["chunk_successor"]["panels_per_chunk"] = 255
    cases.append((m, None))

    m = copy.deepcopy(base)
    key = next(iter(m["imports"]))
    m["imports"][key]["sha256"] = "0" * 64
    cases.append((m, None))

    adapter = (OUTPUT.parent / "validated_global_connection.forge").read_text()
    cases.append((copy.deepcopy(base), adapter + "\nfn bad(){ let x=ivm_inverse(ivm_identity(2)); }\n"))

    if not all(rejected(data, text) for data, text in cases):
        raise SystemExit("mutation escaped")
    print(f"PASS {len(cases)} negative mutations rejected")


if __name__ == "__main__":
    main()
