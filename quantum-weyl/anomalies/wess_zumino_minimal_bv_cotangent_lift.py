#!/usr/bin/env python3
"""Construct the exact minimal-BV cotangent lift of the WZ compensator."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
SCHEMA = HERE / "schema/wess-zumino-minimal-bv-cotangent-lift-v1.schema.json"
DEPENDENCIES = {
    "strict_classical_export": ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
    "strict_quantum_import": ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json",
    "WZ_AFN0_preflight": HERE / "certificates/WESS_ZUMINO_COMPENSATOR_EXTENSION_PREFLIGHT.json",
    "Diff_mixed_H14": ROOT / "quantum-weyl/local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json",
}


Monomial = tuple[str, ...]
Polynomial = dict[Monomial, Fraction]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _fraction(value: object) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError("non-exact coefficient")


def _parse(value: dict[str, Any]) -> Polynomial:
    return {
        tuple(term["factors"]): _fraction(term["coefficient"])
        for term in value["terms"]
    }


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        total = result.get(monomial, Fraction()) + coefficient
        if total:
            result[monomial] = total
        else:
            result.pop(monomial, None)
    return result


def _canonical_product(
    factors: Iterable[str], atoms: dict[str, dict[str, Any]]
) -> tuple[Monomial | None, int]:
    ordered: list[str] = []
    sign = 1
    for factor in factors:
        position = len(ordered)
        while (
            position
            and atoms[ordered[position - 1]]["canonical_order"]
            > atoms[factor]["canonical_order"]
        ):
            if (
                atoms[factor]["Grassmann_parity"]
                and atoms[ordered[position - 1]]["Grassmann_parity"]
            ):
                sign *= -1
            position -= 1
        ordered.insert(position, factor)
    if any(
        left == right and atoms[left]["Grassmann_parity"] == 1
        for left, right in zip(ordered, ordered[1:])
    ):
        return None, 0
    return tuple(ordered), sign


def _multiply(
    left: Polynomial, right: Polynomial, atoms: dict[str, dict[str, Any]]
) -> Polynomial:
    result: Polynomial = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            monomial, sign = _canonical_product(lm + rm, atoms)
            if monomial is not None:
                result = _add(result, {monomial: sign * lc * rc})
    return result


def _apply(
    value: Polynomial,
    rows: dict[str, Polynomial],
    atoms: dict[str, dict[str, Any]],
) -> Polynomial:
    result: Polynomial = {}
    for monomial, coefficient in value.items():
        preceding_parity = 0
        for index, factor in enumerate(monomial):
            image = rows[factor]
            if image:
                term = _multiply(
                    _multiply(
                        {monomial[:index]: Fraction(1)}, image, atoms
                    ),
                    {monomial[index + 1 :]: Fraction(1)},
                    atoms,
                )
                sign = -1 if preceding_parity else 1
                result = _add(
                    result,
                    {key: sign * coefficient * scalar for key, scalar in term.items()},
                )
            preceding_parity ^= atoms[factor]["Grassmann_parity"]
    return result


def _q(value: Fraction) -> int | dict[str, int]:
    if value.denominator == 1:
        return value.numerator
    return {"numerator": value.numerator, "denominator": value.denominator}


def _grading(atom: dict[str, Any]) -> tuple[int, int, int, int, Fraction, Fraction]:
    return (
        atom["ghost_number"],
        atom["antifield_number"],
        atom["form_degree"],
        atom["Grassmann_parity"],
        _fraction(atom["mass_dimension"]),
        _fraction(atom["Weyl_weight"]),
    )


def _monomial_grading(
    monomial: Monomial, atoms: dict[str, dict[str, Any]]
) -> tuple[int, int, int, int, Fraction, Fraction]:
    ghost = antifield = form = parity = 0
    dimension = Fraction()
    weight = Fraction()
    for factor in monomial:
        fg, fa, ff, fp, fd, fw = _grading(atoms[factor])
        ghost += fg
        antifield += fa
        form += ff
        parity ^= fp
        dimension += fd
        weight += fw
    return ghost, antifield, form, parity, dimension, weight


def _render(value: Polynomial, atoms: dict[str, dict[str, Any]]) -> dict[str, Any]:
    terms = sorted(
        value.items(),
        key=lambda row: tuple(atoms[factor]["canonical_order"] for factor in row[0]),
    )
    return {
        "terms": [
            {"coefficient": _q(coefficient), "factors": list(monomial)}
            for monomial, coefficient in terms
        ]
    }


def _atom(
    atom_id: str,
    *,
    origin_kind: str,
    origin_id: str,
    ghost: int,
    antifield: int,
    form: int,
    parity: int,
    dimension: int,
    derivative: int,
    symmetry: str,
    covariant_rank: int = 0,
    contravariant_rank: int = 0,
) -> dict[str, Any]:
    return {
        "atom_id": atom_id,
        "origin": {"kind": origin_kind, "id": origin_id},
        "tensor_signature": {
            "covariant_rank": covariant_rank,
            "contravariant_rank": contravariant_rank,
            "symmetry": symmetry,
            "spacetime_parity": "even",
        },
        "covariant_derivative_order": derivative,
        "ghost_number": ghost,
        "antifield_number": antifield,
        "form_degree": form,
        "Grassmann_parity": parity,
        "mass_dimension": dimension,
        "Weyl_weight": 0,
        "canonical_order": -1,
    }


def _matrix_multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)]
        for i in range(4)
    ]


def build() -> dict[str, Any]:
    strict = json.loads(DEPENDENCIES["strict_classical_export"].read_text())
    imported = json.loads(DEPENDENCIES["strict_quantum_import"].read_text())
    preflight = json.loads(DEPENDENCIES["WZ_AFN0_preflight"].read_text())
    diff_h14 = json.loads(DEPENDENCIES["Diff_mixed_H14"].read_text())
    if (
        strict.get("result_state") != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION"
        or imported.get("independent_replay", {}).get("status")
        != "EXECUTABLE_V2_EXPORT_INDEPENDENTLY_REPLAYED"
        or preflight.get("result_state")
        != "AFN0_DIFF_COMPLETED_WZ_PRIMITIVE_CERTIFIED_FULL_EXTENDED_BV_OPEN"
        or diff_h14.get("claim_flags", {}).get("PURE_DIFF_H14_ZERO") is not True
    ):
        raise ValueError("cotangent-lift dependency drifted")

    generators = deepcopy(strict["generators"])
    generators.extend(
        [
            {
                "symbol": "tau",
                "role": "other_minimal",
                "sector": "minimal",
                "tensor_type": {"covariant_rank": 0, "contravariant_rank": 0, "symmetry": "scalar"},
                "ghost_number": 0,
                "antifield_number": 0,
                "form_degree": 0,
                "Grassmann_parity": 0,
                "mass_dimension": 0,
                "Weyl_weight": 0,
            },
            {
                "symbol": "tau_star",
                "role": "other_minimal",
                "sector": "minimal",
                "tensor_type": {"covariant_rank": 0, "contravariant_rank": 0, "symmetry": "scalar_density"},
                "ghost_number": -1,
                "antifield_number": 1,
                "form_degree": 4,
                "Grassmann_parity": 1,
                "mass_dimension": 4,
                "Weyl_weight": 0,
            },
        ]
    )

    raw_atoms = deepcopy(strict["atoms"])
    additions = [
        _atom("tau", origin_kind="generator", origin_id="tau", ghost=0, antifield=0, form=0, parity=0, dimension=0, derivative=0, symmetry="scalar"),
        _atom("tau_star", origin_kind="generator", origin_id="tau_star", ghost=-1, antifield=1, form=4, parity=1, dimension=4, derivative=0, symmetry="scalar_density"),
        _atom("Lie_tau", origin_kind="derived", origin_id="Lie_transport_tau", ghost=1, antifield=0, form=0, parity=1, dimension=0, derivative=1, symmetry="scalar"),
        _atom("Lie_tau_star", origin_kind="derived", origin_id="Lie_transport_tau_star", ghost=0, antifield=1, form=4, parity=0, dimension=4, derivative=1, symmetry="scalar_density"),
        _atom("N_tau", origin_kind="derived", origin_id="tau_star_nabla_tau_Diff_Noether_coordinate", ghost=-1, antifield=1, form=4, parity=1, dimension=5, derivative=1, symmetry="covector_density", covariant_rank=1),
        _atom("Lie_N_tau", origin_kind="derived", origin_id="Lie_transport_tau_Diff_Noether", ghost=0, antifield=1, form=4, parity=0, dimension=5, derivative=1, symmetry="covector_density", covariant_rank=1),
    ]
    raw_atoms.extend(additions)
    for order, atom in enumerate(raw_atoms):
        atom["canonical_order"] = order
    atoms = {atom["atom_id"]: atom for atom in raw_atoms}

    def component(name: str) -> dict[str, Polynomial]:
        rows = {
            row["source_atom"]: _parse(row["image"])
            for row in strict["differential"][name]["rows"]
        }
        rows.update({atom_id: {} for atom_id in atoms if atom_id not in rows})
        return rows

    delta = component("delta")
    gamma = component("gamma")
    delta["xi_star"] = _add(delta["xi_star"], {("N_tau",): Fraction(1)})
    delta["omega_star"] = _add(delta["omega_star"], {("tau_star",): Fraction(1)})
    delta["Lie_xi_star"] = _add(delta["Lie_xi_star"], {("Lie_N_tau",): Fraction(-1)})
    delta["Lie_omega_star"] = _add(delta["Lie_omega_star"], {("Lie_tau_star",): Fraction(-1)})
    gamma["tau"] = {("omega",): Fraction(1), ("Lie_tau",): Fraction(1)}
    gamma["tau_star"] = {("Lie_tau_star",): Fraction(1)}
    gamma["Lie_tau"] = {("Lie_omega",): Fraction(-1)}
    gamma["N_tau"] = {("Lie_N_tau",): Fraction(1)}
    total_q = {atom: _add(delta[atom], gamma[atom]) for atom in atoms}

    for component, shift in ((delta, -1), (gamma, 0)):
        for source, image in component.items():
            sg, sa, sf, sp, sd, sw = _grading(atoms[source])
            for monomial in image:
                tg, ta, tf, tp, td, tw = _monomial_grading(monomial, atoms)
                if (
                    tg != sg + 1
                    or ta != sa + shift
                    or tf != sf
                    or tp != 1 - sp
                    or td != sd
                    or tw != sw
                ):
                    raise ValueError(f"extended grading failed on {source}: {monomial}")

    delta_square: dict[str, Polynomial] = {}
    delta_gamma: dict[str, Polynomial] = {}
    q_square: dict[str, Polynomial] = {}
    for atom in atoms:
        delta_square[atom] = _apply(delta[atom], delta, atoms)
        delta_gamma[atom] = _add(
            _apply(delta[atom], gamma, atoms),
            _apply(gamma[atom], delta, atoms),
        )
        q_square[atom] = _apply(total_q[atom], total_q, atoms)
    if any(delta_square.values()) or any(delta_gamma.values()) or any(q_square.values()):
        raise ValueError("extended compensator differential identities failed")

    q_doublet = [
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 1, 0],
    ]
    h_doublet = [
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
    ]
    qh = _matrix_multiply(q_doublet, h_doublet)
    hq = _matrix_multiply(h_doublet, q_doublet)
    anticommutator = [[qh[i][j] + hq[i][j] for j in range(4)] for i in range(4)]
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    if _matrix_multiply(q_doublet, q_doublet) != [[0] * 4 for _ in range(4)] or anticommutator != identity:
        raise ValueError("dressed compensator quartet does not contract")

    row_payload = {
        name: {
            "delta": _render(delta[name], atoms),
            "gamma": _render(gamma[name], atoms),
            "Q": _render(total_q[name], atoms),
        }
        for name in (
            "tau",
            "tau_star",
            "xi_star",
            "omega_star",
            "Lie_tau",
            "Lie_tau_star",
            "N_tau",
            "Lie_N_tau",
            "Lie_xi_star",
            "Lie_omega_star",
        )
    }
    result = {
        "schema": "quantum-weyl-wess-zumino-minimal-bv-cotangent-lift-v1",
        "result_id": "WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT",
        "result_state": "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_commit": strict["classical_commit"],
        "extension_scope": {
            "base": "frozen strict pure-Weyl minimal BV export",
            "new_generators": ["tau", "tau_star"],
            "generator_count": len(generators),
            "atom_count": len(atoms),
            "locality": "SUPPORT_LOCAL_FIRST_COVARIANT_JETS",
            "coefficient_field": "Q",
        },
        "master_term": {
            "density": "tau_star (xi^mu nabla_mu tau + omega)",
            "derived_rows": {
                "Q_tau": "L_xi tau + omega",
                "delta_omega_star_extension": "+tau_star",
                "delta_xi_star_extension": "+N_tau, with N_tau_mu=tau_star nabla_mu tau",
                "gamma_tau_star": "L_xi tau_star as a scalar density",
            },
            "variational_origin": "all four rows are Euler derivatives of the single displayed minimal master term",
        },
        "extended_rows": row_payload,
        "exact_checks": {
            "delta_squared_zero_on_all_atoms": not any(delta_square.values()),
            "delta_gamma_anticommutator_zero_on_all_atoms": not any(delta_gamma.values()),
            "Q_squared_zero_on_all_atoms": not any(q_square.values()),
            "exact_component_gradings_verified": True,
            "checked_atom_count": len(atoms),
            "differential_sha256": _digest(row_payload),
        },
        "dressed_cotangent_change": {
            "g_hat": "exp(-2 tau) g",
            "g_hat_star": "exp(2 tau) g_star",
            "tau_hat_star": "tau_star + 2 g_{mu nu} g_star^{mu nu} = tau_star + N_omega",
            "canonical_one_form_identity": "g_star delta g + tau_star delta tau = g_hat_star delta g_hat + tau_hat_star delta tau",
            "Weyl_Koszul_Tate_row": "delta omega_star = tau_hat_star",
            "inverse": "g=exp(2 tau)g_hat; g_star=exp(-2 tau)g_hat_star; tau_star=tau_hat_star-2 g_hat g_hat_star",
            "formal_completion": "TAU_ADIC_LOCAL_ANALYTIC_COMPLETION_REQUIRED_FOR_EXPONENTIAL_CHANGE",
        },
        "contractible_quartet": {
            "ordered_basis": ["tau", "omega", "omega_star", "tau_hat_star"],
            "Q_W": q_doublet,
            "h": h_doublet,
            "QW_squared": _matrix_multiply(q_doublet, q_doublet),
            "QW_h": qh,
            "h_QW": hq,
            "anticommutator": anticommutator,
            "number_operator": identity,
            "status": "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES",
        },
        "cohomology_gate": {
            "extended_H14": "NOT_COMPUTED",
            "extended_H04": "NOT_COMPUTED",
            "known_reduction": "in the tau-adic dressed algebra the Weyl quartet contracts, leaving the pure-Diff BV problem for g_hat",
            "missing_exhaustiveness_step": "enumerate the pure-Diff dimension-four H04 quotient in g_hat and bind the existing pure-Diff H14-zero theorem to the completed dressed algebra",
        },
        "qme_lifecycle": {
            "strict_theory": "OBSTRUCTED_STRICT_FIELD_CONTENT",
            "extended_AFN0_breaking": "EXACT_REMOVABLE",
            "extended_minimal_BV_cotangent_lift": "CERTIFIED",
            "full_extended_BV_QME": "NOT_CERTIFIED",
            "residual_transfer": "FORBIDDEN",
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "TAU_ADIC_DRESSED_PURE_DIFF_H04_H14_QUOTIENT",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC certificate appends the compensator and its antifield to the frozen strict minimal-BV atom dictionary, derives every new field and cotangent row from the single support-local master term tau_star(L_xi tau+omega), and independently verifies delta squared, the delta-gamma anticommutator and total Q squared on all extended atoms. The canonical dressed cotangent change turns the Weyl Noether row into delta omega_star=tau_hat_star and exhibits an exact four-generator contractible quartet. The exponential field change is interpreted only in the declared tau-adic local analytic completion. This does not enumerate the resulting pure-Diff H04 basis, bind the pure-Diff H14 theorem to that completion, add nonminimal gauge-fixing partners, certify a full extended BV QME, authorize residual transfer, or establish Lorentzian products, states, positivity, or particles."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    checks = value.get("exact_checks", {})
    lifecycle = value.get("qme_lifecycle", {})
    quartet = value.get("contractible_quartet", {})
    rows = value.get("extended_rows", {})
    dressed = value.get("dressed_cotangent_change", {})
    if (
        value.get("result_state")
        != "EXACT_MINIMAL_BV_COTANGENT_LIFT_CERTIFIED_EXTENDED_COHOMOLOGY_OPEN"
        or any(checks.get(key) is not True for key in (
            "delta_squared_zero_on_all_atoms",
            "delta_gamma_anticommutator_zero_on_all_atoms",
            "Q_squared_zero_on_all_atoms",
            "exact_component_gradings_verified",
        ))
        or quartet.get("anticommutator") != quartet.get("number_operator")
        or rows.get("omega_star", {}).get("delta", {}).get("terms", [])[-1:]
        != [{"coefficient": 1, "factors": ["tau_star"]}]
        or rows.get("xi_star", {}).get("delta", {}).get("terms", [])[-1:]
        != [{"coefficient": 1, "factors": ["N_tau"]}]
        or rows.get("Lie_omega_star", {}).get("delta", {}).get("terms", [])[-1:]
        != [{"coefficient": -1, "factors": ["Lie_tau_star"]}]
        or rows.get("Lie_xi_star", {}).get("delta", {}).get("terms", [])[-1:]
        != [{"coefficient": -1, "factors": ["Lie_N_tau"]}]
        or dressed.get("Weyl_Koszul_Tate_row") != "delta omega_star = tau_hat_star"
        or dressed.get("formal_completion")
        != "TAU_ADIC_LOCAL_ANALYTIC_COMPLETION_REQUIRED_FOR_EXPONENTIAL_CHANGE"
        or value.get("cohomology_gate", {}).get("extended_H14") != "NOT_COMPUTED"
        or value.get("cohomology_gate", {}).get("extended_H04") != "NOT_COMPUTED"
        or lifecycle.get("extended_minimal_BV_cotangent_lift") != "CERTIFIED"
        or lifecycle.get("full_extended_BV_QME") != "NOT_CERTIFIED"
        or lifecycle.get("residual_transfer") != "FORBIDDEN"
    ):
        raise ValueError("WZ minimal-BV cotangent lift crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale WZ minimal-BV cotangent lift: {OUTPUT}")
    print("WZ MINIMAL-BV COTANGENT LIFT: CERTIFIED; EXTENDED COHOMOLOGY OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
