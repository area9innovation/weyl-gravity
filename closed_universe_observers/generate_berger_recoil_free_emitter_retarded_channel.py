#!/usr/bin/env python3
"""Certify finite U_E evolution and the first retarded Maxwell channel."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers.berger_recoil_free_emitter_retarded_channel import (
    evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right,
)
from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL.json"
SCHEMA = PACKAGE / "schema/berger-recoil-free-emitter-first-retarded-maxwell-channel-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-free-emitter-first-retarded-maxwell-channel.md"
DEPENDENCIES = {
    "positive_energy_preparation": PACKAGE / "certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "forms": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_free_emitter_retarded_channel.py",
    PACKAGE / "berger_recoil_massive_diagonal_preparation.py",
    PACKAGE / "verify_berger_recoil_free_emitter_retarded_channel.py",
    PACKAGE / "tests/test_berger_recoil_free_emitter_retarded_channel.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _defect_count(matrix: sp.Matrix) -> int:
    return sum(sp.simplify(entry) != 0 for entry in matrix)


def canonical_free_evolution_audit(two_j: int) -> dict[str, object]:
    """Check the exact Hamiltonian and constraint identities in one shell."""
    mass_squared = sp.symbols("m_squared", positive=True)
    d0 = d_matrix(two_j, 0)
    d1 = d_matrix(two_j, 1)
    d2 = d_matrix(two_j, 2)
    delta_one = d0.conjugate().T
    delta_two = d1.conjugate().T
    delta_three = d2.conjugate().T
    dimension = 3 * (two_j + 1)
    identity = sp.eye(dimension)
    a_operator = identity + d1 * delta_two / mass_squared
    ell_operator = delta_three * d2 + mass_squared * identity
    h_operator = d1 * delta_two + delta_three * d2 + mass_squared * identity
    zero = sp.zeros(dimension)
    hamiltonian_generator = sp.Matrix.vstack(
        sp.Matrix.hstack(zero, a_operator),
        sp.Matrix.hstack(-ell_operator, zero),
    )
    symplectic_form = sp.Matrix.vstack(
        sp.Matrix.hstack(zero, identity),
        sp.Matrix.hstack(-identity, zero),
    )
    return {
        "two_j": two_j,
        "spatial_two_form_dimension": dimension,
        "A_L_minus_H_defect_count": _defect_count(a_operator * ell_operator - h_operator),
        "L_A_minus_H_defect_count": _defect_count(ell_operator * a_operator - h_operator),
        "dSigma_squared_defect_count": _defect_count(d2 * d1) + _defect_count(d1 * d0),
        "deltaSigma_squared_defect_count": _defect_count(delta_one * delta_two),
        "constraint_preservation_defect_count": _defect_count(
            delta_two * ell_operator - mass_squared * delta_two
        ),
        "A_self_adjoint_defect_count": _defect_count(
            a_operator.conjugate().T - a_operator
        ),
        "L_self_adjoint_defect_count": _defect_count(
            ell_operator.conjugate().T - ell_operator
        ),
        "symplectic_generator_defect_count": _defect_count(
            hamiltonian_generator.conjugate().T * symplectic_form
            + symplectic_form * hamiltonian_generator
        ),
        "free_evolution": "q_t=A p; p_t=-L q; A L=L A=Delta_2+m^2",
        "temporal_reconstruction": "alpha=m^-2 deltaSigma p",
        "switched_current": "delta(hK)=(0,h_prime alpha); delta^2(hK)=0",
    }


def _evaluate(
    values: dict[str, dict], detector: str, two_j: int, column: int
) -> dict[str, object]:
    result = evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right(
        detector_image_certificate=values["detector_image"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        moment_certificate=values["moments"],
        exact_kernel_certificate=values["kernels"],
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=RationalInterval(Fraction(1), Fraction(2)),
    )
    evolution = result["canonical_free_evolution"]
    current = result["switched_current"]
    channel = result["first_retarded_maxwell_channel"]
    return {
        "detector": result["detector"],
        "switch_id": result["switch_id"],
        "two_j": result["two_j"],
        "column": result["column"],
        "mass_squared_interval": result["mass_squared_interval"],
        "support_physical_time": result["support_physical_time"],
        "causal_initial_data_audit": result["causal_initial_data_audit"],
        "canonical_free_evolution_summary": {
            "q_polynomial_coefficient_count": len(
                evolution["q_polynomial_coefficients"]
            ),
            "q_uniform_remainder_upper": evolution["q_uniform_remainder_upper"],
            "p_polynomial_coefficient_count": len(
                evolution["p_polynomial_coefficients"]
            ),
            "p_uniform_remainder_upper": evolution["p_uniform_remainder_upper"],
            "alpha_polynomial_coefficient_count": len(
                evolution["alpha_polynomial_coefficients"]
            ),
            "alpha_uniform_remainder_upper": evolution[
                "alpha_uniform_remainder_upper"
            ],
            "formula": evolution["formula"],
        },
        "switched_current_summary": {
            "spacetime_dimension": len(current["polynomial_coefficients"][0]),
            "polynomial_coefficient_count": len(current["polynomial_coefficients"]),
            "uniform_remainder_upper": current["uniform_remainder_upper"],
            "temporal_block_structural_zero": current[
                "temporal_block_structural_zero"
            ],
            "conservation_identity": current["conservation_identity"],
        },
        "first_retarded_maxwell_channel_summary": {
            "field_polynomial_coefficient_count": len(
                channel["field_polynomial_coefficients"]
            ),
            "field_uniform_remainder_upper": channel[
                "field_uniform_remainder_upper"
            ],
            "time_derivative_polynomial_coefficient_count": len(
                channel["time_derivative_polynomial_coefficients"]
            ),
            "time_derivative_uniform_remainder_upper": channel[
                "time_derivative_uniform_remainder_upper"
            ],
            "support_right_field": channel["support_right_field"],
            "support_right_time_derivative": channel[
                "support_right_time_derivative"
            ],
        },
        "claim_boundary": result["claim_boundary"],
    }


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "positive_energy_preparation": "COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "kernels": "MAXWELL_AND_MASSIVE_BLOCKS_TWO_J0_TO_4_EXPORTED",
        "forms": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "signs": "EXACT_SPACETIME_CODERIVATIVE_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    audits = [canonical_free_evolution_audit(two_j) for two_j in range(5)]
    defect_fields = (
        "A_L_minus_H_defect_count",
        "L_A_minus_H_defect_count",
        "dSigma_squared_defect_count",
        "deltaSigma_squared_defect_count",
        "constraint_preservation_defect_count",
        "A_self_adjoint_defect_count",
        "L_self_adjoint_defect_count",
        "symplectic_generator_defect_count",
    )
    if any(row[field] for row in audits for field in defect_fields):
        raise AssertionError("canonical free-evolution identity failed")
    fixtures = {
        "D0_two_j0_column0": _evaluate(values, "D0", 0, 0),
        "D1_two_j1_column1": _evaluate(values, "D1", 1, 1),
    }
    for fixture in fixtures.values():
        expected = 4 * (fixture["two_j"] + 1)
        channel = fixture["first_retarded_maxwell_channel_summary"]
        if len(channel["support_right_field"]) != expected:
            raise AssertionError("support-right Maxwell field dimension drifted")
        if not fixture["switched_current_summary"]["temporal_block_structural_zero"]:
            raise AssertionError("switched-current temporal block is not structural zero")
        if not all(fixture["causal_initial_data_audit"].values()):
            raise AssertionError("causal support-left data audit failed")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result evolves each finite "
        "coupling-stripped full-canonical preparation with q=C_H q0+S_H A p0 and "
        "p=C_H p0-S_H L q0 on its own exact switch slab, reconstructs "
        "alpha=m^-2 delta_Sigma p, and exports the conserved current "
        "J=delta(hK)=(0,h' alpha). It then applies the finite Maxwell retarded sine "
        "and cosine kernels and exports the field and physical-time derivative at "
        "the support-right slice. Exact shell audits certify A L=L A=Delta_2+m^2, "
        "constraint preservation, and delta J=delta^2(hK)=0 through two_j=4. The "
        "serialized fixtures use m^2 in [1,2] only as validation data. The whole-"
        "support h' hull is rigorous but coarse. This is the first leading Maxwell "
        "channel in the detector/recoil word, not a detector record or feedback "
        "recoil coefficient: retained nonvanishing, propagation to the detector "
        "window, d and Q_a contraction, response rank, infinite-tail control, the "
        "four absolute-g3 recoil intervals, tangent-cone restriction, Bridge 3, "
        "finite-r/all-orders observer stability, and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-free-emitter-first-retarded-maxwell-channel-v1",
        "result_id": "BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL",
        "setting_id": values["positive_energy_preparation"]["setting_id"],
        "claim_status": "FINITE_FREE_EMITTER_AND_FIRST_RETARDED_MAXWELL_CHANNEL_CERTIFIED_DETECTOR_CONTRACTION_OPEN",
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
            "boundaries": "one exact compact emitter-switch slab; support-right Cauchy slice; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "coupling-stripped unrestricted canonical massive-two-form preparation to conserved Maxwell one-form source and retarded field",
            "degree": "massive spatial two-form pair (q,p) to Maxwell spacetime one-form",
            "parity": "D0 axial and D1 transverse detector labels; no further parity quotient",
            "ell": "two_j=0,...,4",
            "m": "all component-major form rows",
            "k": "all passive columns k=0,...,two_j via the certified callable",
            "omega": "finite massive and Maxwell sine/cosine series through order five with uniform rational tails",
        },
        "canonical_evolution_audits": audits,
        "coverage": {
            "detectors": ["D0", "D1"],
            "two_j_inclusive": [0, 4],
            "passive_column_count": 30,
            "runtime_mass_domain": "strictly_positive_rational_mass_squared_interval",
            "serialized_validation_mass_squared_interval": ["1", "2"],
            "output_slice": "emitter_switch_support_right",
        },
        "serialized_fixture_channels": fixtures,
        "flags": {
            "FULL_CANONICAL_FREE_EMITTER_EVOLUTION_BOUND": True,
            "TEMPORAL_COMPONENT_RECONSTRUCTED": True,
            "CONSERVED_SWITCHED_CURRENT_EXPORTED": True,
            "FIRST_RETARDED_MAXWELL_CAUCHY_PAIR_AT_SUPPORT_RIGHT_EXPORTED": True,
            "ALL_D0_D1_COLUMNS_TWO_J0_TO_4_CALLABLE": True,
            "RETAINED_CHANNEL_NONVANISHING_CERTIFIED": False,
            "PROPAGATED_TO_DETECTOR_WINDOW": False,
            "DETECTOR_Q_CONTRACTION_EXPORTED": False,
            "RESPONSE_RANK_FROM_FINITE_CHANNELS_CERTIFIED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "PROPAGATE_THE_SUPPORT_RIGHT_MAXWELL_CAUCHY_PAIR_TO_THE_DETECTOR_WINDOW_AND_CONTRACT_D_THEN_Q_A",
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
        raise SystemExit("stale free-emitter first-retarded-channel certificate")
    print("BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
