#!/usr/bin/env python3
"""Verify and emit the exact thirty-row prolonged metric endpoint."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
    write_coefficient_payload,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
CERTIFICATE_OUTPUT = CERTIFICATES / "curved_prolonged_metric_endpoint_complex.json"
COEFFICIENT_OUTPUT = (
    CERTIFICATES / "curved_prolonged_metric_endpoint_coefficients.json"
)


DEPENDENCY_FILES = {
    "linearized_bach": "linearized_bach.json",
    "curved_retract": "curved_deformation_retract_status.json",
    "curved_core_chain": "curved_core_curvature_chain_map.json",
    "mapping_substitution": "curved_curvature_mapping_cylinder_substitution.json",
    "hybrid_projector": "curved_prolonged_hybrid_algebraic_projector.json",
    "curvature_equation": "curved_curvature_auxiliary_chain_map.json",
}


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not a JSON object")
    return value


def _rejects(action) -> bool:
    try:
        action()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="rerun the exhaustive 1,050-jet coefficient reconstruction",
    )
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    dependencies = {
        name: _load(filename) for name, filename in DEPENDENCY_FILES.items()
    }
    if args.rebuild:
        theorem = ProlongedMetricEndpointComplex.build()
        coefficient_payload = theorem.coefficient_payload()
        verification_rail = "exhaustive_curved_jet_rebuild"
    else:
        coefficient_payload = _load(COEFFICIENT_OUTPUT.name)
        theorem = ProlongedMetricEndpointComplex.from_coefficient_payload(
            coefficient_payload
        )
        verification_rail = "content_addressed_fast_algebraic"
    coefficient_text = json.dumps(
        coefficient_payload, indent=2, sort_keys=True
    ) + "\n"
    coefficient_sha256 = hashlib.sha256(
        coefficient_text.encode("utf-8")
    ).hexdigest()
    certificate = theorem.certificate(
        dependencies=dependencies,
        coefficient_payload_sha256=coefficient_sha256,
    )

    if not args.emit:
        persisted = _load(CERTIFICATE_OUTPUT.name)
        # The verification rail is operational metadata, not a theorem
        # field, so exact equality is expected on both rails.
        if certificate != persisted:
            raise AssertionError("persisted endpoint certificate drifted")

    if args.emit:
        written_digest = write_coefficient_payload(
            COEFFICIENT_OUTPUT, coefficient_payload
        )
        if written_digest != coefficient_sha256:
            raise AssertionError("coefficient payload write digest drifted")
        CERTIFICATE_OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", COEFFICIENT_OUTPUT.relative_to(ROOT))
        print("wrote", CERTIFICATE_OUTPUT.relative_to(ROOT))

    ledger = certificate["ordered_endpoint_ledger"]
    q_end = certificate["Q_end"]
    maps = certificate["local_graph_maps"]
    cyclicity = certificate["cyclicity"]
    boundary = certificate["curved_vs_regression_boundary"]
    checks = {
        "verification_rail": verification_rail in {
            "exhaustive_curved_jet_rebuild",
            "content_addressed_fast_algebraic",
        },
        "ordered_30_rows": sum(row["dimension"] for row in ledger) == 30
        and [row["degree"] for row in ledger] == [-1, 0, 1, 2]
        and [row["dimension"] for row in ledger] == [5, 10, 10, 5],
        "coefficient_complete_Q": q_end[
            "all_curved_lower_order_coefficients_emitted"
        ]
        and q_end["maximum_orders"] == [1, 4, 1]
        and q_end["Q_end_squared"] == "zero",
        "endpoint_cyclicity": q_end["formal_adjoint_defects"] == 0
        and q_end["odd_cyclicity_defect"] == 0
        and cyclicity["endpoint_Q_odd_cyclicity_defect"] == 0,
        "graph_inclusion_explicit": maps["j_end"]["formula"]
        == "I_cyl I_aux"
        and maps["j_end"]["maximum_order"] == 3
        and maps["j_end"]["all_Y_and_dual_X/Y_blocks"] == "zero",
        "graph_projection_explicit": maps["p_end"]["formula"]
        == "P_aux P_cyl"
        and maps["p_end"][
            "cotangent_coefficients_forced_by_BV_canonical_adjoint"
        ],
        "graph_SDR": maps["identities"]["p_end_j_end"] == "identity_30"
        and maps["identities"]["Q_prol_j_end"] == "j_end_Q_end"
        and maps["identities"]["p_end_Q_prol"] == "Q_end_p_end"
        and maps["identities"]["j_end_p_end"] == "P_end",
        "support_local": maps["support"]["finite_order_differential"]
        and maps["support"]["pointwise_inverses_only"]
        and not maps["support"]["inverse_Weyl_Laplacian_or_curl"]
        and not maps["support"]["Fourier_or_harmonic_projector"],
        "actual_curved_not_regression": not boundary[
            "Fourier_66x66_matrices_used_as_curved_coefficients"
        ]
        and len(boundary["actual_curved_sources"]) == 5,
        "green_boundary": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }

    if args.guards:
        bad_retract = deepcopy(dependencies)
        bad_retract["curved_retract"]["promotion_criteria"][
            "actual_curved_Q_conjugation_verified"
        ] = False
        bad_mapping = deepcopy(dependencies)
        bad_mapping["mapping_substitution"]["kernel"]["P_I"] = "unknown"
        bad_hybrid = deepcopy(dependencies)
        bad_hybrid["hybrid_projector"]["minimal_dimension_ledger"][
            "retained_metric_curvature_graph"
        ] = 66
        checks.update(
            {
                "flat_only_retract_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_retract,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
                "incomplete_mapping_kernel_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_mapping,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
                "wrong_endpoint_rank_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_hybrid,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "PROLONGED METRIC ENDPOINT COMPLEX: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
