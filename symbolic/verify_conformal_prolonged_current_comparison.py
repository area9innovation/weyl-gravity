#!/usr/bin/env python3
"""Verify the all-row curvature-prolonged BV current comparison."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_current.prolonged_current_comparison import (
    ProlongedCurrentComparison,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_prolonged_current_comparison.json"


def _load(name: str) -> dict[str, object]:
    return json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))


def _build(**overrides: object) -> ProlongedCurrentComparison:
    inputs: dict[str, object] = {
        "auxiliary_current_certificate": _load("curved_current_comparison.json"),
        "graph_current_certificate": _load("curved_curvature_graph_current.json"),
        "mapping_cylinder_certificate": _load(
            "curved_curvature_mapping_cylinder_substitution.json"
        ),
    }
    inputs.update(overrides)
    return ProlongedCurrentComparison.build(**inputs)  # type: ignore[arg-type]


def main() -> int:
    result = _build()
    certificate = result.certificate(reverify=False)

    broken_mapping = _load("curved_curvature_mapping_cylinder_substitution.json")
    broken_mapping["kernel"]["odd_BV_cyclicity_defect"] = 1
    try:
        _build(mapping_cylinder_certificate=broken_mapping)
    except AssertionError:
        cyclicity_mutation_rejected = True
    else:
        cyclicity_mutation_rejected = False

    broken_auxiliary = _load("curved_current_comparison.json")
    broken_auxiliary["closure"]["gauge_fixing_nonminimal"]["all_rows"][
        "Weyl_nonminimal"
    ] = False
    try:
        _build(auxiliary_current_certificate=broken_auxiliary)
    except AssertionError:
        missing_row_rejected = True
    else:
        missing_row_rejected = False

    broken_graph = _load("curved_curvature_graph_current.json")
    broken_graph["exact_identities"][
        "I_pullback_omega_parent_minus_omega_aux"
    ] = "nonzero"
    try:
        _build(graph_current_certificate=broken_graph)
    except AssertionError:
        current_identity_mutation_rejected = True
    else:
        current_identity_mutation_rejected = False

    broken_hessian = [row[:] for row in result.pulled_back_master_hessian]
    broken_hessian[1][1] = broken_hessian[1][1] + OperatorPolynomial.identity()
    try:
        replace(result, pulled_back_master_hessian=broken_hessian).verify(
            reverify_kernel=False
        )
    except AssertionError:
        pullback_mutation_rejected = True
    else:
        pullback_mutation_rejected = False

    OUTPUT.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    exact = certificate["exact_matrix_identities"]
    transgression = certificate["variational_transgression"]
    ledger = certificate["all_row_ledger"]
    support = certificate["support"]
    guards = {
        "quadratic_parent_is_coefficientwise_complete": certificate[
            "quadratic_BV_parent"
        ]["coefficientwise_complete"],
        "all_16_blocks_are_present": len(
            certificate["quadratic_BV_parent"]["all_16_blocks"]
        ) == 16,
        "master_action_restricts_to_auxiliary": exact[
            "Isharp_Hprol_I_minus_Haux"
        ] == "zero",
        "prolonged_Q_is_nilpotent": exact["Qprol_squared"] == "zero",
        "prolonged_Q_is_odd_cyclic": exact[
            "Qprol_odd_cyclicity_defect"
        ] == "zero",
        "off_shell_d_plus_Q_identity": transgression["off_shell"]
        and transgression["d_plus_Q_form"].endswith(
            "beta=delta Y_I, gamma=0"
        ),
        "compatible_current_is_exact": transgression[
            "compatible_current_identity"
        ] == "I^*omega_prol^comp-omega_aux=0",
        "no_rows_silently_dropped": ledger["silent_rows_dropped"] == 0
        and all(
            ledger[name]
            for name in (
                "degree_ledger_complete",
                "fields_and_curvature_fields",
                "equation_and_identity_rows",
                "antifield_and_identity_antifield_rows",
                "trace_Weyl_and_nonminimal_rows",
            )
        ),
        "support_local_in_all_categories": all(
            support[name]
            for name in ("compact", "spacelike_compact", "smooth_global")
        ),
        "no_nonlocal_inverse_or_Green_input": not any(
            support[name]
            for name in (
                "inverse_Laplacian",
                "inverse_curl",
                "spectral_projector",
                "Green_operator",
            )
        ),
        "PDE_symmetrizer_not_conflated": not certificate[
            "pairing_separation"
        ]["identified_with_each_other"],
        "cyclicity_mutation_rejected": cyclicity_mutation_rejected,
        "missing_auxiliary_row_rejected": missing_row_rejected,
        "current_identity_mutation_rejected": (
            current_identity_mutation_rejected
        ),
        "pullback_mutation_rejected": pullback_mutation_rejected,
        "prolonged_current_flag_warranted": certificate[
            "prolonged_current_comparison"
        ]
        and certificate["warranted_atomic_flags"]
        == ["prolonged_current_comparison"],
    }
    for name, passed in guards.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {OUTPUT.relative_to(ROOT)}")
    print(
        "PROLONGED CURRENT COMPARISON GUARDS: "
        f"{sum(guards.values())}/{len(guards)} PASS"
    )
    return 0 if all(guards.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
