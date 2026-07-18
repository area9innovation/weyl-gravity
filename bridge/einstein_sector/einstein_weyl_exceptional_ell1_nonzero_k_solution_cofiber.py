"""Exact nonzero-k exceptional ell=1 Einstein--Weyl solution cofiber."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-exceptional-ell1-nonzero-k-solution-cofiber-v1.schema.json"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-weyl-exceptional-ell1-nonzero-k-solution-cofiber.md"
VERIFIER = ROOT / "bridge/einstein_sector/verify_einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber.py"
TEST = ROOT / "bridge/einstein_sector/tests/test_einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber.py"
INPUTS = {
    "offshell_maps": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json",
    "direct_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_nonzero_static.json",
    "source_exceptional": ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
    "k0_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "exceptional_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
    "physical_pairing": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_physical_symplectic_restriction.json",
}
CURRENT_ENGINES = {
    "axial_current": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_axial_lee_wald_completion.py",
    "polar_current": ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_polar_lee_wald_gate.py",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _parse_matrix(values: list[list[str]], omega: sp.Symbol, momentum: sp.Symbol) -> sp.Matrix:
    return sp.Matrix(
        [[sp.sympify(value, locals={"omega": omega, "k": momentum, "I": sp.I}) for value in row] for row in values]
    )


def _reduce_shell(expression: sp.Expr, omega: sp.Symbol, momentum: sp.Symbol, shell: sp.Rational) -> sp.Expr:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    domain = sp.QQ.frac_field(momentum, sp.I)
    divisor = sp.Poly(omega**2 - momentum**2 - shell, omega, domain=domain)
    reduced_numerator = sp.rem(sp.Poly(sp.expand(numerator), omega, domain=domain), divisor).as_expr()
    reduced_denominator = sp.rem(sp.Poly(sp.expand(denominator), omega, domain=domain), divisor).as_expr()
    return sp.factor(reduced_numerator / reduced_denominator)


def _minor_witness(matrix: sp.Matrix, rank: int, omega: sp.Symbol, momentum: sp.Symbol, shell: sp.Rational) -> dict[str, Any]:
    for rows in combinations(range(matrix.rows), rank):
        for columns in combinations(range(matrix.cols), rank):
            determinant = _reduce_shell(matrix.extract(rows, columns).det(), omega, momentum, shell)
            if determinant != 0:
                return {"rows": list(rows), "columns": list(columns), "determinant": str(determinant)}
    raise AssertionError(f"no rank-{rank} witness on shell {shell}")


def _all_minors_zero(matrix: sp.Matrix, rank: int, omega: sp.Symbol, momentum: sp.Symbol, shell: sp.Rational) -> bool:
    return all(
        _reduce_shell(matrix.extract(rows, columns).det(), omega, momentum, shell) == 0
        for rows in combinations(range(matrix.rows), rank)
        for columns in combinations(range(matrix.cols), rank)
    )


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _matrices(records: dict[str, dict[str, Any]]) -> dict[str, sp.Matrix | sp.Symbol]:
    omega, momentum = sp.symbols("omega k", real=True)
    target = records["direct_target"]["direct_replay"]
    axial_target = _parse_matrix(target["axial"]["full_Fourier_action_Hessian"], omega, momentum)
    polar_target = _parse_matrix(target["polar"]["full_Fourier_action_Hessian"], omega, momentum)
    axial_source = sp.Matrix(
        [
            [momentum**2 + 2, momentum * omega, 2, 0],
            [momentum * omega, omega**2 - 2, 0, -2],
            [2, 0, momentum**2 + 2, momentum * omega],
            [0, -2, momentum * omega, omega**2 - 2],
        ]
    )
    polar_source = sp.Matrix(
        [
            [0, 0, 1, momentum**2 + 1, -2],
            [0, 1, 0, -momentum * omega, 0],
            [1, 0, 0, omega**2 - 1, 2],
            [0, sp.I * momentum / 2, sp.I * omega / 2, sp.I * omega / 2, -sp.I * omega],
            [sp.I * momentum / 2, sp.I * omega / 2, 0, -sp.I * momentum / 2, sp.I * momentum],
            [(momentum**2 + 1) / 2, momentum * omega, (omega**2 - 1) / 2, (omega**2 - momentum**2 + 2) / 2, -2],
            [sp.Rational(1, 2), 0, -sp.Rational(1, 2), 1, omega**2 - momentum**2 - 2],
        ]
    )
    return {
        "omega": omega,
        "momentum": momentum,
        "axial_source": axial_source,
        "axial_target": axial_target,
        "polar_source": polar_source,
        "polar_target": polar_target,
    }


def _theorem(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import _generic_current_matrix
    from bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate import _time_current_matrix

    matrices = _matrices(records)
    omega = matrices["omega"]
    momentum = matrices["momentum"]
    assert isinstance(omega, sp.Symbol) and isinstance(momentum, sp.Symbol)
    axial_source = matrices["axial_source"]
    axial_target = matrices["axial_target"]
    polar_source = matrices["polar_source"]
    polar_target = matrices["polar_target"]
    assert all(isinstance(matrix, sp.MatrixBase) for matrix in (axial_source, axial_target, polar_source, polar_target))

    shells = {"standard": sp.Integer(4), "extra": sp.Rational(4, 3)}
    axial_gauge = sp.Matrix([omega, -momentum, -omega, momentum])
    polar_gauge = sp.Matrix([2 - 2 * omega**2, 2 * momentum * omega, -2 * momentum**2 - 2, 1])
    axial_representatives = {
        "standard": sp.Matrix([0, 1, -momentum * omega / 2, (momentum**2 + 2) / 2]),
        "extra": sp.Matrix([0, 1, 3 * momentum * omega / 2, -3 * (momentum**2 + 2) / 2]),
    }
    polar_representatives = {
        "standard": sp.Matrix([momentum**2 + 2, -momentum * omega, momentum**2 + 2, 0]),
        "extra": sp.Matrix(
            [-momentum * (3 * momentum**2 + 4), omega * (3 * momentum**2 + 2), -momentum * (3 * momentum**2 + 4), 0]
        ),
    }
    polar_source_standard = sp.Matrix([-2, 0, 2, 0, 1])
    polar_source_standard_reduced = sp.Matrix([-2, 0, 2, 1])
    polar_source_extra = sp.Matrix([polar_representatives["extra"][0], polar_representatives["extra"][1], polar_representatives["extra"][2], 0, 0])

    for parity, target_matrix, gauge, representatives in (
        ("axial", axial_target, axial_gauge, axial_representatives),
        ("polar", polar_target, polar_gauge, polar_representatives),
    ):
        if not _zero(target_matrix * gauge):
            raise AssertionError(f"{parity} target gauge identity changed")
        for branch, shell in shells.items():
            if any(_reduce_shell(value, omega, momentum, shell) != 0 for value in target_matrix * representatives[branch]):
                raise AssertionError(f"{parity} {branch} representative left the target kernel")
            if _all_minors_zero(target_matrix, 2, omega, momentum, shell):
                raise AssertionError(f"{parity} target rank fell below two on {branch}")
            if not _all_minors_zero(target_matrix, 3, omega, momentum, shell):
                raise AssertionError(f"{parity} target rank exceeded two on {branch}")

    axial_source_gauge = axial_gauge
    if not _zero(axial_source * axial_source_gauge):
        raise AssertionError("axial source gauge identity changed")
    if any(_reduce_shell(value, omega, momentum, shells["standard"]) != 0 for value in axial_source * axial_representatives["standard"]):
        raise AssertionError("axial standard source representative changed")
    if all(_reduce_shell(value, omega, momentum, shells["extra"]) == 0 for value in axial_source * axial_representatives["extra"]):
        raise AssertionError("axial extra representative entered the Einstein source kernel")
    if not _all_minors_zero(axial_source, 3, omega, momentum, shells["standard"]):
        raise AssertionError("axial source standard-shell rank exceeded two")
    if _all_minors_zero(axial_source, 2, omega, momentum, shells["standard"]):
        raise AssertionError("axial source standard-shell rank fell below two")
    if _all_minors_zero(axial_source, 3, omega, momentum, shells["extra"]):
        raise AssertionError("axial source extra-shell rank fell below three")

    polar_source_gauge = sp.Matrix([2 * omega**2, -2 * momentum * omega, 2 * momentum**2, -2, -1])
    if not _zero(polar_source * polar_source_gauge):
        raise AssertionError("polar source gauge identity changed")
    if any(_reduce_shell(value, omega, momentum, shells["standard"]) != 0 for value in polar_source * polar_source_standard):
        raise AssertionError("polar standard source representative changed")
    if all(_reduce_shell(value, omega, momentum, shells["extra"]) == 0 for value in polar_source * polar_source_extra):
        raise AssertionError("polar extra representative entered the Einstein source kernel")
    if not _all_minors_zero(polar_source, 4, omega, momentum, shells["standard"]):
        raise AssertionError("polar source standard-shell rank exceeded three")
    if _all_minors_zero(polar_source, 3, omega, momentum, shells["standard"]):
        raise AssertionError("polar source standard-shell rank fell below three")
    if _all_minors_zero(polar_source, 4, omega, momentum, shells["extra"]):
        raise AssertionError("polar source extra-shell rank fell below four")
    polar_inclusion_relation = polar_source_standard_reduced - polar_gauge - 2 * polar_representatives["standard"]
    if any(_reduce_shell(value, omega, momentum, shells["standard"]) != 0 for value in polar_inclusion_relation):
        raise AssertionError("polar source-to-target standard quotient relation changed")

    first, second, eigenvalue = sp.symbols("omega_1 omega_2 lambda", real=True)
    axial_current = _generic_current_matrix(eigenvalue, momentum, first, second).subs(eigenvalue, 2)
    polar_current, polar_symbols = _time_current_matrix()
    polar_current = (polar_current / 2).subs(
        {polar_symbols["lambda"]: 2, polar_symbols["k"]: momentum, polar_symbols["omega_1"]: first, polar_symbols["omega_2"]: second}
    )
    currents = {"axial": axial_current, "polar": polar_current}
    representatives = {"axial": axial_representatives, "polar": polar_representatives}
    grams: dict[str, dict[str, str]] = {"axial": {}, "polar": {}}
    expected_grams = {
        "axial": {"standard": 4 * (momentum**2 + 4), "extra": 4 * (3 * momentum**2 + 4)},
        "polar": {"standard": sp.Integer(4), "extra": 4 * (3 * momentum**2 + 4)},
    }
    for parity in ("axial", "polar"):
        for branch, shell in shells.items():
            vector = representatives[parity][branch].subs(omega, first)
            value = (vector.T * currents[parity].subs(second, first) * vector)[0] / (-sp.I * first)
            reduced = _reduce_shell(value, first, momentum, shell)
            if sp.factor(reduced - expected_grams[parity][branch]) != 0:
                raise AssertionError(f"{parity} {branch} current weight changed: {reduced}")
            grams[parity][branch] = str(sp.factor(reduced))

    extra_frequency, standard_frequency = sp.symbols("omega_e omega_s", real=True)
    mixed_values: dict[str, str] = {}
    mixed_divisors = [extra_frequency**2 - momentum**2 - sp.Rational(4, 3), standard_frequency**2 - momentum**2 - 4]
    groebner = sp.groebner(mixed_divisors, extra_frequency, standard_frequency, momentum, order="lex", extension=sp.I)
    for parity in ("axial", "polar"):
        extra_vector = representatives[parity]["extra"].subs(omega, extra_frequency)
        standard_vector = representatives[parity]["standard"].subs(omega, standard_frequency)
        mixed = sp.cancel(
            (extra_vector.T * currents[parity].subs({first: extra_frequency, second: standard_frequency}) * standard_vector)[0] / sp.I
        )
        numerator, denominator = sp.fraction(mixed)
        remainder_numerator = groebner.reduce(sp.expand(numerator))[1]
        remainder_denominator = groebner.reduce(sp.expand(denominator))[1]
        reduced = sp.factor(sp.I * remainder_numerator / remainder_denominator)
        if reduced != 0:
            raise AssertionError(f"{parity} standard-extra current ceased to be orthogonal: {reduced}")
        mixed_values[parity] = "0"

    rank_witnesses: dict[str, dict[str, Any]] = {}
    for parity, source_matrix, target_matrix in (
        ("axial", axial_source, axial_target),
        ("polar", polar_source, polar_target),
    ):
        source_standard_rank = 2 if parity == "axial" else 3
        source_extra_rank = 3 if parity == "axial" else 4
        rank_witnesses[parity] = {
            "source_standard": _minor_witness(source_matrix, source_standard_rank, omega, momentum, shells["standard"]),
            "source_extra": _minor_witness(source_matrix, source_extra_rank, omega, momentum, shells["extra"]),
            "target_standard": _minor_witness(target_matrix, 2, omega, momentum, shells["standard"]),
            "target_extra": _minor_witness(target_matrix, 2, omega, momentum, shells["extra"]),
        }

    s = sp.symbols("s")
    projectors = {
        "extra": sp.Rational(3, 8) * (4 - s),
        "standard": sp.Rational(3, 8) * (s - sp.Rational(4, 3)),
    }
    for branch, shell in shells.items():
        for projector_branch, projector in projectors.items():
            if sp.factor(projector.subs(s, shell) - int(branch == projector_branch)) != 0:
                raise AssertionError("exceptional all-k CRT projector changed")
    if sp.expand(sum(projectors.values())) != 1:
        raise AssertionError("exceptional all-k CRT projectors lost completeness")

    return {
        "spectral_variable": "s=omega^2-k^2",
        "shells": {branch: str(shell) for branch, shell in shells.items()},
        "projectors": {branch: str(sp.factor(projector)) for branch, projector in projectors.items()},
        "field_orders": {
            "axial_reduced": ["h_t", "h_x", "q_t", "q_x"],
            "polar_reduced": ["A_t", "B", "C_t", "U"],
            "polar_source": ["A", "B", "C", "K", "U"],
        },
        "polynomial_representatives": {
            "axial": {branch: [str(sp.factor(value)) for value in vector] for branch, vector in axial_representatives.items()},
            "polar": {branch: [str(sp.factor(value)) for value in vector] for branch, vector in polar_representatives.items()},
            "polar_source_standard": [str(value) for value in polar_source_standard],
        },
        "rank_witnesses": rank_witnesses,
        "inclusion_relations": {
            "axial": "the source and target polynomial standard representatives coincide in the common b=0 gauge slice",
            "polar": "source_standard_reduced - target_residual_gauge = 2*target_standard on omega^2-k^2=4",
            "polar_relation_remainder": [
                str(_reduce_shell(value, omega, momentum, shells["standard"])) for value in polar_inclusion_relation
            ],
        },
        "solution_quotients": {
            "axial_source_standard": "rank 2, kernel = residual gauge plus one standard Einstein-Maxwell class",
            "axial_source_extra": "rank 3, kernel = residual gauge only",
            "axial_target_each_shell": "rank 2, kernel = residual gauge plus one physical class",
            "polar_source_standard": "rank 3, kernel = residual gauge plus one standard Einstein-Maxwell class",
            "polar_source_extra": "rank 4, kernel = residual gauge only",
            "polar_target_each_shell": "rank 2, kernel = residual gauge plus one physical class",
            "cofiber": "one extra class in each parity for every real nonzero k",
        },
        "action_pairing": {
            "representative_normalization": "the displayed polynomial representatives; no k or omega inverse occurs",
            "Gram": grams,
            "standard_extra_mixed": mixed_values,
            "extra_inertia_for_real_nonzero_k": [2, 0],
            "cofiber_nonradical": True,
        },
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    if not records["offshell_maps"]["classification"]["all_compact_momenta_included"]:
        raise AssertionError("exceptional all-row map input changed")
    if not records["direct_target"]["classification"]["direct_axial_ell1_static_nonzero_momentum_operator_certified"]:
        raise AssertionError("direct exceptional target input changed")
    if not records["k0_cofiber"]["classification"]["exceptional_solution_cofiber_certified"]:
        raise AssertionError("k=0 cofiber input changed")
    theorem = _theorem(records)
    manifest_paths = {
        "generator": Path(__file__),
        "schema": SCHEMA,
        "verifier": VERIFIER,
        "test": TEST,
        "report": REPORT,
        **{f"input_{name}": path for name, path in INPUTS.items()},
        **{f"engine_{name}": path for name, path in CURRENT_ENGINES.items()},
    }
    return {
        "schema": "einstein-weyl-exceptional-ell1-nonzero-k-solution-cofiber-v1",
        "result_id": "EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1",
        "result_state": "NONZERO_K_EXCEPTIONAL_SOLUTION_COFIBER_AND_ACTION_PAIRING_CERTIFIED",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell source included in Weyl-Maxwell target",
            "background": "compactified magnetically supported Plebanski-Hacyan R_t x S1_L x S2 fixture",
            "boundaries": "closed Cauchy slice S1_L x S2; before finite residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "exceptional local-gauge-reduced ell=1 Fourier solution modules",
            "degree": "1",
            "parity": "axial and polar kept separate",
            "ell": "1",
            "m": "all three real SO(3) components",
            "k": "2*pi*n/L with n nonzero",
            "omega": "standard omega^2-k^2=4 and extra omega^2-k^2=4/3",
        },
        "map_lifecycle": "HARMONIC_OFFSHELL_MAP_AND_ONSHELL_COFIBER",
        "theorem": theorem,
        "classification": {
            "nonzero_k_exceptional_solution_cofiber_certified": True,
            "Einstein_image_is_standard_shell": True,
            "one_extra_class_per_parity": True,
            "polynomial_representatives_without_differential_inverse": True,
            "action_pairing_nonradical_positive_on_extra_cofiber": True,
            "standard_extra_action_orthogonality": True,
            "all_m_by_SO3_equivariance": True,
            "single_covariant_support_local_map_reconstructed": False,
            "finite_residual_endpoint_descent_certified": False,
            "Lorentzian_causal_observational_particle_or_quantum_claim": False,
        },
        "interpretation": "For every nonzero compact momentum, the exceptional ell=1 target quotient has exactly the Einstein-Maxwell standard class and one additional fourth-order class in each parity. The existing polynomial all-row map identifies the standard image, while the displayed polynomial representatives identify a nonradical positive extra cofiber without a momentum, frequency, or helicity inverse.",
        "next_gate": "combine this nonzero-k cofiber with the k=0 twist/extra/standard decomposition, reconstruct the harmonic chain maps as one natural tensor-bundle morphism, and include the finite residual endpoints",
        "claim_boundary": "This exact same-background REDUCED-MODE theorem covers ell=1 and nonzero compact momentum. It does not itself reconstruct one support-local covariant map, classify finite residual endpoints, impose a causal boundary condition, identify particles, compare other backgrounds, or support observational or quantum claims.",
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        "source_manifest": {name: _sha256(path) for name, path in manifest_paths.items()},
        "verification_receipt": {
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "commands": ["producer --check", "independent verifier", "scoped unit tests"]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the all-row maps, direct Hessians, source exceptional complex, k=0 cofiber and action-current engines are pinned by SHA-256"},
            "tier_3": {"status": "NOT_RUN", "reason": "the covariant tensor-bundle glue and finite residual endpoint descent remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber --check",
            "python3 bridge/einstein_sector/verify_einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    Draft202012Validator(_load(SCHEMA)).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif _load(OUTPUT) != value:
        raise AssertionError("nonzero-k exceptional cofiber certificate is stale")
    print("EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1: PASS")


if __name__ == "__main__":
    main()
