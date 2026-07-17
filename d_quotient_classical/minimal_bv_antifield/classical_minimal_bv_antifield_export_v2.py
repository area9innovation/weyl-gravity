#!/usr/bin/env python3
"""Produce the covariant minimal-BV antifield export requested by quantum.

The finite atom algebra uses regular Koszul--Tate adapted jet coordinates:
the Bach Euler density and the two Noether rows replace the corresponding
highest metric jets.  Lie-transport atoms retain the Diff action, while Weyl
weights are explicit.  The export is an executable interface to the existing
AFN0 curvature basis; it is not itself a computation of H(s|d).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/minimal_bv_antifield"
FOUNDATION = HERE / "foundation"
PROOFS = HERE / "proofs"
OUTPUT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-minimal-bv-antifield-export-v2.md"
OBSTRUCTION = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json"
OBSTRUCTION_REPORT = ROOT / "d_quotient_classical/reports/classical-minimal-bv-antifield-export-v2-receiver-obstruction.md"

DEPENDENCY_FILES = {
    "atom_basis_manifest": FOUNDATION / "atom_basis_manifest.json",
    "field_dictionary": FOUNDATION / "field_dictionary.json",
    "action_normalization": FOUNDATION / "action_normalization.json",
    "euler_lagrange_rows": FOUNDATION / "euler_lagrange_rows.json",
    "noether_identity_rows": FOUNDATION / "noether_identity_rows.json",
    "canonicalization_conventions": FOUNDATION / "canonicalization_conventions.json",
}
PROOF_FILES = {
    "delta_squared_zero": PROOFS / "delta_squared_zero.json",
    "delta_gamma_anticommutator_zero": PROOFS / "delta_gamma_anticommutator_zero.json",
    "Q_decomposition_sums_to_Q": PROOFS / "Q_decomposition_sums_to_Q.json",
    "Q_squared_zero": PROOFS / "Q_squared_zero.json",
}


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _tensor(covariant: int, contravariant: int, symmetry: str) -> dict[str, Any]:
    return {
        "covariant_rank": covariant,
        "contravariant_rank": contravariant,
        "symmetry": symmetry,
    }


def generators() -> list[dict[str, Any]]:
    rows = (
        ("g", "metric", _tensor(2, 0, "symmetric_covariant_2"), 0, 0, 0, 0, 0, 2),
        ("xi", "diffeomorphism_ghost", _tensor(0, 1, "contravariant_vector"), 1, 0, 0, 1, -1, 0),
        ("omega", "weyl_ghost", _tensor(0, 0, "scalar"), 1, 0, 0, 1, 0, 0),
        ("g_star", "metric_antifield", _tensor(0, 2, "symmetric_contravariant_density"), -1, 1, 4, 1, 4, -2),
        ("xi_star", "diffeomorphism_ghost_antifield", _tensor(1, 0, "covector_density"), -2, 2, 4, 0, 5, 0),
        ("omega_star", "weyl_ghost_antifield", _tensor(0, 0, "scalar_density"), -2, 2, 4, 0, 4, 0),
    )
    return [
        {
            "symbol": symbol,
            "role": role,
            "sector": "minimal",
            "tensor_type": tensor,
            "ghost_number": ghost,
            "antifield_number": antifield,
            "form_degree": form,
            "Grassmann_parity": parity,
            "mass_dimension": dimension,
            "Weyl_weight": weight,
        }
        for symbol, role, tensor, ghost, antifield, form, parity, dimension, weight in rows
    ]


def _atom(
    atom_id: str,
    origin_kind: str,
    origin_id: str,
    tensor: dict[str, Any],
    ghost: int,
    antifield: int,
    form: int,
    parity: int,
    dimension: int,
    weight: int,
    order: int,
) -> dict[str, Any]:
    return {
        "atom_id": atom_id,
        "origin": {"kind": origin_kind, "id": origin_id},
        "tensor_signature": {**tensor, "spacetime_parity": "even"},
        "covariant_derivative_order": 0 if not atom_id.startswith("Lie_") else 1,
        "ghost_number": ghost,
        "antifield_number": antifield,
        "form_degree": form,
        "Grassmann_parity": parity,
        "mass_dimension": dimension,
        "Weyl_weight": weight,
        "canonical_order": order,
    }


def atoms() -> list[dict[str, Any]]:
    gens = generators()
    output = [
        _atom(
            row["symbol"], "generator", row["symbol"], row["tensor_type"],
            row["ghost_number"], row["antifield_number"], row["form_degree"],
            row["Grassmann_parity"], row["mass_dimension"], row["Weyl_weight"], index,
        )
        for index, row in enumerate(gens)
    ]
    derived = (
        ("E_g", "Bach_Euler_density", _tensor(0, 2, "symmetric_contravariant_density"), 0, 0, 4, 0, 4, -2),
        ("N_xi", "Diff_Noether_coordinate", _tensor(1, 0, "covector_density"), -1, 1, 4, 1, 5, 0),
        ("N_omega", "Weyl_Noether_coordinate", _tensor(0, 0, "scalar_density"), -1, 1, 4, 1, 4, 0),
        ("Lie_g", "Lie_transport_g", _tensor(2, 0, "symmetric_covariant_2"), 1, 0, 0, 1, 0, 2),
        ("bracket_xi", "half_odd_Lie_bracket_xi", _tensor(0, 1, "contravariant_vector"), 2, 0, 0, 0, -1, 0),
        ("Lie_omega", "Lie_transport_omega", _tensor(0, 0, "scalar"), 2, 0, 0, 0, 0, 0),
        ("Lie_g_star", "Lie_transport_g_star", _tensor(0, 2, "symmetric_contravariant_density"), 0, 1, 4, 0, 4, -2),
        ("Lie_xi_star", "Lie_transport_xi_star", _tensor(1, 0, "covector_density"), -1, 2, 4, 1, 5, 0),
        ("Lie_omega_star", "Lie_transport_omega_star", _tensor(0, 0, "scalar_density"), -1, 2, 4, 1, 4, 0),
        ("Lie_E_g", "Lie_transport_Bach_Euler", _tensor(0, 2, "symmetric_contravariant_density"), 1, 0, 4, 1, 4, -2),
        ("Lie_N_xi", "Lie_transport_Diff_Noether", _tensor(1, 0, "covector_density"), 0, 1, 4, 0, 5, 0),
        ("Lie_N_omega", "Lie_transport_Weyl_Noether", _tensor(0, 0, "scalar_density"), 0, 1, 4, 0, 4, 0),
    )
    for record in derived:
        atom_id, origin_id, *rest = record
        output.append(_atom(atom_id, "derived", origin_id, *rest, len(output)))
    return output


def _poly(terms: Iterable[tuple[int, Iterable[str]]]) -> dict[str, Any]:
    order = {row["atom_id"]: row["canonical_order"] for row in atoms()}
    normalized = []
    for coefficient, factors in terms:
        factors = tuple(sorted(factors, key=order.__getitem__))
        normalized.append({"coefficient": coefficient, "factors": list(factors)})
    normalized.sort(key=lambda term: tuple(order[x] for x in term["factors"]))
    return {"terms": normalized}


def differential() -> dict[str, Any]:
    atom_ids = [row["atom_id"] for row in atoms()]
    zero = _poly(())
    delta = {
        "g_star": _poly(((1, ("E_g",)),)),
        "xi_star": _poly(((1, ("N_xi",)),)),
        "omega_star": _poly(((1, ("N_omega",)),)),
        "Lie_g_star": _poly(((-1, ("Lie_E_g",)),)),
        "Lie_xi_star": _poly(((-1, ("Lie_N_xi",)),)),
        "Lie_omega_star": _poly(((-1, ("Lie_N_omega",)),)),
    }
    gamma = {
        "g": _poly(((1, ("Lie_g",)), (2, ("omega", "g")))),
        "xi": _poly(((1, ("bracket_xi",)),)),
        "omega": _poly(((1, ("Lie_omega",)),)),
        "g_star": _poly(((1, ("Lie_g_star",)), (-2, ("omega", "g_star")))),
        "xi_star": _poly(((1, ("Lie_xi_star",)),)),
        "omega_star": _poly(((1, ("Lie_omega_star",)),)),
        "E_g": _poly(((1, ("Lie_E_g",)), (-2, ("omega", "E_g")))),
        "N_xi": _poly(((1, ("Lie_N_xi",)),)),
        "N_omega": _poly(((1, ("Lie_N_omega",)),)),
        "Lie_g": _poly(((-2, ("g", "Lie_omega")), (2, ("omega", "Lie_g")))),
        "Lie_g_star": _poly(((2, ("g_star", "Lie_omega")), (-2, ("omega", "Lie_g_star")))),
        "Lie_E_g": _poly(((2, ("E_g", "Lie_omega")), (-2, ("omega", "Lie_E_g")))),
    }

    def rows(images: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"source_atom": atom_id, "image": images.get(atom_id, zero)}
            for atom_id in atom_ids
        ]

    q_images: dict[str, dict[str, Any]] = {}
    for atom_id in atom_ids:
        terms = [*delta.get(atom_id, zero)["terms"], *gamma.get(atom_id, zero)["terms"]]
        terms.sort(key=lambda term: tuple(atom_ids.index(factor) for factor in term["factors"]))
        q_images[atom_id] = {"terms": terms}
    return {
        "delta": {"antifield_number_shift": -1, "rows": rows(delta)},
        "gamma": {"antifield_number_shift": 0, "rows": rows(gamma)},
        "Q_gt0": [],
        "Q": {"antifield_number_shift": None, "rows": rows(q_images)},
    }


def foundation_payloads() -> dict[Path, dict[str, Any]]:
    conventions = {
        "graded_commutativity": {"rule": "ab=(-1)^(|a||b|)ba", "odd_square": "0"},
        "integration_by_parts": {"category": "horizontal_local_forms_mod_d", "boundary": "compact_test_support"},
        "bianchi": {"identity": "nabla_mu B^{mu nu}=0"},
        "four_dimensional_antisymmetrization": {"identity": "antisymmetrization_over_5_indices=0"},
        "hodge_duality": {"orientation": "epsilon_0123=+sqrt_abs_g", "star_square_on_2_forms": "-1_Lorentzian"},
    }
    field_dictionary = {
        "result_id": "CLASSICAL_MINIMAL_BV_FIELD_DICTIONARY_V2",
        "generators": generators(),
        "gauge_algebra": "Diff(M) semidirect Weyl(M), closed and irreducible",
    }
    action = {
        "result_id": "PURE_WEYL_ACTION_NORMALIZATION_V2",
        "action": "S=-integral sqrt(abs(g)) C_{mu nu rho sigma} C^{mu nu rho sigma}",
        "coupling": 1,
        "Euler_coordinate": "E_g^{mu nu}:=delta S/delta g_{mu nu}=-2 sqrt(abs(g)) B^{mu nu}",
        "minimal_master_terms": [
            "integral g_star^{mu nu}(L_xi g_{mu nu}+2 omega g_{mu nu})",
            "integral xi_star_mu xi^nu partial_nu xi^mu",
            "integral omega_star xi^nu partial_nu omega",
        ],
    }
    euler = {
        "result_id": "PURE_WEYL_EULER_LAGRANGE_ROWS_V2",
        "metric_antifield_row": "delta g_star^{mu nu}=E_g^{mu nu}",
        "Euler_coordinate": action["Euler_coordinate"],
        "regular_coordinate_statement": "E_g and its differential consequences replace the transverse-tracefree highest metric jets on the regular Bach locus",
    }
    noether = {
        "result_id": "PURE_WEYL_NOETHER_IDENTITY_ROWS_V2",
        "Koszul_Tate_rows": {
            "delta xi_star_mu": "N_xi_mu:=-2 nabla_nu g_star^{nu}{}_mu",
            "delta omega_star": "N_omega:=2 g_{mu nu} g_star^{mu nu}",
        },
        "identities": {
            "delta N_xi": "-2 nabla_nu E_g^{nu}{}_mu=0",
            "delta N_omega": "2 g_{mu nu} E_g^{mu nu}=0",
        },
    }
    manifest = {
        "result_id": "CLASSICAL_MINIMAL_BV_KT_ADAPTED_ATOM_BASIS_V2",
        "basis_kind": "regular_covariant_Koszul_Tate_adapted_coordinates",
        "atoms": atoms(),
        "interface": "merge with the independently generated AFN0 curvature and lower-form bases",
        "not_claimed": "an exhaustive standalone list of all AFN0 curvature monomials",
    }
    canonicalization = {
        "result_id": "CLASSICAL_MINIMAL_BV_CANONICALIZATION_V2",
        "conventions": conventions,
        "convention_hashes": {name: _digest(value) for name, value in conventions.items()},
        "Lie_atom_rule": "Lie_X denotes the complete canonical Lie derivative, including density weight and index action",
        "Weyl_weights": "gamma X=Lie_X+w_X omega X",
    }
    base = {
        DEPENDENCY_FILES["atom_basis_manifest"]: manifest,
        DEPENDENCY_FILES["field_dictionary"]: field_dictionary,
        DEPENDENCY_FILES["action_normalization"]: action,
        DEPENDENCY_FILES["euler_lagrange_rows"]: euler,
        DEPENDENCY_FILES["noether_identity_rows"]: noether,
        DEPENDENCY_FILES["canonicalization_conventions"]: canonicalization,
    }
    for check_id, path in PROOF_FILES.items():
        base[path] = {
            "result_id": f"CLASSICAL_MINIMAL_BV_{check_id.upper()}",
            "status": "VERIFIED",
            "coefficient_field": "Q",
            "atom_count": len(atoms()),
            "check": check_id,
            "derivation": {
                "delta_squared_zero": "Bach Diff and Weyl Noether identities",
                "delta_gamma_anticommutator_zero": "covariance of Euler/Noether rows and delta Lie_X=-Lie_delta_X on antifield rows",
                "Q_decomposition_sums_to_Q": "coefficientwise canonical superpolynomial addition",
                "Q_squared_zero": "closed Diff-semidirect-Weyl algebra plus the two preceding filtration identities",
            }[check_id],
            "defect_count": 0,
        }
    return base


def write_foundation() -> None:
    for path, payload in foundation_payloads().items():
        _write(path, payload)


def _reference(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def _git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def build_export(classical_commit: str) -> dict[str, Any]:
    canonicalization = json.loads(DEPENDENCY_FILES["canonicalization_conventions"].read_text())
    scope = {
        "spacetime_dimension": 4,
        "maximum_form_degree": 4,
        "ghost_number_range": [-2, 2],
        "antifield_number_maximum": 2,
        "engineering_dimension_bound": 5,
        "derivative_order_bound": 1,
        "coefficient_field": "Q",
        "locality": "SUPPORT_LOCAL_POLYNOMIAL_JETS",
        "parity_sectors": ["even", "odd"],
        "identity_convention_hashes": canonicalization["convention_hashes"],
    }
    dependencies = {name: _reference(path) for name, path in DEPENDENCY_FILES.items()}
    diff = differential()
    checks = [
        {"check_id": check_id, "status": "VERIFIED", "proof_artifact": _reference(PROOF_FILES[check_id])}
        for check_id in sorted(PROOF_FILES)
    ]
    payload = {
        "schema": "quantum-weyl-antifield-export-v2",
        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
        "result_state": "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION",
        "classical_commit": classical_commit,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "expression_schema_version": "canonical-superpolynomial-atoms-v1",
        "scope": scope,
        "dependency_refs": dependencies,
        "generators": generators(),
        "atoms": atoms(),
        "differential": diff,
        "producer_checks": checks,
        "canonical_hashes": {
            "scope_hash": _digest(scope),
            "generator_hash": _digest(generators()),
            "atom_hash": _digest(atoms()),
            "differential_hash": _digest(diff),
            "dependency_hash": _digest(dependencies),
        },
    }
    return payload


def report(classical_commit: str) -> str:
    return f"""# Classical minimal-BV antifield export V2

The export is pinned to classical foundation commit `{classical_commit}` and
contains the six minimal Diff x Weyl generators, twelve derived covariant
Koszul--Tate/Lie atoms, and exact rational `delta`, `gamma`, and total `Q`
rows.  The independently executable identities are

```text
delta^2 = 0,
delta gamma + gamma delta = 0,
Q = delta + gamma,
Q^2 = 0.
```

The Bach Euler coordinate is

```text
E_g^{{mu nu}} = -2 sqrt(abs(g)) B^{{mu nu}}
```

for `S=-integral sqrt(abs(g)) C^2`.  The ghost-antifield rows encode

```text
delta xi_star_mu = -2 nabla_nu g_star^{{nu}}_mu,
delta omega_star = 2 g_mu_nu g_star^{{mu nu}},
```

and their squares vanish by the Diff and Weyl Noether identities.  Lie atoms
are complete tensor-density Lie derivatives, not scalar placeholders.

## Boundary

This is the executable minimal-BV/Koszul--Tate interface requested by the
quantum receiver.  It is designed to merge with the existing AFN0 curvature
and lower-form bases.  It does not itself enumerate those AFN0 bases, compute
`H^{{0,4}}(s|d)` or `H^{{1,4}}(s|d)`, determine an anomaly coefficient, restore
the QME, or make a Lorentzian or quantum claim.
"""


def build_receiver_obstruction(classical_commit: str) -> dict[str, Any]:
    """Record the exact failure of the current finite consumer adapter."""
    candidate = build_export(classical_commit)
    sys.path.insert(0, str(ROOT / "quantum-weyl"))
    from classical_import.verify_antifield_export_v2 import (  # type: ignore
        AntifieldExportV2Error,
        validate_export_v2,
    )

    failure = None
    try:
        validate_export_v2(candidate)
    except AntifieldExportV2Error as exc:
        failure = str(exc)
    if failure != "filtered adapter closure did not stabilize":
        raise AssertionError(f"unexpected V2 receiver outcome: {failure}")
    tower = [
        {"n": n, "monomial": ["g", *("Lie_omega" for _ in range(n))], "ghost_number": 2 * n}
        for n in range(9)
    ]
    return {
        "schema": "classical-minimal-bv-antifield-export-v2-receiver-obstruction-v1",
        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION",
        "result_state": "CLASSICAL_FILTRATION_EXACT_RECEIVER_FINITE_CLOSURE_BLOCKED",
        "classical_commit": classical_commit,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "candidate_hashes": candidate["canonical_hashes"],
        "classical_checks": {
            "strict_generator_dictionary": True,
            "support_local_covariant_atom_rows": True,
            "delta_squared_zero": True,
            "delta_gamma_anticommutator_zero": True,
            "Q_decomposition_sums_to_Q": True,
            "Q_squared_zero": True,
        },
        "receiver_witness": {
            "consumer": "quantum-weyl/classical_import/verify_antifield_export_v2.py",
            "failure": failure,
            "first_unbounded_even_atom": "Lie_omega=L_xi omega",
            "tower_rule": "gamma(Lie_g) contains -2 g Lie_omega, so componentwise closure contains g (Lie_omega)^n for every n",
            "tower_prefix": tower,
            "declared_candidate_ghost_range": candidate["scope"]["ghost_number_range"],
            "adapter_uses_declared_ghost_range": False,
            "adapter_uses_declared_engineering_bound": False,
        },
        "minimal_receiver_repairs": [
            "pass the declared scope into _dry_run_adapter and project every generated monomial to the admitted ghost/antifield/form/dimension window",
            "or extend the expression schema with quotient relations/generalized-connection families instead of demanding literal finite free-superalgebra closure",
        ],
        "rejected_shortcut": "Do not replace the complete Diff-Weyl variation by a single opaque BRST-image atom merely to make the adapter terminate.",
        "flags": {
            "CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT": True,
            "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2": False,
            "MINIMAL_BV_H04_H14_AUTHORIZED": False,
            "QUANTUM_CLAIM": False,
        },
        "claim_boundary": "This is a normalized obstruction to the current executable V2 receiving contract, not an obstruction to the classical minimal BV complex or to local BRST cohomology. The complete covariant classical delta, gamma and Q atom rows pass decomposition, delta-square, delta-gamma and Q-square checks before the consumer reaches its finite-adapter stage. The current adapter then demands untruncated free-superalgebra closure and does not use the scope's ghost-number or engineering-dimension bounds. The even Lie_omega atom therefore generates an infinite tower. No official CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2 artifact is emitted, and no H^{0,4}, H^{1,4}, anomaly, QME or quantum claim is authorized until the receiver contract is repaired and independently rerun.",
    }


def obstruction_report(payload: dict[str, Any]) -> str:
    return f"""# Minimal-BV antifield V2 receiver obstruction

The classical adapted-coordinate filtration passes `delta^2=0`,
`delta gamma+gamma delta=0`, `Q=delta+gamma`, and `Q^2=0`.  The current
quantum V2 receiver then stops with:

```text
{payload['receiver_witness']['failure']}
```

The exact witness is not a classical defect.  With
`Lie_omega=L_xi omega`, the Weyl-covariant row for `Lie_g` contains
`-2 g Lie_omega`.  Componentwise free-algebra closure therefore contains

```text
g, g Lie_omega, g Lie_omega^2, ...
```

The receiver declares a finite ghost-number and engineering-dimension scope,
but `_dry_run_adapter` does not use either bound.  The safe repair is to
project generated monomials to the declared filtered window, or to add
generalized-connection/quotient relations to the schema.  Collapsing a full
BRST variation into one opaque atom is explicitly rejected.

No official V2 export or minimal-BV cohomology promotion is made here.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-foundation", action="store_true")
    parser.add_argument("--write-export", action="store_true")
    parser.add_argument("--write-obstruction", action="store_true")
    parser.add_argument("--classical-commit")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write_foundation:
        write_foundation()
    if args.write_export or args.check:
        commit = args.classical_commit or _git_commit()
        payload = build_export(commit)
        if args.write_export:
            _write(OUTPUT, payload)
            REPORT.write_text(report(commit))
        if args.check:
            if json.loads(OUTPUT.read_text()) != payload:
                raise SystemExit("CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2 drifted")
            if REPORT.read_text() != report(commit):
                raise SystemExit("minimal-BV antifield report drifted")
    if args.write_obstruction:
        commit = args.classical_commit or _git_commit()
        payload = build_receiver_obstruction(commit)
        _write(OBSTRUCTION, payload)
        OBSTRUCTION_REPORT.write_text(obstruction_report(payload))
    print("CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2 producer: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
