#!/usr/bin/env python3
"""Certify finite coupling-stripped positive-energy emitter coefficients."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    coclosed_two_form_projector_audit,
    evaluate_coupling_stripped_positive_energy_preparation_at_support_left,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json"
SCHEMA = PACKAGE / "schema/berger-recoil-positive-energy-preparation-coefficients-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-positive-energy-preparation-coefficients.md"
DEPENDENCIES = {
    "physical_cauchy": PACKAGE / "certificates/BERGER_RECOIL_PHYSICAL_MASSIVE_CAUCHY_PREPARATION.json",
    "coupling_stripped": PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json",
    "positive_energy": PACKAGE / "certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json",
    "forms": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_massive_diagonal_preparation.py",
    PACKAGE / "verify_berger_recoil_positive_energy_preparation_coefficients.py",
    PACKAGE / "tests/test_berger_recoil_positive_energy_preparation_coefficients.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evaluate(values: dict[str, dict], detector: str, two_j: int, column: int) -> dict[str, object]:
    return evaluate_coupling_stripped_positive_energy_preparation_at_support_left(
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


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "physical_cauchy": "EMITTER_FULL_FORM_CAUCHY_PAIR_EXPORTED",
        "coupling_stripped": "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED",
        "positive_energy": "OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED",
        "forms": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "signs": "EXACT_SPACETIME_CODERIVATIVE_BLOCKS_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "kernels": "MAXWELL_AND_MASSIVE_BLOCKS_TWO_J0_TO_4_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    projector_audits = [coclosed_two_form_projector_audit(two_j) for two_j in range(5)]
    defect_fields = (
        "idempotence_defect_count",
        "self_adjoint_defect_count",
        "coderivative_defect_count",
        "exact_form_annihilation_defect_count",
    )
    if [row["coclosed_rank"] for row in projector_audits] != [0, 2, 3, 4, 5]:
        raise AssertionError("co-closed rank rail drifted")
    if any(row[field] for row in projector_audits for field in defect_fields):
        raise AssertionError("co-closed projector identity failed")
    fixtures = {
        "D0_two_j1_column0": _evaluate(values, "D0", 1, 0),
        "D1_two_j4_column4": _evaluate(values, "D1", 4, 4),
    }
    if len(fixtures["D0_two_j1_column0"]["coupling_stripped_preparation_q"]) != 6:
        raise AssertionError("D0 preparation dimension drifted")
    if len(fixtures["D1_two_j4_column4"]["coupling_stripped_preparation_p"]) != 15:
        raise AssertionError("D1 preparation dimension drifted")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result binds the finite physical spacetime two-form jet to the six-component emitter Cauchy carrier used by the recoil word. For K=dt wedge alpha+beta it constructs the exact orthogonal Hodge projector Pi_co onto ker(delta_Sigma) in every Berger block through two_j=4, verifies Pi_co^2=Pi_co=Pi_co^dagger, delta_Sigma Pi_co=0 and Pi_co d_Sigma=0, and takes q=Pi_co beta and p=Pi_co(partial_t beta-d_Sigma alpha)=Pi_co partial_t beta. It then applies the coupling-stripped positive-energy dual tilde_u=(-p,(Delta_2^co+m^2)q), returning outward rational interval coefficients for any D0/D1 passive column and caller-declared positive rational mass-squared interval. The serialized fixtures use m^2 in [1,2] only as a validation domain, not as a physical mass choice. This closes a finite canonical-trace and coefficient gate; it does not prove that any retained coefficient is nonzero, control the infinite spatial tail, evolve tilde_u through U_E, evaluate I_abc or recoil, restrict to the tangent cone, activate Bridge 3, promote finite-r/all-orders observer stability, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-positive-energy-preparation-coefficients-v1",
        "result_id": "BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS",
        "setting_id": values["physical_cauchy"]["setting_id"],
        "claim_status": "FINITE_COCLOSED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_CERTIFIED_FULL_SPATIAL_SUM_OPEN",
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
            "boundaries": "support-left slice of h0 or h1; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "co-closed spatial two-form Cauchy covector and coupling-stripped positive-energy-dual preparation",
            "degree": "spatial two-form pair (q,p)",
            "parity": "D0 axial and D1 transverse detector labels; no further parity quotient",
            "ell": "two_j=0,...,4",
            "m": "all component-major spatial two-form rows",
            "k": "all passive columns k=0,...,two_j via the certified callable",
            "omega": "advanced finite sine/cosine enclosure at the exact support-left slice",
        },
        "canonical_trace": {
            "full_form_jet_order": ["K", "partial_t K"],
            "spacetime_split": "K=dt wedge alpha+beta",
            "canonical_pair": "(q,p)=(Pi_co beta,Pi_co(partial_t beta-dSigma alpha))",
            "exact_form_reduction": "Pi_co dSigma=0, hence p=Pi_co partial_t beta",
            "positive_energy_dual": "(q,p)->(-p,(Delta_2^co+m^2)q)",
        },
        "projector_audits": projector_audits,
        "coverage": {
            "detectors": ["D0", "D1"],
            "two_j_inclusive": [0, 4],
            "passive_column_count": 30,
            "runtime_mass_domain": "strictly_positive_rational_mass_squared_interval",
            "serialized_validation_mass_squared_interval": ["1", "2"],
        },
        "serialized_fixture_coefficients": fixtures,
        "flags": {
            "CANONICAL_SPATIAL_CAUCHY_TRACE_EXPORTED": True,
            "EXACT_COCLOSED_TWO_FORM_PROJECTORS_TWO_J0_TO_4_CERTIFIED": True,
            "COUPLING_STRIPPED_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS_EXPORTED": True,
            "ALL_D0_D1_COLUMNS_TWO_J0_TO_4_CALLABLE": True,
            "RETAINED_COEFFICIENT_NONVANISHING_CERTIFIED": False,
            "INFINITE_SPATIAL_TAIL_CONTROLLED": False,
            "FREE_EMITTER_EVOLUTION_BOUND": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVOLVE_THE_FINITE_PREPARATIONS_THROUGH_U_E_AND_BIND_THE_FIRST_RETARDED_RECOIL_CHANNEL",
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
        raise SystemExit("stale positive-energy preparation coefficient certificate")
    print("BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
