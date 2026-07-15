#!/usr/bin/env python3
"""Verify the projector-free differential-module audit of the rank-34 SCC."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_rank34_module import (  # noqa: E402
    ExpandedRelativeRank34Module,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
STATE_GAUGE = CERTIFICATES / "curved_curvature_state_gauge_chain_map.json"
IDENTITY = CERTIFICATES / "curved_curvature_identity_chain_map.json"
SUBSIDIARY = CERTIFICATES / "curved_weyl_cotton_hyperbolic.json"
OUTPUT = CERTIFICATES / "curved_expanded_relative_witness_rank34_module.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path}")
    return value


def _rejects(
    audit: ExpandedRelativeRank34Module,
    state_gauge: dict[str, object],
    identity: dict[str, object],
    subsidiary: dict[str, object],
) -> bool:
    try:
        audit.certificate(
            state_gauge_certificate=state_gauge,
            identity_chain_certificate=identity,
            subsidiary_certificate=subsidiary,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-rank34-green", action="store_true")
    args = parser.parse_args()
    if args.claim_rank34_green:
        raise SystemExit(
            "REFUSED: the rank-fourteen field cokernel has no projector-free "
            "induced Green inverse"
        )

    state_gauge = _load(STATE_GAUGE)
    identity = _load(IDENTITY)
    subsidiary = _load(SUBSIDIARY)
    audit = ExpandedRelativeRank34Module.build()
    certificate = audit.certificate(
        state_gauge_certificate=state_gauge,
        identity_chain_certificate=identity,
        subsidiary_certificate=subsidiary,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    submodule = certificate["local_differential_submodule"]
    recursive = certificate["presented_submodule_recursive_inverse"]
    quotient = certificate["quotient_presentation"]
    algebra = certificate["off_diagonal_algebra"]
    boundary = certificate["precise_remaining_obstruction"]
    checks = {
        "rank34_exact": certificate["rank34_component"]["rank"] == 34,
        "rank12_intertwiner": submodule["presentation_rank"] == 12
        and submodule["intertwining_defect"] == 0,
        "local_K_origin": submodule["Noether_origin"].startswith("B_vector"),
        "no_projector": not submodule["pointwise_or_helicity_projector_used"],
        "submodule_left_inverse": recursive["left_inverse_defect"] == 0,
        "submodule_right_inverse": recursive["right_inverse_defect"] == 0,
        "quotient_rank22": quotient["quotient_rank"] == 22,
        "constraint_quotient_closed": quotient["constraint_quotient_rank"] == 8
        and quotient["constraint_quotient_symmetric_hyperbolic"],
        "C1_descends": quotient["C1_descends_to_field_cokernel"],
        "physical_intertwiner_open": not quotient[
            "C1_induced_biwave_intertwiner_constructed"
        ],
        "raw_ideal_not_nilpotent": not algebra["raw_ideal_nilpotent"]
        and algebra["R_squared_trace"] != "0",
        "rank34_still_open": not boundary["rank34_Green_inverse_constructed"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_state = deepcopy(state_gauge)
        bad_state["T_state_K_aux_exact"] = False
        bad_identity = deepcopy(identity)
        bad_identity["second_chain_relation_exact"] = False
        bad_subsidiary = deepcopy(subsidiary)
        bad_subsidiary["exact_sourced_subsidiary_operator_identity"] = False
        checks.update(
            {
                "broken_C1_gauge_identity_rejected": _rejects(
                    audit, bad_state, identity, subsidiary
                ),
                "broken_Bianchi_square_rejected": _rejects(
                    audit, state_gauge, bad_identity, subsidiary
                ),
                "broken_sourced_identity_rejected": _rejects(
                    audit, state_gauge, identity, bad_subsidiary
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RANK-34 MODULE: {sum(checks.values())}/{len(checks)} PASS")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
