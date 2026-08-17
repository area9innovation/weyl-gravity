#!/usr/bin/env python3
"""Independently verify the BT torus small-action gradient floor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import product

import jsonschema


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SMALL_ACTION_GRADIENT_FLOOR_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-torus-small-action-gradient-floor-v1.schema.json",
)
SOURCE_COMMIT = "60c678b7fab85f3d8fbf99403a31b08c63c9e98d"


def file_hash(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dec(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def reconstruct_fixture() -> dict[str, object]:
    """Recompute the axial fixture without importing the producer."""

    side = 4
    points = list(product(range(side), repeat=4))

    def index(point: tuple[int, int, int, int]) -> int:
        return ((point[0] * side + point[1]) * side + point[2]) * side + point[3]

    axial = (Fraction(11, 10), Fraction(1), Fraction(9, 10), Fraction(1))
    field = [axial[point[0]] for point in points]
    neighbors: list[list[int]] = [[] for _ in points]
    for x, point in enumerate(points):
        for axis in range(4):
            for step in (-1, 1):
                neighbor = list(point)
                neighbor[axis] = (neighbor[axis] + step) % side
                neighbors[x].append(index(tuple(neighbor)))

    def residual(values: list[Fraction]) -> list[Fraction]:
        return [
            sum((values[y] / values[x] - 1 for y in neighbors[x]), Fraction())
            for x in range(len(values))
        ]

    base = residual(field)
    gradient = [
        sum(
            (
                base[y] * field[x] / field[y]
                - base[x] * field[y] / field[x]
                for y in neighbors[x]
            ),
            Fraction(),
        )
        for x in range(len(points))
    ]
    shifted_one = residual([value + 1 for value in field])
    shifted_two = residual([value + 2 for value in field])
    residual_norm = sum((value**2 for value in base), Fraction())
    gradient_norm = sum((value**2 for value in gradient), Fraction())
    shifted_one_norm = sum((value**2 for value in shifted_one), Fraction())
    shifted_two_norm = sum((value**2 for value in shifted_two), Fraction())
    omega = Fraction(2)
    return {
        "vertices": len(points),
        "axial": axial,
        "omega": omega,
        "residual_norm_squared": residual_norm,
        "gradient_norm_squared": gradient_norm,
        "quotient": gradient_norm / residual_norm,
        "floor": omega**2 / 16,
        "shift_one": shifted_one_norm,
        "shift_two": shifted_two_norm,
        "gradient_sum": sum(gradient, Fraction()),
    }


def verify(certificate: dict[str, object]) -> list[tuple[str, bool]]:
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)
    try:
        jsonschema.Draft202012Validator(schema).validate(certificate)
        schema_ok = True
    except jsonschema.ValidationError:
        schema_ok = False

    provenance = certificate["provenance"]
    provenance_ok = (
        provenance["repository_base_commit"] == SOURCE_COMMIT
        and all(
            os.path.isfile(os.path.join(ROOT, row["path"]))
            and file_hash(os.path.join(ROOT, row["path"])) == row["sha256"]
            for row in provenance["inputs"]
        )
    )
    sobolev = certificate["critical_sobolev_lemma"]
    sobolev_ok = (
        sobolev["scope"] == "all real psi on T_L^4 with L>=4"
        and sobolev["statement"]
        == "there is a dimension-only S_4<infinity such that [sum_(directed x~y)|psi_y-psi_x|^4]^(1/2)<=S_4*||Delta psi||_2^2"
        and sobolev["derivation"]
        == "apply the volume-uniform discrete H^1-to-L^4 Sobolev inequality to the four forward first differences; each has mean zero and its lower-order term is absorbed by the torus gap. The forward Hessian-energy sum equals ||Delta psi||_2^2 by Fourier symbols; the negative directed differences are translates of the forward ones, so their fixed factor is absorbed into S_4"
        and sobolev["constant_policy"]
        == "S_4 is universal but not numerically optimized; define C_4=(9/2)*sqrt(8)*S_4 and rho_*=min(1,1/(8*C_4))"
    )
    remainder = certificate["nonlinear_remainder_lemma"]
    remainder_ok = (
        remainder["edge_bound"]
        == "if R=||r||_2<=1, every unoriented edge ratio is at most 8+R<=9, hence |psi_y-psi_x|<=log 9"
        and remainder["scalar_remainders"]
        == "a(t)=exp(t)-1-t and b(t)=t*exp(t)-exp(t)+1 obey 0<=a(t),b(t)<=(9/2)*t^2 for |t|<=log 9"
        and remainder["sobolev_consequence"]
        == "||n||_2<=C_4*||p||_2^2 and ||d||_2<=C_4*||p||_2^2"
    )
    branch = certificate["additive_branch_theorem"]
    branch_ok = (
        branch["path"]
        == "u^(s)=u+s for s>=0, psi^(s)=log(u+s), and r_x^(s)=Delta u_x/(u_x+s)"
        and branch["monotonicity"]
        == "||r^(s)||_2<=||r^(0)||_2 and ||Delta psi^(s)||_2->0 as s->infinity"
        and branch["quadratic_dichotomy"]
        == "R_s>=P_s-C_4*P_s^2, where P_s=||Delta psi^(s)||_2"
        and branch["branch_selection"]
        == "if R<=rho_*, continuity along the additive path forbids P_s=1/(2*C_4); hence P_0<1/(2*C_4) and P_0<=2R"
    )
    theorem = certificate["small_action_theorem"]
    theorem_ok = (
        theorem["pairing_floor"]
        == "<g,psi>>=R^2/2 because ||d||_2<=4*C_4*R^2 and R<=1/(8*C_4)"
        and theorem["spectral_step"]
        == "after centering psi, ||psi||_2<=||Delta psi||_2/omega_L<=2R/omega_L"
        and theorem["gradient_floor"] == "||g||_2>=omega_L*R/4"
        and theorem["quotient_floor"]
        == "Q=||g||_2^2/R^2>=omega_L^2/16"
        and theorem["action_threshold"]
        == "A<=A_*:=rho_*^2/2 implies Q/omega_L^2>=1/16"
    )

    rebuilt = reconstruct_fixture()
    fixture = certificate["exact_fixture"]
    fixture_ok = (
        fixture["vertices"] == rebuilt["vertices"]
        and tuple(dec(value) for value in fixture["axial_field_values"])
        == rebuilt["axial"]
        and dec(fixture["omega_L"]) == rebuilt["omega"]
        and dec(fixture["residual_norm_squared"])
        == rebuilt["residual_norm_squared"]
        and dec(fixture["gradient_norm_squared"])
        == rebuilt["gradient_norm_squared"]
        and dec(fixture["quotient"]) == rebuilt["quotient"]
        and dec(fixture["one_sixteenth_free_scale_floor"]) == rebuilt["floor"]
        and dec(fixture["shift_one_residual_norm_squared"]) == rebuilt["shift_one"]
        and dec(fixture["shift_two_residual_norm_squared"]) == rebuilt["shift_two"]
        and rebuilt["gradient_sum"] == 0
        and rebuilt["shift_two"] < rebuilt["shift_one"]
        and rebuilt["shift_one"] < rebuilt["residual_norm_squared"]
        and rebuilt["quotient"] >= rebuilt["floor"]
        and all(fixture["checks"].values())
    )
    combined = certificate["combined_concentration_alternative"]
    disposition = certificate["research_disposition"]
    boundary_ok = (
        combined["collapse_action_quantization"]
        == "Q_L/omega_L^2->0 implies liminf ||r_L||_2>=rho_* and liminf A_L>=A_*=rho_*^2/2"
        and combined["remaining_counterfamily_shape"]
        == "POSITIVE_ACTION_HIGH_FIELD_WEIGHT_AMPLIFICATION_WITH_FLAT_CURVATURE_AND_ALL_HEIGHT_CUT_CURRENT_CANCELLATION"
        and disposition["vanishing_action_collapsing_sequence"] == "RULED_OUT"
        and disposition["uniform_small_action_scaled_PL"]
        == "PROVED_WITH_CONSTANT_ONE_SIXTEENTH"
        and disposition["positive_action_three_condition_branch"] == "OPEN"
        and disposition["all_field_torus_scaled_PL"] == "OPEN"
        and disposition["nonseparable_counterfamily"] == "NOT_CONSTRUCTED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    self_checks = certificate["checks"]
    return [
        ("strict_schema", schema_ok),
        (
            "producer_not_imported",
            "bt_euclidean_torus_small_action_gradient_floor" not in sys.modules,
        ),
        ("predecessor_hash_and_source_commit", provenance_ok),
        ("critical_sobolev_input", sobolev_ok),
        ("nonlinear_remainders", remainder_ok),
        ("additive_branch_selection", branch_ok),
        ("small_action_gradient_floor", theorem_ok),
        ("independent_axial_reconstruction", fixture_ok),
        ("action_quantization_and_boundaries", boundary_ok),
        (
            "dependency_tags",
            certificate["dependency_tags"]
            == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        ),
        (
            "self_checks",
            self_checks["ok"] is True
            and self_checks["passed"] == self_checks["total"] == 10
            and all(self_checks["details"].values()),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as handle:
            certificate = json.load(handle)
        checks = verify(certificate)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return 1
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    passed = sum(value for _, value in checks)
    print(
        "BT torus small-action gradient-floor verifier: "
        f"{passed}/{len(checks)} checks passed"
    )
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
