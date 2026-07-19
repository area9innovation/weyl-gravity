#!/usr/bin/env python3
"""Certify the finite detector-polynomial and Berger ``Dhat_1`` binding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _apply_spacetime_dhat1,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
    assemble_detector_advanced_maxwell_polynomial,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_DETECTOR_FORM_BINDING.json"
SCHEMA = PACKAGE / "schema/berger-recoil-detector-form-binding-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-detector-form-binding.md"
DEPENDENCIES = {
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "detector_provider": PACKAGE / "certificates/BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER.json",
    "form_signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "matrix_engine": PACKAGE / "certificates/BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_detector_form_binding.py",
    PACKAGE / "verify_berger_recoil_detector_form_binding.py",
    PACKAGE / "tests/test_berger_recoil_detector_form_binding.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "detector_provider": "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED",
        "form_signs": "EXACT_SPACETIME_D_BLOCKS_EXPORTED",
        "matrix_engine": "COMPLEX_MATRIX_VECTOR_INTERVAL_CONVOLUTION_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    detector = values["detector_image"]
    assembled = assemble_detector_advanced_maxwell_polynomial(
        detector, detector="D0", two_j=0, column=0
    )
    applied = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector, detector="D1", two_j=4, column=4
    )
    wrong_sign = _apply_spacetime_dhat1(
        detector,
        detector="D0",
        two_j=0,
        column=0,
        radical_bits=80,
        time_derivative_sign=1,
    )
    correct_sign = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector, detector="D0", two_j=0, column=0
    )
    if _payload_sha256(wrong_sign["polynomial_coefficients"]) == _payload_sha256(
        correct_sign["polynomial_coefficients"]
    ):
        raise AssertionError("physical-time derivative sign mutation escaped")
    if assembled["dimension"] != 4 or applied["output_dimension"] != 30:
        raise AssertionError("finite detector/form dimensions drifted")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result assembles every "
        "D0/D1 passive-column advanced-Maxwell polynomial through two_j=4 in "
        "the certified component-major spacetime one-form basis, then applies "
        "the exact Berger Dhat_1 with partial_t=-partial_T. Algebraic radicals "
        "are outward rationally enclosed. The output remainder includes a new "
        "uniform bound for the physical-time derivative of the omitted cosine "
        "tail and induced-norm propagation through d0 and d1. This binds the "
        "first physical preparation-form stage only. Switch multiplication, "
        "the advanced massive-two-form Green image, Cauchy trace, positive-energy "
        "dual, I_abc, recoil records, the second-order cone, Bridge 3 and quantum "
        "claims remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-detector-form-binding-v1",
        "result_id": "BERGER_RECOIL_DETECTOR_FORM_BINDING",
        "setting_id": values["detector_image"]["setting_id"],
        "claim_status": "FINITE_DETECTOR_ADVANCED_MAXWELL_DHAT1_BINDING_CERTIFIED_MASSIVE_PREPARATION_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "compact detector and switch supports; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "detector-selected complex interval spacetime one- and two-form polynomials",
            "degree": "Dhat_1: spacetime degree 1 to 2",
            "parity": "D0 axial and D1 transverse detector profiles",
            "ell": "two_j=0,...,4",
            "m": "all component-major representation rows",
            "k": "all passive columns k=0,...,two_j",
            "omega": "advanced Maxwell polynomial in T plus uniform value and derivative remainders",
        },
        "basis_binding": {
            "input": "[scalar; theta1; theta2; theta3], each coframe block ordered by representation row",
            "output": "[dt theta1;dt theta2;dt theta3;theta1 theta2;theta1 theta3;theta2 theta3]",
            "coefficient_variable": "T=t_detector_center-t",
            "physical_time_derivative": "partial_t=-partial_T",
        },
        "fixtures": {
            "D0_two_j0_column0_assembled_sha256": _payload_sha256(assembled),
            "D1_two_j4_column4_Dhat1_sha256": _payload_sha256(applied),
            "wrong_time_sign_detected": True,
        },
        "flags": {
            "FINITE_DETECTOR_SPACETIME_ONE_FORM_POLYNOMIAL_ASSEMBLY_EXPORTED": True,
            "EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE": True,
            "PHYSICAL_TIME_DERIVATIVE_TAIL_BOUND_EXPORTED": True,
            "COMPONENT_MAJOR_BASIS_BINDING_CERTIFIED": True,
            "ADVANCED_MASSIVE_TWO_FORM_IMAGE_EVALUATED": False,
            "EMITTER_CAUCHY_COEFFICIENTS_SERIALIZED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "MULTIPLY_BY_EXACT_SWITCH_THEN_APPLY_ADVANCED_MASSIVE_TWO_FORM_GREEN_KERNEL",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale detector/form binding certificate")
    print("BERGER_RECOIL_DETECTOR_FORM_BINDING generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
