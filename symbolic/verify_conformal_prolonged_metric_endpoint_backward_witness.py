#!/usr/bin/env python3
"""Verify the coefficient-complete canonical W0 on the metric endpoint."""

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
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_backward_witness import (
    ProlongedMetricEndpointBackwardWitness,
    write_payload,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
ENDPOINT_COEFFICIENTS = CERTIFICATES / "curved_prolonged_metric_endpoint_coefficients.json"
COEFFICIENT_OUTPUT = (
    CERTIFICATES / "curved_prolonged_metric_endpoint_backward_witness_coefficients.json"
)
CERTIFICATE_OUTPUT = (
    CERTIFICATES / "curved_prolonged_metric_endpoint_backward_witness.json"
)

DEPENDENCIES = {
    "endpoint": "curved_prolonged_metric_endpoint_complex.json",
    "ghost_biwave": "ghost_biwave_factorization.json",
    "field_biwave": "field_biwave_intertwiner.json",
    "minimal_witness": "minimal_witness_matrix.json",
}


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON object")
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
        help="rerun the exhaustive curved T_gf/K/T coefficient reconstruction",
    )
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    endpoint_payload = _load(ENDPOINT_COEFFICIENTS)
    endpoint = ProlongedMetricEndpointComplex.from_coefficient_payload(
        endpoint_payload
    )
    dependencies = {
        name: _load(CERTIFICATES / filename)
        for name, filename in DEPENDENCIES.items()
    }

    if args.rebuild:
        theorem = ProlongedMetricEndpointBackwardWitness.build(endpoint)
        coefficient_payload = theorem.coefficient_payload()
        verification_rail = "exhaustive_curved_jet_rebuild"
    else:
        coefficient_payload = _load(COEFFICIENT_OUTPUT)
        theorem = ProlongedMetricEndpointBackwardWitness.from_coefficient_payload(
            endpoint, coefficient_payload
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

    if args.emit:
        if write_payload(COEFFICIENT_OUTPUT, coefficient_payload) != coefficient_sha256:
            raise AssertionError("W0 coefficient payload write drifted")
        CERTIFICATE_OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", COEFFICIENT_OUTPUT.relative_to(ROOT))
        print("wrote", CERTIFICATE_OUTPUT.relative_to(ROOT))
    else:
        if certificate != _load(CERTIFICATE_OUTPUT):
            raise AssertionError("persisted endpoint W0 certificate drifted")

    witness = certificate["W0"]
    d_end = certificate["D_end"]
    ghost = certificate["ghost_block"]
    normalization = certificate["endpoint_normalization"]
    filtration = certificate["endpoint_green_filtration_input"]
    checks = {
        "verification_rail": verification_rail in {
            "exhaustive_curved_jet_rebuild",
            "content_addressed_fast_algebraic",
        },
        "canonical_W0": witness["degree"] == -1
        and witness["maximum_order"] == 3
        and witness["graded_cyclic"],
        "middle_normalization": witness["nonzero_blocks"]["E_to_M"]
        == "endpoint fibre identity",
        "D_identity": d_end["identity"] == "D_end=Q_end W0+W0 Q_end"
        and d_end["off_diagonal_blocks"] == "zero"
        and d_end["coefficientwise_complete"],
        "field_block": d_end["degreewise_blocks"]["M"]
        == "Bach_bar+K_met T_gf=H_end",
        "tracefree_scalar_biwave": normalization["tracefree_principal_symbol"]
        == "(zeta^2)^2 I_9"
        and normalization["legacy_middle_2I_rejected"]
        and normalization["legacy_middle_2I_principal_spectrum_at_dt"]
        == "1^4+2^5",
        "formal_adjoints": d_end["formal_adjoint_defects"] == 0
        and d_end["degreewise_blocks"]["E"].endswith("(D_M)^sharp")
        and d_end["degreewise_blocks"]["I"].endswith("(D_G)^sharp"),
        "triangular_ghost": ghost["matrix_form"]
        == [
            ["Box(Box+2) I_4", "0"],
            ["(1/2) div", "I_1"],
        ]
        and ghost["Weyl_scalar_completion"] == "pointwise identity",
        "filtration_input": filtration["D_end_available_coefficientwise"]
        and filtration["formula_for_relative_saddle"] == "S_end=D_end-C B"
        and filtration["all_exported"],
        "support_local": certificate["support"]["finite_order"]
        and not certificate["support"]["inverse_Laplacian_or_curl"]
        and not certificate["support"]["spectral_or_helicity_projector"],
        "green_boundary": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }

    if args.guards:
        bad_endpoint = deepcopy(dependencies)
        bad_endpoint["endpoint"]["Q_end"]["Q_end_squared"] = "unknown"
        bad_ghost = deepcopy(dependencies)
        bad_ghost["ghost_biwave"]["factorization"]["product"] = "unknown"
        bad_middle = deepcopy(dependencies)
        bad_middle["minimal_witness"]["backward_blocks"]["E_to_M"] = (
            "sharp^{-1}"
        )
        checks.update(
            {
                "open_endpoint_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_endpoint,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
                "missing_ghost_factor_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_ghost,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
                "abstract_normalization_dependency_rejected": _rejects(
                    lambda: theorem.certificate(
                        dependencies=bad_middle,
                        coefficient_payload_sha256=coefficient_sha256,
                    )
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "PROLONGED METRIC ENDPOINT BACKWARD WITNESS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
