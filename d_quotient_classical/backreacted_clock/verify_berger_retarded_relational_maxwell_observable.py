#!/usr/bin/env python3
"""Independent replay of the retarded relational Maxwell observable."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    for dependency in data["dependency_refs"].values():
        target = ROOT / dependency["path"]
        if _sha(target) != dependency["sha256"]:
            raise AssertionError(f"dependency digest drifted: {target}")
    for source in data["provenance"]["source_manifest"]:
        target = ROOT / source["path"]
        if _sha(target) != source["sha256"]:
            raise AssertionError(f"source digest drifted: {target}")

    beta = 2 * sp.sqrt(10) / 3
    omega = sp.Rational(3, 4)
    mu = sp.factor(beta / omega)
    volume = 12 * sp.sqrt(10) * sp.pi**2 / 5
    symplectic = sp.factor(-2 * beta * volume)
    poisson = sp.factor(1 / symplectic)
    energy = sp.factor(beta**2 * volume)
    h_coefficient = sp.factor(energy / omega)
    if (mu, symplectic, poisson, h_coefficient) != (
        8 * sp.sqrt(10) / 9,
        -32 * sp.pi**2,
        -1 / (32 * sp.pi**2),
        128 * sp.sqrt(10) * sp.pi**2 / 9,
    ):
        raise AssertionError("independent reduced constants failed")

    x, y, tau = sp.symbols("x y tau", real=True)
    q = x * sp.cos(mu * tau) - y * sp.sin(mu * tau)
    p = x * sp.sin(mu * tau) + y * sp.cos(mu * tau)
    bracket_qp = sp.factor(poisson * (sp.diff(q, x) * sp.diff(p, y) - sp.diff(q, y) * sp.diff(p, x)))
    h = h_coefficient * (x**2 + y**2)
    bracket_qh = sp.factor(poisson * (sp.diff(q, x) * sp.diff(h, y) - sp.diff(q, y) * sp.diff(h, x)))
    bracket_ph = sp.factor(poisson * (sp.diff(p, x) * sp.diff(h, y) - sp.diff(p, y) * sp.diff(h, x)))
    if sp.simplify(bracket_qp - poisson) != 0:
        raise AssertionError("quadrature bracket failed")
    if sp.simplify(bracket_qh - sp.diff(q, tau)) != 0 or sp.simplify(bracket_ph - sp.diff(p, tau)) != 0:
        raise AssertionError("relational Hamilton equations failed")

    if data["relational_redshift"]["one_plus_z"] != "2":
        raise AssertionError("actual redshift is not two")
    if data["retarded_mode_preparation"]["post_source_signal"].find("t>=t_plus") < 0:
        raise AssertionError("post-source mode identity missing")
    cutoff = data["retarded_mode_preparation"]["exact_exterior_form_audit"]
    expected_determinant = str(-4 * sp.sqrt(10) / 3)
    if cutoff["Lorenz_three_form_components"] != {} or cutoff["current_closure_components"] != {}:
        raise AssertionError("cutoff current is not Lorenz/conserved")
    if cutoff["coefficient_matrix_determinant"] != expected_determinant:
        raise AssertionError("cutoff current nontriviality determinant failed")
    if cutoff["nonzero_for_nonconstant_switch"] is not True:
        raise AssertionError("cutoff source was allowed to vanish")
    if data["periodic_clock_and_crossings"]["rotation_is_identity"] is not False:
        raise AssertionError("winding was erased")
    obstruction = data["localized_apparatus_obstruction"]
    if obstruction["first_missing_order"] != "r*kappa=epsilon_R^2*kappa":
        raise AssertionError("mixed obstruction order failed")
    witness = obstruction["normalized_existing_witness"]
    if witness["claim_flag"] != "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED" or witness["value"] is not False:
        raise AssertionError("normalized mixed obstruction witness failed")
    for forbidden in (
        "BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE",
        "BERGER_MIXED_EPSILON_R2_KAPPA_APPARATUS",
        "BERGER_COMPLETE_GLOBAL_S1_CLOCK_OBSERVABLE_WITHOUT_WINDING",
        "BERGER_FULLY_BACKREACTED_MAXWELL_SIGNAL",
        "QUANTUM_CLAIM",
    ):
        if data["flags"][forbidden] is not False:
            raise AssertionError(f"forbidden promotion: {forbidden}")
    print("BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE independent verification: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    verify(args.path)


if __name__ == "__main__":
    main()
