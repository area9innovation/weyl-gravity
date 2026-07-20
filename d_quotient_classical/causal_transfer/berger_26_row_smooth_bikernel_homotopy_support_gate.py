#!/usr/bin/env python3
"""Classify support classes for extending the retained Berger homotopy."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-26-row-smooth-bikernel-homotopy-support-gate.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-26-row-smooth-bikernel-homotopy-support-gate-v1.schema.json"
)
VERIFIER = (
    ROOT
    / "d_quotient_classical/causal_transfer/"
    "verify_berger_26_row_smooth_bikernel_homotopy_support_gate.py"
)
TESTS = (
    ROOT
    / "d_quotient_classical/causal_transfer/tests/"
    "test_berger_26_row_smooth_bikernel_homotopy_support_gate.py"
)
DEPENDENCIES = {
    "classical_homotopy": (
        ROOT
        / "d_quotient_classical/certificates/"
        "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json"
    ),
    "classical_proof": (
        ROOT
        / "d_quotient_classical/generated/"
        "berger_26_row_causal_green_homotopy_v2/causal_proof.json"
    ),
    "quantum_Ward_reduction": (
        ROOT
        / "quantum-weyl/lorentzian/certificates/"
        "BERGER_RETAINED26_HADAMARD_WARD_REDUCTION.json"
    ),
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "result_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _support_class_ledger() -> list[dict[str, Any]]:
    common = {
        "background": "M=R_t x Sigma_B with Sigma_B compact",
        "kernel_regularness": "C-infinity(M_x x M_y; Hom(E_y,E_x))",
        "wavefront_set": "EMPTY",
        "topology": (
            "strict LF limit over fixed closed support carriers; each fixed-"
            "carrier space has the induced compact-open C-infinity Frechet "
            "seminorms in both variables"
        ),
    }
    return [
        {
            **common,
            "class_id": "K_PC_X",
            "support_condition": (
                "the x-projection of support is past compact; y is smooth "
                "with compact-open control"
            ),
            "operator": "Lambda26_plus_x=W26_x G26_plus_x",
            "continuous_extension": True,
            "homotopy_identity": (
                "q26_x Lambda26_plus_x+Lambda26_plus_x q26_x=I"
            ),
            "causal_support": (
                "supp(Lambda26_plus_x K) subset "
                "J_plus(pr_x supp K) x M_y"
            ),
            "C26_membership": "NOT_EXPORTED",
        },
        {
            **common,
            "class_id": "K_FC_X",
            "support_condition": (
                "the x-projection of support is future compact; y is smooth "
                "with compact-open control"
            ),
            "operator": "Lambda26_minus_x=W26_x G26_minus_x",
            "continuous_extension": True,
            "homotopy_identity": (
                "q26_x Lambda26_minus_x+Lambda26_minus_x q26_x=I"
            ),
            "causal_support": (
                "supp(Lambda26_minus_x K) subset "
                "J_minus(pr_x supp K) x M_y"
            ),
            "C26_membership": "NOT_EXPORTED",
        },
        {
            **common,
            "class_id": "K_TC_X",
            "support_condition": (
                "the x-projection of support is both past and future compact"
            ),
            "operator": "both Lambda26_plus_x and Lambda26_minus_x",
            "continuous_extension": True,
            "homotopy_identity": "both one-sided identities hold",
            "causal_support": "both declared one-sided estimates hold",
            "C26_membership": "NOT_EXPORTED",
        },
        {
            **common,
            "class_id": "K_SC_X_EQUALS_ALL_SMOOTH",
            "support_condition": (
                "x-spacelike compact; because Sigma_B is compact this is the "
                "full smooth compact-open Frechet space"
            ),
            "operator": "certified factorization W26_x G26_plus_or_minus_x",
            "continuous_extension": False,
            "homotopy_identity": "NOT_AVAILABLE_FROM_CERTIFIED_FACTORIZATION",
            "causal_support": "NO_ONE_SIDED_SOURCE_BOUND",
            "C26_membership": "YES_BY_SMOOTHNESS_ONLY",
        },
    ]


def _cutoff_escape_fixture() -> dict[str, Any]:
    return {
        "background_property": "compact spatial Cauchy surface",
        "homogeneous_row": (
            "choose nonzero smooth h with P26 h=0 from nonzero compact-Cauchy "
            "data"
        ),
        "retarded_sequence": {
            "cutoff": (
                "chi_n(t)=0 for t<=-n-1 and chi_n(t)=1 for t>=-n"
            ),
            "source": "f_n=P26(chi_n h) in C_c-infinity(M;E26)",
            "source_limit": (
                "f_n tends to 0 in the compact-open C-infinity topology "
                "because its support escapes to past infinity"
            ),
            "green_image": "G26_plus f_n=chi_n h by past-compact uniqueness",
            "image_limit": (
                "chi_n h tends to h, which is nonzero, on every fixed compact"
            ),
            "conclusion": (
                "G26_plus has no continuous extension from C_c-infinity to "
                "the full smooth compact-open Frechet space"
            ),
        },
        "advanced_sequence": {
            "cutoff": (
                "reverse cutoff with transition in [n,n+1]"
            ),
            "source": "g_n=P26((1-chi(t-n)) h) in C_c-infinity(M;E26)",
            "source_limit": (
                "g_n tends to 0 in the compact-open C-infinity topology"
            ),
            "green_image": (
                "G26_minus g_n=(1-chi(t-n)) h by future-compact uniqueness"
            ),
            "image_limit": "the image tends to h on every fixed compact",
            "conclusion": (
                "G26_minus has no continuous extension from C_c-infinity to "
                "the full smooth compact-open Frechet space"
            ),
        },
        "scope": (
            "obstructs the certified factorized W26 G26 same-sided "
            "construction on all smooth kernels; it does not rule out a "
            "different noncausal q26-homotopy or a direct equivariant "
            "Hadamard selection"
        ),
    }


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    classical = values["classical_homotopy"]
    proof = values["classical_proof"]
    ward = values["quantum_Ward_reduction"]
    support = classical["support_category"]
    checks = {
        "global_hyperbolicity_certified": support["globally_hyperbolic"] is True,
        "compact_spatial_Cauchy_surface": (
            support["boundary_conditions"]
            == "global Berger cylinder with compact spatial Cauchy surface"
        ),
        "compact_source_domain_only": (
            support["test_function_space"]
            == (
                "compactly supported smooth sources to smooth "
                "advanced/retarded sections"
            )
        ),
        "all_classical_homotopy_rows_verified": all(
            row["status"] == "VERIFIED"
            for row in classical["green_proof_checks"].values()
        ),
        "same_sided_support_proof_present": (
            "same-sided" in proof["support_proof"]["ghost_and_identity"]
            and "same-sided" in proof["support_proof"]["metric_and_antifield"]
        ),
        "cyclic_adjoint_reversal_present": (
            "Lambda26,+^sharp" in proof["cyclicity"]["identity"]
        ),
        "Ward_defect_only_smooth": (
            ward["ward_reduction"]["smooth_defect"]
            == "C26=[H26_plus,q26] is a smooth kernel"
            and ward["smooth_support_class_audit"]["status"]
            == "MISSING_SMOOTH_KERNEL_HOMOTOPY_CARRIER"
        ),
        "Ward_support_profile_absent": (
            set(ward["candidate_status"])
            .isdisjoint(
                {
                    "C26_x_past_compact",
                    "C26_x_future_compact",
                    "C26_x_time_compact",
                    "C26_mode_support",
                }
            )
        ),
    }
    if not all(checks.values()):
        raise AssertionError(
            f"bikernel support inputs drifted: "
            f"{[name for name, ok in checks.items() if not ok]}"
        )

    ledger = _support_class_ledger()
    if [row["continuous_extension"] for row in ledger] != [
        True,
        True,
        True,
        False,
    ]:
        raise AssertionError("support-class disposition drifted")
    return {
        "schema": (
            "pure-weyl-berger-26-row-smooth-bikernel-homotopy-"
            "support-gate-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "ONE_SIDED_BIKERNEL_EXTENSIONS_CERTIFIED_FULL_SMOOTH_"
            "FACTORIZATION_OBSTRUCTED_C26_SUPPORT_PROFILE_REQUIRED"
        ),
        "lifecycle_status": "BLOCKED_ON_TYPED_C26_SUPPORT_PROFILE",
        "dependency_tags": ["LORENTZIAN-CAUSAL"],
        "setting_id": classical["setting_id"],
        "dependencies": {
            name: _artifact(path, values[name])
            for name, path in DEPENDENCIES.items()
        },
        "exact_input_checks": checks,
        "support_classes": ledger,
        "kernel_actions": {
            "first_variable": (
                "(Lambda_x K)(x,y)=Lambda[K(.,y)](x), continuously on the "
                "declared one-sided LF class"
            ),
            "second_variable": (
                "obtained by graded cyclic transpose on the complementary "
                "one-sided class"
            ),
            "cyclic_adjoint": (
                "(Lambda26_plus_x)^sharp is the convention-signed "
                "Lambda26_minus_y on compactly pairing complementary supports"
            ),
            "wavefront": (
                "all declared inputs are smooth, so WF(K)=empty; the extended "
                "Green and local W26 actions preserve smoothness"
            ),
        },
        "positive_fixture": {
            "kernel": "K(x,y)=f(x) tensor g(y), f and g compactly supported",
            "membership": ["K_PC_X", "K_FC_X", "K_TC_X"],
            "homotopy_identity": "VERIFIED_BY_COMPACT_SOURCE_THEOREM",
            "adjoint_pairing": "VERIFIED_BY_COMPACT_SUPPORT_AND_CYCLICITY",
        },
        "negative_fixture": _cutoff_escape_fixture(),
        "C26_import_boundary": {
            "exported": ["smoothness", "empty wavefront set"],
            "not_exported": [
                "x-past-compact support",
                "x-future-compact support",
                "x-time-compact support",
                "y-variable analogues",
                "stationary harmonic/mode support of the smooth remainder",
                "a serialized smooth kernel or pairing-null projection",
            ],
            "current_membership_decision": (
                "C26 belongs to the full smooth class, where the certified "
                "factorized same-sided extension is continuity-obstructed. "
                "Membership in every positive one-sided domain is undecided."
            ),
            "typed_need": "C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER",
        },
        "classification": {
            "past_compact_extension_certified": True,
            "future_compact_extension_certified": True,
            "time_compact_extension_certified": True,
            "cyclic_adjoint_control_certified": True,
            "full_smooth_factorized_extension_certified": False,
            "full_smooth_factorized_extension_obstructed": True,
            "C26_in_positive_extension_domain_certified": False,
            "smooth_Ward_correction_constructed": False,
            "retained_BRST_Hadamard_promoted": False,
            "positivity_or_quantum_claim": False,
        },
        "science_forge": {
            "work_item": (
                "sf:program/work/"
                "classical-bikernel-homotopy-extension-for-q26"
            ),
            "current_gate_status": "BLOCKED_ON_QUANTUM_SUPPORT_EXPORT",
        },
        "next_gate": (
            "IMPORT_C26_SUPPORT_PROFILE_THEN_APPLY_ONE_SIDED_EXTENSION_OR_"
            "CERTIFY_C26_SPECIFIC_SMOOTH_HOMOTOPY_OBSTRUCTION"
        ),
        "claim_boundary": (
            "This LORENTZIAN-CAUSAL support theorem extends the certified "
            "retained-26 advanced/retarded homotopies continuously in the "
            "first kernel variable to the standard past-compact, "
            "future-compact and time-compact smooth LF classes, with empty "
            "wavefront set, same-sided support, the q26 homotopy identity and "
            "graded cyclic adjoint reversal. A cutoff-escape sequence proves "
            "that the certified factorization through G26,+/- has no "
            "continuous extension to the full smooth compact-open Frechet "
            "class on the spatially compact Berger cylinder. The imported "
            "Ward artifact certifies only that C26 is smooth, so it places "
            "C26 in the obstructed full class but does not decide membership "
            "in any positive one-sided domain. No smooth Ward correction, "
            "BRST Hadamard covariance, positivity, particle, Lorentzian QME, "
            "scattering, unitarity or quantum theorem is established."
        ),
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "berger_26_row_smooth_bikernel_homotopy_support_gate "
                    "--check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "verify_berger_26_row_smooth_bikernel_homotopy_support_gate"
                ),
                (
                    "python3 -m unittest d_quotient_classical."
                    "causal_transfer.tests."
                    "test_berger_26_row_smooth_bikernel_homotopy_support_gate"
                ),
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    return f"""# Retained-26 smooth-bikernel homotopy support gate

The certified advanced/retarded homotopies extend continuously in one kernel
variable to the standard past-compact, future-compact and time-compact smooth
LF spaces.  On these domains the same-sided support estimates,

```text
q26 Lambda26,+/- + Lambda26,+/- q26 = I,
```

smoothness and the graded advanced/retarded adjoint reversal all persist.

They do not extend by continuity to the full smooth compact-open Frechet
space.  Let `h` be a nonzero homogeneous solution and move a temporal cutoff
to past infinity.  Then

```text
f_n=P26(chi_n h) -> 0,
G26,+ f_n=chi_n h -> h != 0.
```

The advanced case follows by moving the reversed cutoff to future infinity.
This is a support/topology obstruction to the certified factorization
`Lambda26,+/-=W26 G26,+/-`, not a no-go for a different noncausal homotopy or
a directly equivariant Hadamard selection.

The imported Ward certificate exports only
`C26=[H26_plus,q26] is smooth`.  It supplies no past-, future- or
time-compact support statement in either variable, no harmonic support of the
smooth remainder and no serialized kernel.  Consequently `C26` is known to
belong only to the full smooth class where the factorized extension is
obstructed; membership in every positive one-sided domain is undecided.

CURRENT GATE: BLOCKED — require `C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER`
EVIDENCE: {RESULT_ID}
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = (
        ("full_smooth_factorized_extension_certified", True),
        ("C26_in_positive_extension_domain_certified", True),
        ("smooth_Ward_correction_constructed", True),
        ("retained_BRST_Hadamard_promoted", True),
        ("positivity_or_quantum_claim", True),
    )
    for key, replacement in mutations:
        mutant = deepcopy(value)
        mutant["classification"][key] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value), encoding="utf-8")
        REPORT.write_text(_report(value), encoding="utf-8")
    if args.check and (
        OUTPUT.read_text(encoding="utf-8") != _render(value)
        or REPORT.read_text(encoding="utf-8") != _report(value)
    ):
        raise AssertionError("bikernel support-gate outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
