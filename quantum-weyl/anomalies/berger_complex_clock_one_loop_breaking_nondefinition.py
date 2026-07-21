#!/usr/bin/env python3
"""Certify the first missing datum for the Berger clock one-loop breaking."""

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
OUTPUT = HERE / "certificates/BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1.json"
SCHEMA = HERE / "schema/berger-complex-clock-one-loop-breaking-nondefinition-v1.schema.json"
RECEIVER_SCHEMA = HERE / "schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json"
REPORT = QROOT / "reports/berger-complex-clock-one-loop-breaking-nondefinition-v1.md"
REQUEST = ROOT / "planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/positive-berger-complex-clock-one-loop-nondefinition-fragment-v1.json"
ATLAS_SCHEMA = ROOT / "residual_atlas/schema/residual-atlas-fragment-v1.schema.json"

PINS = {
    "local_anomaly_complex": {
        "path": "quantum-weyl/anomalies/certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1.json",
        "source_commit": "06f1531ee0485670eb0df45d82ef896d999cac60",
        "sha256": "edfec590245e6e9c5156ae2ae72a8a8e18548a2e628012d7b44ded034df933ac",
    },
    "matter_coupled_master_action": {
        "path": "d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json",
        "source_commit": "306ff78a2001f23124d412e9a2f41531bec74f78",
        "sha256": "a537e31bf667520443903551b5bf2596dff9a1c35fade88d2ffc1e89c1e0b836",
    },
    "berger_classical_gauge_fixed_unary": {
        "path": "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json",
        "source_commit": "445e26663d06764bc858ff0a004ba6178acce75f",
        "sha256": "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
    },
    "loop_multiplicity_receiver": {
        "path": "quantum-weyl/spectral/euclidean/certificates/REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json",
        "source_commit": "3213092073d15ca833fe1625d4fe4b57cd420a66",
        "sha256": "0927a3b9ad6e2d04366b30667d4eec64c7948a70cb54767459a7416f8ba71a0c",
    },
    "conditional_covariant_regulator_receiver": {
        "path": "quantum-weyl/anomalies/certificates/DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT.json",
        "source_commit": "5bf7a254183e407d439ea85ed99a979ed61917b4",
        "sha256": "62f53393712a58c25ca26f2318e9feba4fea8efedd2659e4eeb76b7634de2f13",
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
    anomaly = values["local_anomaly_complex"]
    action = values["matter_coupled_master_action"]
    unary = values["berger_classical_gauge_fixed_unary"]
    multiplicity = values["loop_multiplicity_receiver"]
    regulator = values["conditional_covariant_regulator_receiver"]

    if anomaly["coefficient_and_qme_status"]["coefficient_status"] != "NOT_COMPUTED_FOR_GRAVITY_CLOCK_THEORY":
        raise ValueError("anomaly coefficient predecessor was unexpectedly promoted")
    if not action["claim_flags"]["LOCAL_ACTION_CERTIFIED"]:
        raise ValueError("matter-coupled master action is not certified")
    if unary["result_id"] != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION":
        raise ValueError("wrong Berger unary input")
    if multiplicity["claim_flags"]["REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED"]:
        raise ValueError("loop multiplicity receiver was unexpectedly accepted")
    if regulator["claim_flags"]["SELECTED_HESSIAN_IMPORTED"]:
        raise ValueError("selected Hessian was unexpectedly imported")

    coefficient_rows = [
        {
            "class_id": class_id,
            "parity": parity,
            "prequotient_coefficient": "NONDEFINED",
            "quartet_primitive": primitive,
            "counterterm_coefficient": "NONDEFINED",
        }
        for class_id, parity, primitive in (
            ("ANOM_OMEGA_C2", "even", "B_C=int sqrt(g) tau C2"),
            ("ANOM_OMEGA_E4", "even", "B_E=four-dimensional Euler Wess-Zumino primitive"),
            ("ANOM_OMEGA_C_DUAL_C", "odd", "B_P=int sqrt(g) tau CdualC"),
            ("ANOM_OMEGA_BOX_R", "even_scheme_dependent", "B_BOX=-(1/12)int sqrt(g) R2 plus horizontal current"),
        )
    ]

    value = {
        "schema": "quantum-weyl-berger-complex-clock-one-loop-breaking-nondefinition-v1",
        "result_id": "BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1",
        "result_state": "NONDEFINED_MISSING_ACTION_DERIVED_EUCLIDEAN_BV_INTEGRATION_SLICE",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": PINS,
        "theory_scope": {
            "theory": anomaly["theory"]["name"],
            "background": anomaly["theory"]["background"],
            "chart": anomaly["theory"]["local_algebra"],
            "strict_action_complex_map": anomaly["strict_to_coupled_action_morphism"]["verdict"],
            "strict_separator": anomaly["strict_to_coupled_action_morphism"]["separator"]["separation"],
        },
        "available_input_ledger": {
            "action_and_CME": "CERTIFIED",
            "minimal_and_nonminimal_BV_rows": "CERTIFIED",
            "classical_gauge_fixed_54_row_unary_and_SDR": "CERTIFIED_CLASSICAL_NOT_LOOP_OPERATOR",
            "local_H14_even_and_odd": "ZERO_ON_DECLARED_REGULAR_FORMAL_POLAR_CHART",
            "quartet_primitives": "CERTIFIED",
            "conditional_covariant_regulator_receiver": "CERTIFIED_RECEIVER_ONLY",
        },
        "missing_input_ledger": {
            "Euclidean_continuation_and_domains": "MISSING",
            "action_derived_gauge_fixed_Lagrangian_integration_slice": "MISSING_FIRST",
            "complete_even_ghost_nonminimal_Hessian_blocks": "MISSING",
            "ellipticity_and_formal_adjoint_proof": "MISSING",
            "determinant_Berezinian_row_map": "MISSING",
            "measure_and_Jacobians": "MISSING",
            "zero_mode_and_stabilizer_projectors": "MISSING",
            "real_contours_and_spectral_cuts": "MISSING",
            "explicit_Euclidean_regulator_and_subtraction": "MISSING",
            "independent_coefficient_rail": "NOT_REACHED",
        },
        "first_missing_input": {
            "id": "POSITIVE_BERGER_COMPLEX_CLOCK_EUCLIDEAN_BV_INTEGRATION_SLICE_V1",
            "reason": "the complete classical 54-row unary BV matrix contains antifields and contractible rows and does not define the quadratic Lagrangian integration variables or their determinant exponents",
            "producer_request": "planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json",
            "receiver_schema": "quantum-weyl/anomalies/schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json",
        },
        "coefficient_ledger": coefficient_rows,
        "quotient_disposition": {
            "H14_even_dimension": 0,
            "H14_odd_dimension": 0,
            "actual_breaking": "NONDEFINED",
            "actual_counterterm": "NONDEFINED_COEFFICIENTS",
            "strict_199_over_30_minus_87_over_20_import": "FORBIDDEN_CHANGED_THEORY_NO_ACTION_COMPLEX_MAP",
            "zero_quotient_implication": "IF_A_REGULATED_CONSISTENT_LOCAL_BREAKING_IS_COMPUTED_THEN_IT_IS_REMOVABLE_BY_THE_CERTIFIED_PRIMITIVES",
        },
        "ward_disposition": {
            "phase_shift_current_compatibility": "NONDEFINED_BEFORE_REGULATED_INSERTION",
            "K_Berger_compatibility": "NONDEFINED_BEFORE_REGULATED_INSERTION",
            "raw_D": "NOT_A_LINEAR_SYMMETRY_OF_THE_FIXED_CLOCK_BACKGROUND",
        },
        "claim_flags": {
            "ACTUAL_BREAKING_COEFFICIENTS_COMPUTED": False,
            "COUNTERTERM_COEFFICIENTS_COMPUTED": False,
            "LOCAL_GRAVITY_CLOCK_QME_RESTORED": False,
            "K_BERGER_WARD_IDENTITY_PROVED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
            "HADAMARD_STATE_CERTIFIED": False,
            "PARTICLE_OR_POSITIVITY_CLAIM": False,
        },
        "next_gate": "Supply one content-addressed action-derived positive-Berger complex-clock Euclidean BV integration slice satisfying the strict receiver schema; only then compute all prequotient coefficients on two independent rails and reduce them through the certified quartet primitives.",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL audit imports the exact "
            "positive-Berger complex-clock local anomaly quotient, its 961/1920 "
            "strict-to-coupled separator, the complete matter-coupled master action, "
            "the classical 54-row gauge-fixed unary contraction, the repository loop-"
            "multiplicity receiver and the conditional covariant-regulator receiver. "
            "It proves that the actual one-loop breaking coefficients are not defined "
            "by the current repository data because the first indispensable input--an "
            "action-derived Euclidean gauge-fixed Lagrangian integration slice and full "
            "Hessian--is absent. The zero H14 quotient means a future consistent local "
            "breaking will be removable; it neither makes its coefficients zero nor "
            "restores the QME. Strict pure-Weyl coefficients are not imported across "
            "the certified nonexistence of an action-complex map. No Lorentzian QME, "
            "Hadamard state, positivity, particle, scattering or unitarity claim follows."
        ),
    }
    value["proof_hashes"] = {
        "input_inventory_sha256": _digest({name: pin["sha256"] for name, pin in PINS.items()}),
        "missing_input_ledger_sha256": _digest(value["missing_input_ledger"]),
        "coefficient_ledger_sha256": _digest(value["coefficient_ledger"]),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    missing = value["missing_input_ledger"]
    if (
        value["result_state"] != "NONDEFINED_MISSING_ACTION_DERIVED_EUCLIDEAN_BV_INTEGRATION_SLICE"
        or missing["action_derived_gauge_fixed_Lagrangian_integration_slice"] != "MISSING_FIRST"
        or any(row["prequotient_coefficient"] != "NONDEFINED" for row in value["coefficient_ledger"])
        or any(value["claim_flags"].values())
    ):
        raise ValueError("Berger one-loop nondefinition boundary crossed")


def _report(value: dict[str, Any]) -> str:
    return f"""# Berger complex-clock one-loop breaking: first missing datum

## Result

The actual one-loop local BV breaking of the positive-Berger gravity--complex-
clock theory is **not yet defined**.  The first missing datum is the
action-derived Euclidean gauge-fixed Lagrangian integration slice and its full
Hessian.  The existing 54-row gauge-fixed object is a classical unary BV
differential and contraction; it is not a determinant or loop-multiplicity
operator.

This is a fail-closed `LOCAL-ALGEBRAIC`/`EUCLIDEAN-SPECTRAL` result.  The
matter-coupled master action, minimal/nonminimal BV rows, classical gauge
fixing, local anomaly quotient, and Wess--Zumino primitives are certified.
The Euclidean domains, Hessian blocks, Berezinian row map, measure, zero-mode
projectors, contours and regulator are absent.

Consequently every prequotient coefficient of `omega C2`, `omega E4`,
`omega CdualC`, and `omega BoxR` remains `NONDEFINED`, as does the actual
counterterm coefficient.  The zero local quotient proves only the conditional
statement that a future consistent local breaking is removable.  It does not
set the coefficients to zero.

The strict pure-Weyl vector `(199/30,-87/20)` is not imported: the exact
strict-to-coupled action-complex separator is `{value['theory_scope']['strict_separator']['numerator']}/{value['theory_scope']['strict_separator']['denominator']}`.

## Producer contract

The single typed request is
`planning/forge-requests/positive-berger-complex-clock-euclidean-bv-integration-slice.json`.
Its payload must satisfy
`quantum-weyl/anomalies/schema/berger-complex-clock-euclidean-bv-integration-slice-v1.schema.json`.

## Claim boundary

No gravity-clock coefficient, counterterm, restored QME, K_Berger Ward
identity, Lorentzian QME, Hadamard state, positivity, particle, scattering or
unitarity conclusion is made.

EVIDENCE: quantum-weyl/anomalies/certificates/BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1.json

CLOSE-OUT: DONE — exact first missing action/regulator datum certified and one typed producer request emitted; coefficient computation correctly remains nondefined.
"""


def _claim(status: str, statement: str) -> dict[str, str]:
    return {"status": status, "statement": statement}


def _atlas_fragment(value: dict[str, Any]) -> dict[str, Any]:
    na = _claim("NOT_APPLICABLE", "This coefficient gate is not a classical mode or second-order tangent calculation.")
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
                "id": "quantum.berger.complex_clock.one_loop_breaking_coefficient_gate",
                "scope": {
                    "theory": value["theory_scope"]["theory"],
                    "background": value["theory_scope"]["background"],
                    "boundaries": "Euclidean continuation, domains and boundary conditions are not supplied",
                    "charge_sector": "fixed positive-Berger clock on the regular formal rho-nonzero polar chart",
                    "carrier": "local H14 quotient plus a missing action-derived Euclidean gauge-fixed integration slice; not a particle or mode carrier",
                    "degree": "ghost number one, form degree four",
                    "parity": "even and odd coefficient rows kept distinct",
                    "ell": "NOT_APPLICABLE",
                    "m": "NOT_APPLICABLE",
                    "k": "NOT_APPLICABLE",
                    "omega": "NOT_APPLICABLE",
                },
                "descriptions": {
                    "causal": "NO_CERTIFIED_MAP",
                    "symplectic": "NOT_APPLICABLE",
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
                    "classical_mode_imported": _claim("NOT_APPLICABLE", "This entry imports an action and local BV complex, not a classical mode."),
                    "BRST_cocycle": _claim("CERTIFIED", "The complete matter-coupled ghost-one local candidate complex is certified on the declared regular chart."),
                    "BRST_exactness": _claim("CERTIFIED", "The even and odd H14 quotients vanish with explicit quartet primitives."),
                    "pairing_status": _claim("NOT_APPLICABLE", "No state or residual pairing is computed by a local coefficient gate."),
                    "compatible_complex_structure": _claim("NOT_APPLICABLE", "No one-particle carrier is present."),
                    "Hadamard_two_point_function": _claim("NO_CERTIFIED_MAP", "A local Euclidean coefficient preflight does not supply a Lorentzian two-point function."),
                    "state_space_status": _claim("NOT_APPLICABLE", "No state space is constructed."),
                    "anomaly_QME_dependency": _claim("OPEN", "Actual breaking and counterterm coefficients are NONDEFINED until the action-derived Euclidean gauge-fixed integration slice and full Hessian land."),
                    "lifecycle_state": _claim("OPEN", "The local quotient is CLASSIFIED; coefficient computation and gravity-clock QME restoration remain open."),
                    "particle_interpretation": _claim("NOT_APPLICABLE", "Local anomaly candidates and counterterms are not particles."),
                    "carrier_crosswalk": _claim("NO_CERTIFIED_MAP", "The strict pure-Weyl coefficient vector cannot cross the certified 961/1920 action-complex separator."),
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
            "PYTHONPATH=quantum-weyl python3 quantum-weyl/anomalies/berger_complex_clock_one_loop_breaking_nondefinition.py --check",
            "PYTHONPATH=quantum-weyl python3 quantum-weyl/anomalies/verify_berger_complex_clock_one_loop_breaking_nondefinition.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/positive-berger-complex-clock-one-loop-nondefinition-fragment-v1.json",
        ],
    }
    Draft202012Validator(json.loads(ATLAS_SCHEMA.read_text())).validate(fragment)
    return fragment


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
            raise ValueError("Berger one-loop nondefinition certificate drifted")
        if REPORT.read_text() != _report(value):
            raise ValueError("Berger one-loop nondefinition report drifted")
        if json.loads(ATLAS_OUTPUT.read_text()) != _atlas_fragment(value):
            raise ValueError("Berger one-loop atlas fragment drifted")
        Draft202012Validator.check_schema(json.loads(RECEIVER_SCHEMA.read_text()))
        if json.loads(REQUEST.read_text())["body"]["state"] not in {"REQUESTED", "ACCEPTED", "LANDED"}:
            raise ValueError("typed producer request is not live")
    else:
        _write(value)
    print("BERGER_COMPLEX_CLOCK_ONE_LOOP_BREAKING_NONDEFINITION_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
