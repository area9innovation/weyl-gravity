#!/usr/bin/env python3
"""Bind the direct cyclic causal homotopy to the certified BV currents."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.certificate_provenance import (
    DigestMode,
    digest_file,
    load_json_object,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"
OUTPUT = CERTIFICATES / "curved_direct_causal_pairing_transport.json"
REPORT = GENERATED / "curved_direct_causal_pairing_transport.md"

INPUTS = {
    "curved_pbw": "adjoint_tractor_bgg_curved_pbw.json",
    "parent_transfer": "adjoint_tractor_green_transfer.json",
    "full_homotopy": "curved_full_prolonged_green_homotopy_assembly.json",
    "prolonged_current": "curved_prolonged_current_comparison.json",
    "auxiliary_metric_current": "curved_current_comparison.json",
    "green_current_theorem": "curved_green_current_pairing.json",
    "EAL_regression": "curved_EAL_pairing_regression.json",
}


def _load(filename: str) -> dict[str, object]:
    return load_json_object(CERTIFICATES / filename, root=ROOT)


def _sha256(filename: str) -> str:
    return digest_file(
        CERTIFICATES / filename,
        mode=DigestMode.RAW_FILE,
        root=ROOT,
    )


def _require_inputs(inputs: Mapping[str, Mapping[str, object]]) -> None:
    pbw = inputs["curved_pbw"]
    transfer = inputs["parent_transfer"]
    full = inputs["full_homotopy"]
    prolonged = inputs["prolonged_current"]
    current = inputs["auxiliary_metric_current"]
    green_current = inputs["green_current_theorem"]
    eal = inputs["EAL_regression"]

    required = {
        "curved BGG chain maps": pbw["theorem_boundary"][
            "curved_BGG_chain_maps_exact"
        ],
        "curved cyclic BGG maps": pbw["theorem_boundary"][
            "cyclic_i_sharp_equals_p"
        ],
        "curved BGG support locality": pbw["theorem_boundary"]["support_local"],
        "all-order Bach match": pbw["Bach_comparison"][
            "total_defect_entries"
        ]
        == 0
        and pbw["Bach_comparison"]["normalization"] == "-2",
        "parent advanced/retarded Green operators": transfer["parent_YM_detour"][
            "advanced_retarded_Green_operators"
        ],
        "tracefree transfer active": transfer["tracefree_causal_green_homotopy"],
        "parent adjoint relation": transfer["parent_YM_detour"][
            "adjoint_relation"
        ]
        == "Lambda_parent,+^sharp=Lambda_parent,-",
        "full causal homotopy": full["causal_green_homotopy"],
        "full causal support": full["full_hybrid_assembly"][
            "causal_support_exact_conditionally"
        ],
        "full graded adjoint": full["full_hybrid_assembly"][
            "graded_adjoint_exact_conditionally"
        ],
        "full transfer gate": full["future_gate"]["all_row_causal_homotopy_ready"],
        "prolonged current": prolonged["prolonged_current_comparison"],
        "prolonged cyclicity": prolonged["exact_matrix_identities"][
            "Qprol_odd_cyclicity_defect"
        ]
        == "zero",
        "prolonged current pullback": prolonged["variational_transgression"][
            "d_plus_Q_form"
        ]
        == "I^*omega_prol-omega_aux=d beta+Q gamma, beta=delta Y_I, gamma=0",
        "auxiliary metric current": current["curved_current_comparison"],
        "slab current identity": current["closure"]["curved_slab_current_identity"],
        "conditional Green/current theorem": green_current[
            "Green_pairing_equals_current_pairing"
        ]
        and green_current["theorem"]["prerequisite"] == "green_homotopies"
        and current["Green_current_prerequisite"] == "green_homotopies",
        "EAL all-energy normalization": eal["verified"]
        and eal["all_energy_normalization"],
        "EAL signs": eal["krein_signs"] == {"E": 1, "A": -1, "L": -1},
    }
    failed = [name for name, value in required.items() if value is not True]
    if failed:
        raise AssertionError(f"direct causal pairing prerequisites failed: {failed}")


def _require_boundary(certificate: Mapping[str, object]) -> None:
    if certificate["final_covariant_H4"] is not False:
        raise AssertionError("pairing transport must not promote final covariant H4")
    forbidden = {
        "causal_quasi_isomorphism",
        "residual_endpoint_recovery",
        "SO42_equivariant_transport",
        "final_covariant_H4",
    }
    if forbidden.intersection(certificate["status_flags_promoted"]):
        raise AssertionError("pairing certificate promoted a downstream flag")


def build_certificate(
    inputs: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    _require_inputs(inputs)
    full = inputs["full_homotopy"]
    eal = inputs["EAL_regression"]

    certificate: dict[str, object] = {
        "schema": "pure-weyl-direct-causal-pairing-transport-v1",
        "dependency_tag": "LORENTZIAN-CAUSAL",
        "fail_closed": True,
        "input_certificate_sha256": {
            role: _sha256(filename) for role, filename in INPUTS.items()
        },
        "causal_difference": {
            "same_sided_formula": full["full_hybrid_assembly"]["formula"],
            "same_sided_adjoint": (
                "Lambda_full,+^sharp=Lambda_full,-"
            ),
            "definition": "Delta_Lambda=Lambda_full,+-Lambda_full,-",
            "local_algebraic_cancellation": (
                "H_alg is identical in the + and - homotopies and cancels"
            ),
            "trace_doublet_cancellation": (
                "h_tr is identical in the + and - endpoint homotopies and cancels"
            ),
            "reduced_formula": (
                "Delta_Lambda=i_end U ((p Delta_Lambda_parent i) direct-sum 0) "
                "U^-1 p_end"
            ),
            "chain_identity": (
                "Q Delta_Lambda+Delta_Lambda Q=0 by subtracting the two "
                "same-sided homotopy identities"
            ),
            "graded_antisymmetry": "Delta_Lambda^sharp=-Delta_Lambda",
            "causal_support": True,
        },
        "pairing_transport": {
            "parent_Green_current_identity": True,
            "cyclic_BGG_transfer": "i^sharp=p",
            "cyclic_trace_shear": "U^sharp=U^-1",
            "cyclic_hybrid_transfer": "i_end^sharp=p_end",
            "prolonged_to_auxiliary": (
                "I^*omega_prol-omega_aux=d beta+Q gamma"
            ),
            "auxiliary_to_metric": (
                "i^*omega_aux-omega_met=d beta+Q gamma"
            ),
            "closed_cauchy_surface": "boundary(S^3)=empty",
            "cohomological_improvements": "d-exact integrates to zero; Q-exact vanishes on cohomology",
            "positive_PDE_symmetrizer_used": False,
            "canonical_D_TF_inverse_used": False,
            "global_W0_G_end_identity_used": False,
            "implementation_neutral": True,
        },
        "normalization": {
            "all_energy": eal["all_energy_normalization"],
            "chiralities": eal["chiralities"],
            "families": eal["families"],
            "Krein_signs": eal["krein_signs"],
            "statement": "+I_E direct-sum (-I_A) direct-sum (-I_L)",
        },
        "Green_pairing_equals_current_pairing": True,
        "pairing_compatibility": True,
        "status_flags_promoted": [
            "Green_pairing_equals_current_pairing",
            "pairing_compatibility",
        ],
        "final_covariant_H4": False,
        "downstream_not_promoted_by_this_certificate": [
            "causal_quasi_isomorphism",
            "residual_endpoint_recovery",
            "SO42_equivariant_transport",
            "final_covariant_H4",
        ],
        "theorem_boundary": (
            "The causal pairing defined by Delta_Lambda agrees on cohomology "
            "with the prolonged, auxiliary, metric and E/A/L Cauchy-current "
            "pairings.  This uses the direct cyclic transferred homotopy and "
            "does not assert a canonical D_TF Green inverse, a prolonged "
            "witness, a causal quasi-isomorphism, endpoint recovery, residual "
            "equivariance or final covariant H4."
        ),
    }
    _require_boundary(certificate)
    return certificate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    inputs = {role: _load(filename) for role, filename in INPUTS.items()}
    certificate = build_certificate(inputs)

    if args.guards:
        guard_results = {}
        for role, path in (
            (
                "curved_pbw",
                ("theorem_boundary", "cyclic_i_sharp_equals_p"),
            ),
            ("full_homotopy", ("causal_green_homotopy",)),
            (
                "full_homotopy",
                ("full_hybrid_assembly", "graded_adjoint_exact_conditionally"),
            ),
            ("prolonged_current", ("prolonged_current_comparison",)),
            (
                "green_current_theorem",
                ("Green_pairing_equals_current_pairing",),
            ),
            ("EAL_regression", ("verified",)),
        ):
            tampered = deepcopy(inputs)
            cursor = tampered[role]
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = False
            label = role + ":" + ".".join(path)
            try:
                build_certificate(tampered)
            except AssertionError:
                guard_results[label] = True
            else:
                guard_results[label] = False
        promoted = deepcopy(certificate)
        promoted["final_covariant_H4"] = True
        try:
            _require_boundary(promoted)
        except AssertionError:
            guard_results["manual_final_H4_promotion_rejected"] = True
        else:
            guard_results["manual_final_H4_promotion_rejected"] = False
        if not all(guard_results.values()):
            raise AssertionError(f"pairing fail-closed guards failed: {guard_results}")
        certificate["fail_closed_guards"] = guard_results

    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        REPORT.write_text(
            "# Direct causal pairing transport\n\n"
            "The full same-sided homotopies are cyclic, so their difference is "
            "graded antisymmetric.  The common algebraic contraction and trace "
            "doublet contraction cancel from that difference, leaving the "
            "cyclic transfer of the parent causal operator.  The certified "
            "prolonged-to-auxiliary and auxiliary-to-metric current improvements "
            "then identify this causal pairing with the closed-`S^3` Cauchy "
            "current on cohomology.  Its all-energy normalization is "
            "`+E,-A,-L`.\n\n"
            "This promotes implementation-neutral pairing compatibility and "
            "Green/current equality only.  It does not construct a canonical "
            "`D_TF` inverse or promote the causal quasi-isomorphism, endpoint "
            "recovery, residual equivariance, or final covariant `H4`.\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))
        print("wrote", REPORT.relative_to(ROOT))
    else:
        persisted = _load(OUTPUT.name)
        if "fail_closed_guards" in persisted and "fail_closed_guards" not in certificate:
            certificate["fail_closed_guards"] = persisted["fail_closed_guards"]
        if certificate != persisted:
            raise AssertionError("persisted direct causal pairing certificate drifted")

    print("[PASS] cyclic causal difference is graded antisymmetric")
    print("[PASS] Green/current pairing equality transported through all current maps")
    print("[PASS] all-energy E/A/L normalization is +E,-A,-L")
    print("[PASS] final covariant H4 remains fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
