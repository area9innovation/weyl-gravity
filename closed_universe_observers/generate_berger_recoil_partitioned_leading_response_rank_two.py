#!/usr/bin/env python3
"""Certify partition-refined detector-selected leading response rank two."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_partitioned_massive_preparation import (
    evaluate_partitioned_positive_energy_preparation_at_support_left,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json"
SCHEMA = PACKAGE / "schema/berger-recoil-partitioned-leading-response-rank-two-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-partitioned-leading-response-rank-two.md"
DEPENDENCIES = {
    "positive_energy_preparation": PACKAGE / "certificates/BERGER_RECOIL_POSITIVE_ENERGY_PREPARATION_COEFFICIENTS.json",
    "dynamical_rank": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "coupling_stripped": PACKAGE / "certificates/BERGER_COUPLING_STRIPPED_DETECTOR_SELECTED_PREPARATIONS.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "forms": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
    "signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "haar": PACKAGE / "certificates/BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR.json",
    "operator_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_partitioned_massive_preparation.py",
    PACKAGE / "verify_berger_recoil_partitioned_leading_response_rank_two.py",
    PACKAGE / "tests/test_berger_recoil_partitioned_leading_response_rank_two.py",
    SCHEMA,
    REPORT,
]
PARTITION_RAIL = (2, 4, 8, 16, 32)
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _coordinate_excludes_zero(value: dict[str, dict[str, str]]) -> bool:
    real = value["real"]
    imaginary = value["imaginary"]
    return not (
        Fraction(real["lower"]) <= 0 <= Fraction(real["upper"])
        and Fraction(imaginary["lower"])
        <= 0
        <= Fraction(imaginary["upper"])
    )


def _evaluate(
    values: dict[str, dict], detector: str, partition_count: int
) -> dict[str, object]:
    result = evaluate_partitioned_positive_energy_preparation_at_support_left(
        detector_image_certificate=values["detector_image"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        moment_certificate=values["moments"],
        exact_kernel_certificate=values["kernels"],
        detector=detector,
        two_j=0,
        column=0,
        mass_squared_interval=VALIDATION_MASS_SQUARED,
        partition_count=partition_count,
    )
    covector_q = result["coupling_stripped_advanced_covector_q"]
    covector_p = result["coupling_stripped_advanced_covector_p"]
    energy = result["positive_energy_lower_bound"]
    return {
        "detector": detector,
        "two_j": 0,
        "column": 0,
        "partition_count": partition_count,
        "cell_width": result["cell_width"],
        "mass_squared_interval": result["mass_squared_interval"],
        "q_coordinate_indices_excluding_zero": [
            index
            for index, entry in enumerate(covector_q)
            if _coordinate_excludes_zero(entry)
        ],
        "p_coordinate_indices_excluding_zero": [
            index
            for index, entry in enumerate(covector_p)
            if _coordinate_excludes_zero(entry)
        ],
        "positive_energy_lower_bound": energy,
        "diagonal_value_uniform_remainder_upper": result[
            "diagonal_value_endpoint_audit"
        ]["uniform_remainder_upper"],
        "diagonal_cosine_uniform_remainder_upper": result[
            "diagonal_cosine_endpoint_audit"
        ]["uniform_remainder_upper"],
    }


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "positive_energy_preparation": "FULL_CANONICAL_POSITIVE_ENERGY_DUAL_CERTIFIED",
        "dynamical_rank": "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED",
        "coupling_stripped": "COUPLING_STRIPPED_FIXED_PREPARATIONS_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "kernels": "MAXWELL_AND_MASSIVE_BLOCKS_TWO_J0_TO_4_EXPORTED",
        "forms": "EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED",
        "signs": "EXACT_SPACETIME_CODERIVATIVE_BLOCKS_EXPORTED",
        "haar": "EXACT_BERGER_HAAR_DENSITY_EXPORTED",
        "operator_word": "EXACT_PETER_WEYL_RECONSTRUCTION_WEIGHT_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    rails = {
        detector: [_evaluate(values, detector, count) for count in PARTITION_RAIL]
        for detector in ("D0", "D1")
    }
    coarse = {detector: rows[0] for detector, rows in rails.items()}
    refined = {detector: rows[-1] for detector, rows in rails.items()}
    if any(row["positive_energy_lower_bound"]["strictly_positive"] for row in coarse.values()):
        raise AssertionError("coarse mutation unexpectedly certified nonvanishing")
    if not all(row["positive_energy_lower_bound"]["strictly_positive"] for row in refined.values()):
        raise AssertionError("32-cell detector energy lower bound is not positive")
    if not refined["D0"]["q_coordinate_indices_excluding_zero"]:
        raise AssertionError("D0 refined covector has no nonzero coordinate witness")
    if not refined["D1"]["q_coordinate_indices_excluding_zero"]:
        raise AssertionError("D1 refined covector has no nonzero coordinate witness")

    peter_weyl = values["operator_word"]["peter_weyl_reconstruction"]
    if peter_weyl["inner_product_weight"] != "(two_j+1)/Vol_Berger":
        raise AssertionError("Peter--Weyl inner-product weight changed")
    if peter_weyl["berger_volume"] != "Vol_Berger=16 pi^2 c with c=3 sqrt(10)/20":
        raise AssertionError("Berger volume convention changed")
    energy_rows = {
        detector: {
            "energy_symbol": f"E_{index}",
            "coefficient_block_uniform_rational_lower_bound": refined[detector][
                "positive_energy_lower_bound"
            ]["energy_lower"],
            "peter_weyl_weight": "(two_j+1)/Vol_Berger=1/(16*pi^2*c) for two_j=0",
            "berger_volume": peter_weyl["berger_volume"],
            "physical_energy_lower_bound": f"({refined[detector]['positive_energy_lower_bound']['energy_lower']})/(16*pi^2*c)",
            "strictly_positive": True,
        }
        for index, detector in enumerate(("D0", "D1"))
    }
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL parameter-domain theorem "
        "repairs the zero-containing whole-support switch hull by integrating the "
        "positive normalized switch on 32 rational cells before applying the finite "
        "massive sine/cosine matrices. For each selected detector the two_j=0, k=0 "
        "advanced Cauchy covector has a coordinate rectangle excluding zero uniformly "
        "for m_a^2 in [1,2]. The positive symplectic dual therefore gives "
        "E_a=<p_a,A_a p_a>+<q_a,L_a q_a>>0 with a machine-readable rational coefficient-block lower "
        "bound and the exact positive Peter-Weyl weight 1/Vol_Berger. Exact Green adjunction identifies the coupling-stripped diagonal "
        "record with E_a; nonzero g_0,g_1 and the causal zero M_01=0 make the selected "
        "leading matrix [[g_0 E_0,0],[M_10,g_1 E_1]] rank two. The 2-cell mutation "
        "fails to prove either diagonal, so nonvanishing is carried by the partitioned "
        "bounds rather than the abstract choice of two probes. This theorem is uniform "
        "only on the validation mass-squared domain [1,2], which is not declared to be "
        "the physical emitter masses. It does not certify arbitrary positive masses, "
        "the infinite-harmonic numerical reconstruction, feedback recoil, the four "
        "absolute-g3 intervals, tangent-cone survival, fixed-background K_Berger "
        "descent, Bridge 3, finite-r/all-orders stability, or a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-partitioned-leading-response-rank-two-v1",
        "result_id": "BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO",
        "setting_id": values["positive_energy_preparation"]["setting_id"],
        "claim_status": "FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_CERTIFIED_ON_MASS_DOMAIN",
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
            "boundaries": "exact h0/h1 compact switch slabs and clock-labelled detector functionals; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "detector-selected full canonical massive-two-form preparation witnessed in its two_j=0,k=0 Peter-Weyl coefficient",
            "degree": "massive spatial two-form Cauchy covector and positive-energy dual",
            "parity": "D0 axial and D1 transverse detector labels",
            "ell": "two_j=0 witness",
            "m": "all three spatial two-form component rows",
            "k": "passive column k=0",
            "omega": "massive finite sine/cosine enclosure on m_0^2,m_1^2 in [1,2]",
        },
        "partition_refinement_rails": rails,
        "positive_energy_witnesses": energy_rows,
        "green_adjoint_response": {
            "identity": "Q_a[d G_A,ret delta(h_a U_E u_a)]=ell_a(u_a)",
            "positive_dual": "u_a=(-A_a p_a,L_a q_a)",
            "diagonal": "ell_a(u_a)=E_a>0",
            "causal_zero": "M_01=0 because h_1 is later than detector D0",
            "matrix": [["g_0 E_0", "0"], ["M_10", "g_1 E_1"]],
            "determinant": "g_0 g_1 E_0 E_1 != 0 for nonzero g_0,g_1",
            "rank": 2,
        },
        "flags": {
            "CELL_PARTITIONED_POSITIVE_SWITCH_GREEN_INTEGRATION_EXPORTED": True,
            "D0_TWO_J0_ADVANCED_COVECTOR_NONZERO_ON_MASS_DOMAIN": True,
            "D1_TWO_J0_ADVANCED_COVECTOR_NONZERO_ON_MASS_DOMAIN": True,
            "GREEN_ADJOINT_DIAGONAL_RESPONSES_STRICTLY_NONZERO_ON_MASS_DOMAIN": True,
            "FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_ON_MASS_DOMAIN": True,
            "ARBITRARY_POSITIVE_MASS_DOMAIN_CERTIFIED": False,
            "INFINITE_HARMONIC_NUMERICAL_RESPONSE_RECONSTRUCTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXTEND_THE_PARTITIONED_RESPONSE_WITNESS_TO_DECLARED_PHYSICAL_MASS_DOMAINS_AND_FEEDBACK_CHANNELS",
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
        raise SystemExit("stale partitioned leading-response rank-two certificate")
    print("BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
