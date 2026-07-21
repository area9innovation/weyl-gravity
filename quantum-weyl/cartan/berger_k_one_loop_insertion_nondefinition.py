#!/usr/bin/env python3
"""Certify the first missing operator in the Berger one-loop K-Cartan defect."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
OUTPUT = HERE / "certificates/BERGER_K_ONE_LOOP_INSERTION_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-k-one-loop-insertion-nondefinition-v1.schema.json"
REPORT = QROOT / "reports/berger-k-one-loop-insertion-nondefinition-v1.md"
ATLAS_OUTPUT = ROOT / "residual_atlas/positive-berger-k-one-loop-insertion-nondefinition-fragment-v1.json"
ATLAS_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"

PINS = {
    "one_loop_breaking_disposition": {
        "path": "quantum-weyl/anomalies/certificates/BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1.json",
        "source_commit": "30e3c64010a7f28a594ccc1ba4ffd3e59bccdedf",
        "sha256": "43d8602c23180e8910a5bd36f4a96e844722a0961b2cc4b3c12cb82aa3d43365",
    },
    "classical_k_cartan_signoff": {
        "path": "d_quotient_classical/certificates/PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF.json",
        "source_commit": "78b0d7c2e47a9817a9098b617369df2685cf2c30",
        "sha256": "1065c80d6c73ca63c49d7c55368fe9aa7e6284903639ae0a87f4d589d819e3e8",
    },
    "generator_conjugation_audit": {
        "path": "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json",
        "source_commit": "d4e6645f94afe95e4821912d20e0b14656e360ea",
        "sha256": "afc14ea90b10a9a59f0e7d240fcb2231eada9097d1d0e051f8f058d86de3d149",
    },
    "classical_gauge_fixed_cyclic_complex": {
        "path": "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "source_commit": "445e26663d06764bc858ff0a004ba6178acce75f",
        "sha256": "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
    },
    "integration_slice_request": {
        "path": "planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json",
        "source_commit": "30e3c64010a7f28a594ccc1ba4ffd3e59bccdedf",
        "sha256": "74480680cdeb2531aa9c692b19db172b8f8bb17e6cb5148706e978536156b27a",
    },
    "integration_slice_receiver": {
        "path": "quantum-weyl/anomalies/schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json",
        "source_commit": "30e3c64010a7f28a594ccc1ba4ffd3e59bccdedf",
        "sha256": "cc7f638128cf3b68d0eec730710840172b6ae698934d93108b2e83317144582e",
    },
}


def _historical(pin: dict[str, str]) -> bytes:
    return subprocess.run(
        [
            "git",
            "show",
            f"{pin['source_commit']}:physics/symplectic-reconstruction/{pin['path']}",
        ],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


def _load_historical(pin: dict[str, str]) -> dict[str, Any]:
    data = _historical(pin)
    if hashlib.sha256(data).hexdigest() != pin["sha256"]:
        raise ValueError(f"historical input drifted: {pin['path']}")
    return json.loads(data)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    values = {name: _load_historical(pin) for name, pin in PINS.items()}
    breaking = values["one_loop_breaking_disposition"]
    k_signoff = values["classical_k_cartan_signoff"]
    generator = values["generator_conjugation_audit"]
    cyclic = values["classical_gauge_fixed_cyclic_complex"]
    request = values["integration_slice_request"]
    receiver = values["integration_slice_receiver"]

    if (
        breaking["result_state"]
        != "NONDEFINED_MISSING_ACTION_DERIVED_EUCLIDEAN_BV_INTEGRATION_SLICE"
        or breaking["quotient_disposition"]["actual_counterterm"]
        != "NONDEFINED_COEFFICIENTS"
        or any(
            row["prequotient_coefficient"] != "NONDEFINED"
            for row in breaking["coefficient_ledger"]
        )
    ):
        raise ValueError("matter-coupled one-loop predecessor crossed its boundary")
    if (
        not k_signoff["flags"]["K_BERGER_CARTAN_THROUGH_ARITY_THREE"]
        or k_signoff["flags"]["RAW_D_CARTAN_CERTIFIED"]
        or k_signoff["review_scope"]["gauge_fixed_rows"] != 54
    ):
        raise ValueError("wrong classical K-Cartan import")
    if (
        generator["interpretation"]["frozen_e0_generator"]
        != "K=D-omega R"
        or not generator["flags"]["AFFINE_D_ZERO_ARITY_NONZERO"]
        or generator["flags"]["EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D"]
    ):
        raise ValueError("K/raw-D separation drifted")
    if (
        cyclic["row_layout"]["total_rows"] != 54
        or not cyclic["exact_checks"]["gauge_fixed_classical_unary_q1_squared_zero"]
        or not cyclic["exact_checks"]["gauge_fixed_classical_unary_q1_cyclic_by_canonical_transport"]
    ):
        raise ValueError("classical cyclic complex import failed")
    Draft202012Validator.check_schema(receiver)
    if request["body"]["state"] != "REQUESTED":
        raise ValueError("integration-slice request was unexpectedly promoted")

    value = {
        "schema": "quantum-weyl-berger-k-one-loop-insertion-nondefinition-v1",
        "result_id": "BERGER_K_ONE_LOOP_INSERTION_NONDEFINITION_V1",
        "result_state": "NONDEFINED_UPSTREAM_Q1_AND_RENORMALIZED_K_INSERTIONS_ABSENT",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": PINS,
        "setting": {
            "theory": breaking["theory_scope"]["theory"],
            "background": breaking["theory_scope"]["background"],
            "chart": breaking["theory_scope"]["chart"],
            "carrier": "complete 54-row gauge-fixed gravity-clock BV complex",
            "generator": "K_Berger=D-omega R",
            "raw_D": "AFFINE_WITH_NONZERO_ZERO_ARITY_COMPONENT",
        },
        "classical_import": {
            "status": "CERTIFIED_54_ROW_K_CARTAN_THROUGH_ARITY_THREE",
            "Q0": "CERTIFIED",
            "iota_K_0": "CERTIFIED_CLASSICAL",
            "L_K_0": "CERTIFIED_CLASSICAL",
            "cyclic_pairing": "CERTIFIED_CLASSICAL",
            "real_structure": "NOT_EXPORTED_IN_IMPORTED_54_ROW_K_SIGNOFF",
            "K_fixes_background": True,
            "raw_D_fixes_background": False,
        },
        "one_loop_import": {
            "breaking_coefficients": "NONDEFINED",
            "counterterm_coefficients": "NONDEFINED",
            "local_QME": "NOT_RESTORED",
            "H14_even_dimension": 0,
            "H14_odd_dimension": 0,
            "zero_quotient_implication": "CONDITIONAL_REMOVABILITY_ONLY_AFTER_A_REGULATED_CONSISTENT_BREAKING_IS_COMPUTED",
        },
        "operator_ledger": {
            "Q0": "CERTIFIED",
            "iota_K_0": "CERTIFIED_CLASSICAL",
            "L_K_0": "CERTIFIED_CLASSICAL",
            "Gamma1_regulated": "NOT_DEFINED",
            "breaking_A1": "NOT_DEFINED",
            "counterterm_B1": "NOT_DEFINED",
            "Q1": "NOT_DEFINED",
            "iota_K_1": "NOT_DEFINED",
            "L_K_1": "NOT_DEFINED",
            "cartan_defect_A_K_1": "NOT_DEFINED",
        },
        "phase_boundary_zero_mode_ledger": {
            "rotation_generator_R": "CERTIFIED_CLASSICAL_MATRIX",
            "phase_shift_current_regulated_insertion": "NOT_EXPORTED",
            "K_Berger_regulated_Ward_carrier": "NOT_EXPORTED",
            "boundary_and_transgression_terms": "NOT_DEFINED_WITHOUT_INTEGRATION_SLICE",
            "zero_mode_and_stabilizer_projectors": "NOT_DEFINED_WITHOUT_INTEGRATION_SLICE",
        },
        "defect_target": {
            "formula": "A_K^(1)=[Q0,iota_K^(1)]_+ + [Q1,iota_K^(0)]_+ - L_K^(1)",
            "classification": "NONDEFINED_UPSTREAM_Q1_AND_RENORMALIZED_INSERTIONS_ABSENT",
            "local_quotient_reduction": "NOT_ENTERED_UNDEFINED_DEFECT",
            "exact_primitive": "NOT_APPLICABLE_BEFORE_DEFECT_EXISTS",
            "nontrivial_separator": "NOT_APPLICABLE_BEFORE_DEFECT_EXISTS",
            "raw_D_disposition": "SEPARATE_AFFINE_GENERATOR_NO_QUANTUM_D_IDENTITY_INFERRED",
        },
        "first_missing_operator": {
            "id": "Q1_BERGER_COMPLEX_CLOCK_ONE_LOOP",
            "status": "NOT_DEFINED",
            "reason": "Q1 requires an actual regulated breaking, explicit quartet counterterm coefficients and a restored local one-loop QME; all are nondefined in the terminal predecessor",
            "upstream_first_missing_input": "POSITIVE_BERGER_COMPLEX_CLOCK_EUCLIDEAN_BV_INTEGRATION_SLICE_V1",
            "producer_request": "planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json",
            "receiver_schema": "quantum-weyl/anomalies/schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json",
        },
        "verification_disposition": {
            "counterterm_scheme_covariance": "NOT_DEFINED_NO_COUNTERTERM_OR_BASE_SCHEME",
            "representative_independence": "NOT_DEFINED_NO_RENORMALIZED_INSERTION",
            "quantum_cyclicity": "NOT_DEFINED_CLASSICAL_CYCLICITY_ONLY",
            "quantum_real_structure": "NOT_DEFINED_CLASSICAL_REAL_STRUCTURE_NOT_EXPORTED",
            "phase_current_compatibility": "NOT_DEFINED_NO_REGULATED_CURRENT_INSERTION",
        },
        "claim_flags": {
            "ACTUAL_BREAKING_COEFFICIENTS_COMPUTED": False,
            "COUNTERTERM_CONSTRUCTED": False,
            "LOCAL_QME_RESTORED": False,
            "Q1_CONSTRUCTED": False,
            "RENORMALIZED_K_INSERTION_CONSTRUCTED": False,
            "QUANTUM_K_CARTAN_DEFECT_CLASSIFIED": False,
            "RAW_D_QUANTUM_CARTAN_INFERRED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "HADAMARD_STATE_CERTIFIED": False,
            "PARTICLE_OR_POSITIVITY_CLAIM": False,
        },
        "next_gate": "Satisfy the existing action-derived Euclidean BV integration-slice receiver, compute all four prequotient breaking and counterterm coefficients on independent rails, restore the local QME, construct Q1 and the renormalized K_Berger current insertions, and only then evaluate and reduce A_K^(1).",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL theorem imports the terminal "
            "positive-Berger gravity-clock coefficient disposition and the certified "
            "classical 54-row cyclic K_Berger Cartan complex by exact historical hash. "
            "It proves that the one-loop K_Berger Cartan defect is not defined because "
            "the first required quantum operator Q1 is absent: the regulated breaking "
            "and its counterterm coefficients remain nondefined until an action-derived "
            "Euclidean BV integration slice lands. The classical K_Berger identity does "
            "not become quantum, and the zero local anomaly quotient gives only "
            "conditional removability. Raw D remains a separate affine operation. No "
            "Lorentzian QME, Hadamard, positivity, particle, scattering or unitarity "
            "claim follows."
        ),
        "science_forge": {
            "work_item": "sf:program/work/quantum-berger-k-cartan-one-loop-insertion",
            "stop_condition_disposition": "SMALLEST_MISSING_OPERATOR_Q1_NAMED_WITH_EXACT_UPSTREAM_INPUT",
        },
    }
    value["proof_hashes"] = {
        "input_inventory_sha256": _digest({name: pin["sha256"] for name, pin in PINS.items()}),
        "operator_ledger_sha256": _digest(value["operator_ledger"]),
        "defect_target_sha256": _digest(value["defect_target"]),
        "phase_boundary_zero_mode_ledger_sha256": _digest(value["phase_boundary_zero_mode_ledger"]),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    ledger = value["operator_ledger"]
    if (
        value["result_state"]
        != "NONDEFINED_UPSTREAM_Q1_AND_RENORMALIZED_K_INSERTIONS_ABSENT"
        or ledger["Q1"] != "NOT_DEFINED"
        or ledger["iota_K_1"] != "NOT_DEFINED"
        or ledger["cartan_defect_A_K_1"] != "NOT_DEFINED"
        or value["defect_target"]["local_quotient_reduction"]
        != "NOT_ENTERED_UNDEFINED_DEFECT"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("Berger one-loop K-Cartan nondefinition boundary crossed")


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _atlas_fragment(value: dict[str, Any]) -> dict[str, Any]:
    na = _claim("NOT_APPLICABLE", "This operator gate is not a classical mode or second-order tangent calculation.")
    certificate_bytes = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    fragment = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_by_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "quantum.berger.complex_clock.k_cartan.one_loop_insertion_gate",
                "scope": {
                    "theory": value["setting"]["theory"],
                    "background": value["setting"]["background"],
                    "boundaries": "Euclidean domains, boundary terms and zero-mode projectors are not supplied",
                    "charge_sector": "fixed positive-Berger clock; stationary generator K_Berger=D-omega R",
                    "carrier": "54-row local BV K-Cartan operator gate; not a particle or mode carrier",
                    "degree": "one-loop Cartan insertion and ghost-number-one breaking",
                    "parity": "all BV parities; coefficient parities remain unresolved",
                    "ell": "NOT_APPLICABLE",
                    "m": "NOT_APPLICABLE",
                    "k": "NOT_APPLICABLE",
                    "omega": "K_Berger weight; raw D is affine and separate",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "OPEN",
                    "nonlinear": "NOT_APPLICABLE",
                    "observational": "NOT_APPLICABLE",
                    "quantum": "OPEN",
                },
                "mode_data": {
                    "dispersion": na,
                    "lee_wald": na,
                    "taub_maps": na,
                    "resonance": na,
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": na,
                        "smooth_secular": na,
                        "causal_retarded": na,
                    },
                },
                "quantum_data": {
                    "entry_kind": "NON_MODE_PARTICLE_GUARD",
                    "dependency_tags": value["dependency_tags"],
                    "classical_mode_imported": _claim("NOT_APPLICABLE", "The imported object is a classical BV operator complex, not a residual mode."),
                    "BRST_cocycle": _claim("OPEN", "The actual one-loop K-Cartan defect is not defined because Q1 and the renormalized insertions are absent."),
                    "BRST_exactness": _claim("NO_CERTIFIED_MAP", "A zero local quotient cannot classify a defect that has not been constructed."),
                    "pairing_status": _claim("OPEN", "The classical cyclic pairing is certified; quantum cyclic compatibility is not defined."),
                    "compatible_complex_structure": _claim("NOT_APPLICABLE", "No one-particle carrier is present."),
                    "Hadamard_two_point_function": _claim("NO_CERTIFIED_MAP", "No Lorentzian two-point function follows from this local operator gate."),
                    "state_space_status": _claim("NOT_APPLICABLE", "No state space is constructed."),
                    "anomaly_QME_dependency": _claim("OPEN", "The actual breaking, counterterm, restored QME and Q1 remain nondefined."),
                    "lifecycle_state": _claim("OPEN", "The first missing quantum operator is certified; the K-Cartan quantum identity is not classified."),
                    "particle_interpretation": _claim("NOT_APPLICABLE", "A Cartan insertion is not a particle state."),
                    "carrier_crosswalk": _claim("NO_CERTIFIED_MAP", "The classical K-Cartan complex has no certified renormalized Q1/insertion crosswalk."),
                },
                "evidence": [
                    {
                        "path": str(OUTPUT.relative_to(ROOT)),
                        "result_id": value["result_id"],
                        "sha256": hashlib.sha256(certificate_bytes).hexdigest(),
                    }
                ],
                "claim_boundary": value["claim_boundary"],
            }
        ],
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 quantum-weyl/cartan/berger_k_one_loop_insertion_nondefinition.py --check",
            "PYTHONPATH=quantum-weyl python3 quantum-weyl/cartan/verify_berger_k_one_loop_insertion_nondefinition.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/positive-berger-k-one-loop-insertion-nondefinition-fragment-v1.json",
        ],
    }
    Draft202012Validator(json.loads(ATLAS_SCHEMA.read_text())).validate(fragment)
    return fragment


def _report(value: dict[str, Any]) -> str:
    return f"""# Berger one-loop K-Cartan insertion: exact nondefinition

## Result

The classical stationary generator is certified as

    K_Berger = D - omega R,

on all 54 gauge-fixed gravity-clock BV rows through arity three. Raw D is
affine about the rotating clock background and is kept separate.

The one-loop Cartan defect

    A_K^(1) = [Q0,iota_K^(1)]_+ + [Q1,iota_K^(0)]_+ - L_K^(1)

is nevertheless NONDEFINED. Its first missing quantum operator is
Q1_BERGER_COMPLEX_CLOCK_ONE_LOOP. The terminal coefficient calculation
certifies that the regulated breaking and all counterterm coefficients remain
NONDEFINED because the action-derived Euclidean gauge-fixed BV integration
slice and full Hessian have not landed.

Therefore iota_K^(1), L_K^(1), the regulated phase-shift-current insertion,
boundary/transgression terms and zero-mode contributions are not defined.
The imported 54-row K-signoff also does not export a classical real structure,
so no quantum real-structure compatibility test is inferred from cyclicity.
The defect cannot be reduced in the zero local quotient, and it is not yet
classified as zero, exact or anomalous.

## Next gate

Use the existing producer contract at
planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json.
After it is satisfied, compute the four breaking coefficients on independent
rails, construct the counterterm and restored Q1, and then evaluate the full
K_Berger defect in one declared scheme.

## Claim boundary

This is LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL. It does not promote the classical
K-Cartan theorem to quantum, does not infer any raw-D identity, and establishes
no Lorentzian QME, Hadamard, positivity, particle, scattering or unitarity
claim.

EVIDENCE: quantum-weyl/cartan/certificates/BERGER_K_ONE_LOOP_INSERTION_NONDEFINITION_V1.json

CLOSE-OUT: DONE — the smallest missing quantum operator Q1 and its exact upstream Euclidean integration-slice dependency are certified; the one-loop K-Cartan defect correctly remains nondefined.
"""


def _write(value: dict[str, Any]) -> None:
    OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(_report(value))
    ATLAS_OUTPUT.write_text(json.dumps(_atlas_fragment(value), indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != value:
            raise ValueError("Berger one-loop K-Cartan certificate drifted")
        if REPORT.read_text() != _report(value):
            raise ValueError("Berger one-loop K-Cartan report drifted")
        if json.loads(ATLAS_OUTPUT.read_text()) != _atlas_fragment(value):
            raise ValueError("Berger one-loop K-Cartan atlas fragment drifted")
    else:
        _write(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
