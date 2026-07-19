"""Independent verifier for the candidate-13 same-fibre resonance census."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.schema.json"
INPUTS = {
    "candidate13": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json",
    "candidate13_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json",
    "ell0_nonzero_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell0_homogeneous_nonzero_frequency": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "ell1_nonzero_k_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
}
MASSES = {
    "q_minus": 6 - 2 * sp.sqrt(3),
    "p_extra": sp.Rational(16, 3),
    "q_plus": 6 + 2 * sp.sqrt(3),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def verify_interval(defect: sp.Expr, stored: dict[str, object]) -> None:
    witness = certified_nonzero_interval(sp.factor(defect))
    if witness is None:
        raise AssertionError("candidate-13 verifier found a same-fibre collision")
    bounds, digits = witness
    expected = {
        "expression": sp.sstr(sp.factor(defect)),
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }
    if stored != expected:
        raise AssertionError("candidate-13 same-fibre interval witness changed")


def verify() -> None:
    value = json.loads(CERTIFICATE.read_text())
    jsonschema.validate(value, json.loads(SCHEMA.read_text()))
    if value["schema_sha256"] != sha(SCHEMA):
        raise AssertionError("candidate-13 same-fibre schema hash changed")
    for name, path in INPUTS.items():
        if value["provenance"]["inputs"][name]["sha256"] != sha(path):
            raise AssertionError(f"candidate-13 same-fibre input hash changed: {name}")
    candidate = json.loads(INPUTS["candidate13"].read_text())
    rho = parse(candidate["rho"])
    expected_keys = []
    channel_index = {
        (row["momentum_fibre_abs_n"], row["first_branch"], row["second_branch"], row["temporal_channel"]): row
        for row in value["channels"]
    }
    if len(channel_index) != len(value["channels"]):
        raise AssertionError("candidate-13 same-fibre channel key repeated")
    defect_count = 0
    for momentum_number in (1, 2):
        frequencies = {
            branch: sp.sqrt(momentum_number**2 * rho + mass_square)
            for branch, mass_square in MASSES.items()
        }
        for first_branch, second_branch in itertools.combinations_with_replacement(MASSES, 2):
            channels = [("SUM", frequencies[first_branch] + frequencies[second_branch], 4 * momentum_number**2 * rho)]
            if first_branch != second_branch:
                channels.append(("DIFFERENCE", frequencies[first_branch] - frequencies[second_branch], sp.S.Zero))
            for temporal_channel, output_frequency, output_momentum_squared in channels:
                key = (momentum_number, first_branch, second_branch, temporal_channel)
                expected_keys.append(key)
                row = channel_index[key]
                expected_ell0 = (
                    "empty nonzero-Fourier physical quotient at K=2*n*sqrt(rho)"
                    if temporal_channel == "SUM"
                    else "empty homogeneous physical quotient at K=0 and Omega!=0"
                )
                if row["ell0_disposition"] != expected_ell0:
                    raise AssertionError("candidate-13 ell=0 channel disposition changed")
                spectral_value = sp.factor(output_frequency**2 - output_momentum_squared)
                if sp.simplify(parse(row["spectral_value_s"]) - spectral_value) != 0:
                    raise AssertionError("candidate-13 same-fibre spectral value changed")
                expected_defects = [spectral_value - sp.Rational(4, 3), spectral_value - 4]
                for output_ell in (2, 3, 4):
                    angular = output_ell * (output_ell + 1)
                    expected_defects.extend(
                        [spectral_value - (angular - sp.Rational(2, 3)), (spectral_value - angular) ** 2 - 2 * angular]
                    )
                if len(row["nonzero_shell_defects"]) != len(expected_defects):
                    raise AssertionError("candidate-13 same-fibre target-shell count changed")
                for defect, stored in zip(expected_defects, row["nonzero_shell_defects"]):
                    verify_interval(defect, stored["witness"])
                    defect_count += 1
    if set(channel_index) != set(expected_keys) or len(expected_keys) != 18 or defect_count != 144:
        raise AssertionError("candidate-13 same-fibre census completeness changed")
    classification = value["classification"]
    if not (
        classification["candidate_13_all_nonzero_same_fibre_channels_off_shell"]
        and classification["ell0_nonzero_fourier_quotient_empty_imported"]
        and classification["ell0_homogeneous_nonzero_frequency_quotient_empty_imported"]
        and classification["ell1_through_ell4_nonzero_shell_defects_certified"]
        and not classification["same_fibre_nonzero_frequency_source_matrices_required_for_bounded_gate"]
    ):
        raise AssertionError("candidate-13 same-fibre nonzero classification weakened")
    if (
        classification["same_fibre_zero_frequency_source_matrices_classified"]
        or classification["mixed_Einstein_extra_taub_intersection_classified"]
        or classification["complete_mixed_two_fibre_tangent_cone_classified"]
        or classification["causal_or_quantum_claim"]
    ):
        raise AssertionError("candidate-13 same-fibre census exceeded scope")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_SAME_FIBRE_RESONANCE_CENSUS independent verification: PASS")


if __name__ == "__main__":
    verify()
