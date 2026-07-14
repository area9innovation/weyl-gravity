#!/usr/bin/env python3
"""Verify coefficient substitution into the curvature cotangent cylinder."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_mapping_cylinder_substitution import (
    CurvatureMappingCylinderSubstitution,
)


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"
STATE_GAUGE = CERTIFICATE_DIR / "curved_curvature_state_gauge_chain_map.json"
LINEARIZED_BACH = CERTIFICATE_DIR / "linearized_bach.json"
EQUATION = CERTIFICATE_DIR / "curved_curvature_auxiliary_chain_map.json"
IDENTITY = CERTIFICATE_DIR / "curved_curvature_identity_chain_map.json"
RETRACT = CERTIFICATE_DIR / "curved_chain_maps.json"
KERNEL = CERTIFICATE_DIR / "curved_curvature_mapping_cylinder_kernel.json"
COTANGENT = CERTIFICATE_DIR / "curved_prolonged_bv_differential_audit.json"
OUTPUT = CERTIFICATE_DIR / "curved_curvature_mapping_cylinder_substitution.json"


def _load(path: Path) -> dict[str, object]:
    if not path.exists():
        raise AssertionError(f"required certificate is absent: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path.relative_to(ROOT)}")
    return value


def _rejects(
    state_gauge: dict[str, object],
    linearized_bach: dict[str, object],
    equation: dict[str, object],
    identity: dict[str, object],
    retract: dict[str, object],
    kernel: dict[str, object],
    cotangent: dict[str, object],
) -> bool:
    try:
        CurvatureMappingCylinderSubstitution(
            state_gauge,
            linearized_bach,
            equation,
            identity,
            retract,
            kernel,
            cotangent,
        ).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    state_gauge = _load(STATE_GAUGE)
    linearized_bach = _load(LINEARIZED_BACH)
    equation = _load(EQUATION)
    identity = _load(IDENTITY)
    retract = _load(RETRACT)
    kernel = _load(KERNEL)
    cotangent = _load(COTANGENT)
    audit = CurvatureMappingCylinderSubstitution(
        state_gauge,
        linearized_bach,
        equation,
        identity,
        retract,
        kernel,
        cotangent,
    )
    certificate = audit.certificate()

    broken_a_order = deepcopy(equation)
    broken_a_order["A_equation"]["maximum_order"] = 3
    broken_a_hash = deepcopy(equation)
    broken_a_hash["A_equation"]["sha256"] = "not-a-digest"
    broken_first_square = deepcopy(equation)
    broken_first_square["first_chain_relation_exact"] = False
    broken_b_rank = deepcopy(identity)
    broken_b_rank["B_identity"]["rank"] = 3
    broken_second_square = deepcopy(identity)
    broken_second_square["second_chain_relation_exact"] = False
    broken_degree = deepcopy(kernel)
    broken_degree["degree_checks"][
        "every_split_Q_arrow_raises_degree_by_one"
    ] = False
    broken_pairing = deepcopy(kernel)
    broken_pairing["mapping_cylinder"]["BV_pairing_defect"] = 1
    broken_state_gauge = deepcopy(state_gauge)
    broken_state_gauge["T_state_K_aux_exact"] = False
    broken_bach_input = deepcopy(linearized_bach)
    broken_bach_input["gauge_jet_test"]["exhaustive"] = False
    broken_h_link = deepcopy(identity)
    broken_h_link["A_metric"]["tracefree_Bach_to_curvature_sha256"] = "f" * 64
    broken_projection_link = deepcopy(identity)
    broken_projection_link["identity_projection"][
        "full_retract_projection_sha256"
    ] = "e" * 64
    broken_cotangent = deepcopy(cotangent)
    broken_cotangent["exact_results"]["cotangent_adjoint_Q_squared"] = False

    mutations = {
        "wrong_A_order_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_a_order,
            identity,
            retract,
            kernel,
            cotangent,
        ),
        "bad_A_hash_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_a_hash,
            identity,
            retract,
            kernel,
            cotangent,
        ),
        "broken_first_square_rejected": _rejects(
            state_gauge,
            linearized_bach,
            broken_first_square,
            identity,
            retract,
            kernel,
            cotangent,
        ),
        "wrong_B_rank_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_b_rank,
            retract,
            kernel,
            cotangent,
        ),
        "broken_second_square_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_second_square,
            retract,
            kernel,
            cotangent,
        ),
        "broken_degree_ledger_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            identity,
            retract,
            broken_degree,
            cotangent,
        ),
        "broken_BV_pairing_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            identity,
            retract,
            broken_pairing,
            cotangent,
        ),
        "broken_state_gauge_square_rejected": _rejects(
            broken_state_gauge,
            linearized_bach,
            equation,
            identity,
            retract,
            kernel,
            cotangent,
        ),
        "incomplete_Bach_gauge_jets_rejected": _rejects(
            state_gauge,
            broken_bach_input,
            equation,
            identity,
            retract,
            kernel,
            cotangent,
        ),
        "A_B_H_hash_mismatch_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_h_link,
            retract,
            kernel,
            cotangent,
        ),
        "retract_projection_hash_mismatch_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            broken_projection_link,
            retract,
            kernel,
            cotangent,
        ),
        "broken_cotangent_audit_rejected": _rejects(
            state_gauge,
            linearized_bach,
            equation,
            identity,
            retract,
            kernel,
            broken_cotangent,
        ),
    }

    OUTPUT.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = {
        "coefficientwise_complete": certificate[
            "coefficientwise_complete_prolonged_Q"
        ],
        "support_local": certificate["support_local"],
        "all_new_blocks_accounted_for": certificate["substitution"][
            "all_new_blocks_accounted_for"
        ],
        "formal_adjoints_forced": certificate["substitution"][
            "formal_adjoint_tables_generated_from_primal_tables"
        ],
        "first_chain_square": certificate["substitution"][
            "first_chain_relation_exact"
        ],
        "second_chain_square": certificate["substitution"][
            "second_chain_relation_exact"
        ],
        "Q_squared": certificate["kernel"]["Q_squared"] == "zero",
        "BV_pairing": certificate["kernel"]["BV_pairing_defect"] == 0,
        "odd_BV_cyclicity": certificate["kernel"][
            "odd_BV_cyclicity_defect"
        ] == 0,
        "SDR_identity": certificate["kernel"]["I_P_minus_identity"] == "QH+HQ",
        "three_adjoint_tables_content_addressed": all(
            len(entry["derived_sha256"]) == 64
            and len(entry["source_pairing_sha256"]) == 64
            and len(entry["target_pairing_sha256"]) == 64
            for entry in certificate["formal_adjoint_provenance"].values()
            if isinstance(entry, dict)
        ),
        "two_atomic_flags_warranted": certificate["warranted_atomic_flags"]
        == [
            "support_local_prolongation_retract",
            "prolonged_BV_operator_identity",
        ],
        "no_status_file_mutation": not certificate["status_flags_promoted"],
        **mutations,
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {OUTPUT.relative_to(ROOT)}")
    print(
        "CURVATURE MAPPING-CYLINDER SUBSTITUTION GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
