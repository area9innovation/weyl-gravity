#!/usr/bin/env python3
"""Independent verifier for the Schur Wodzicki-residue certificate."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json"
SCHEMA = HERE / "schema/generic-background-ghost-schur-wodzicki-residue-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _independent_replay(*, mutate_mixed_ricci: bool = False) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    # The scalar mixed heat kernel has coefficient
    # A_mn=-Ric_mn/6+g_mn R/12.  Wres(P Delta^-2)=2 A.
    mixed_ricci = Fraction(-1, 7) if mutate_mixed_ricci else Fraction(-1, 6)
    mixed_trace = Fraction(1, 12)
    b1_w_ric = 2 * mixed_ricci
    b1_trw_r = 2 * mixed_trace

    # The S^3 average n_i n_j=delta_ij/4 and the Wres measure converts
    # the normalized angular average by a factor two in (4 pi)^-2 units.
    b2_trw2 = 2 * Fraction(1, 4)

    k_w_ric = Fraction(-1, 3) * b1_w_ric
    k_trw_r = Fraction(-1, 3) * b1_trw_r
    k_trw2 = Fraction(1, 3) * b2_trw2

    r2 = -2 * k_trw_r
    ric2 = -2 * k_w_ric + 4 * k_trw2
    log_r2 = r2 - Fraction(1, 2) * Fraction(1, 27)
    log_ric2 = ric2 - Fraction(1, 2) * Fraction(2, 27)
    return r2, ric2, log_r2, log_ric2


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)

    dependency = payload["dependencies"]["Schatten_split"]
    dependency_path = ROOT / dependency["path"]
    assert dependency_path.is_file()
    assert _sha256(dependency_path) == dependency["sha256"]
    schatten = json.loads(dependency_path.read_text())
    assert schatten["result_id"] == dependency["result_id"]
    assert schatten["critical_local_residue"]["Ricci_basis"] == (
        "Wres(K^2)=(4 pi)^-2 integral[R^2+2 Ric_mn Ric^mn]/27"
    )

    r2, ric2, log_r2, log_ric2 = _independent_replay()
    replay = payload["exact_residues"]["coefficient_replay"]
    assert _fraction(replay["K_Ricci_basis_coefficients"]["R2"]) == r2 == Fraction(1, 9)
    assert _fraction(replay["K_Ricci_basis_coefficients"]["Ric2"]) == ric2 == Fraction(4, 9)
    assert _fraction(replay["log_S_Ricci_basis_coefficients"]["R2"]) == log_r2 == Fraction(5, 54)
    assert _fraction(replay["log_S_Ricci_basis_coefficients"]["Ric2"]) == log_ric2 == Fraction(11, 27)

    # Independent Einstein replay from the exact scalar ratio.
    direct_einstein = Fraction(1, 6) * 2 * (Fraction(1, 2) + Fraction(1, 6))
    general_einstein = r2 + ric2 / 4
    assert direct_einstein == general_einstein == Fraction(2, 9)
    assert _fraction(replay["Einstein_crosscheck"]["residual"]) == 0

    isotropic = replay["isotropic_W_B1_crosscheck"]
    assert _fraction(isotropic["direct_wR"]) == Fraction(1, 3)
    assert _fraction(isotropic["general_wR"]) == Fraction(1, 3)
    assert _fraction(isotropic["residual"]) == 0

    mutated = _independent_replay(mutate_mixed_ricci=True)
    assert mutated != (r2, ric2, log_r2, log_ric2)
    assert mutated[0] + mutated[1] / 4 != direct_einstein
    mutated_isotropic_b1 = 2 * Fraction(-1, 7) + 4 * 2 * Fraction(1, 12)
    assert mutated_isotropic_b1 != Fraction(1, 3)

    flags = payload["claim_flags"]
    assert flags["WODZICKI_RESIDUE_K_COMPUTED"] is True
    assert flags["WODZICKI_RESIDUE_LOG_S_COMPUTED"] is True
    assert flags["FULL_SCHUR_REGULARIZED_DETERMINANT_COMPUTED"] is False
    assert flags["RENORMALIZED_R_K_COMPUTED"] is False
    assert flags["FINITE_PART_R_K2_COMPUTED"] is False
    assert flags["ZETA_SCALE_COEFFICIENT_COMPUTED"] is False
    assert flags["ZETA_MULTIPLICATIVE_ANOMALY_COMPUTED"] is False
    print("GENERIC GHOST SCHUR WODZICKI RESIDUE: INDEPENDENT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
