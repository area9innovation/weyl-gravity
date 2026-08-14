#!/usr/bin/env python3
"""Executable v2 contract for a covariant minimal-BV antifield export.

Unlike the historical v1 metadata preflight, v2 admits no opaque expression
objects.  A finite, grading-bounded atom dictionary and exact sparse
supercommutative polynomials make ``delta``, ``gamma``, and ``Q`` executable
by the consumer.  The consumer reconstructs the total differential, replays
the filtration identities, and routes the resulting blocks through the
existing :mod:`local_bv.filtered_complex` API.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ci.standalone_provenance import (
    ProvenanceResolutionError,
    read_attached_blob,
)
from local_bv.filtered_complex import FilteredDegree, FilteredLocalComplex
from local_bv.relative_cohomology import SparseMatrix


SCHEMA_ID = "quantum-weyl-antifield-export-v2"
REQUIRED_ROLES = {
    "metric": (0, 0, 0, 0),
    "diffeomorphism_ghost": (1, 0, 0, 1),
    "weyl_ghost": (1, 0, 0, 1),
    "metric_antifield": (-1, 1, 4, 1),
    "diffeomorphism_ghost_antifield": (-2, 2, 4, 0),
    "weyl_ghost_antifield": (-2, 2, 4, 0),
}
DEPENDENCY_KEYS = {
    "atom_basis_manifest",
    "field_dictionary",
    "action_normalization",
    "euler_lagrange_rows",
    "noether_identity_rows",
    "canonicalization_conventions",
}
PRODUCER_CHECKS = {
    "delta_squared_zero",
    "delta_gamma_anticommutator_zero",
    "Q_decomposition_sums_to_Q",
    "Q_squared_zero",
}
HASH_KEYS = {
    "scope_hash",
    "generator_hash",
    "atom_hash",
    "differential_hash",
    "dependency_hash",
}
TOP_LEVEL_FIELDS = {
    "schema",
    "result_id",
    "result_state",
    "classical_commit",
    "dependency_tags",
    "expression_schema_version",
    "scope",
    "dependency_refs",
    "generators",
    "atoms",
    "differential",
    "producer_checks",
    "canonical_hashes",
}


class AntifieldExportV2Error(RuntimeError):
    """Raised when the executable antifield handoff fails closed."""


@dataclass(frozen=True)
class Grading:
    ghost: int
    antifield: int
    form: int
    parity: int
    dimension: Fraction
    weight: Fraction

    def product(self, other: "Grading") -> "Grading":
        return Grading(
            self.ghost + other.ghost,
            self.antifield + other.antifield,
            self.form + other.form,
            (self.parity + other.parity) % 2,
            self.dimension + other.dimension,
            self.weight + other.weight,
        )


Monomial = tuple[str, ...]
Polynomial = dict[Monomial, Fraction]


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _exact_payload(value: object, path: str = "$") -> None:
    if isinstance(value, float):
        raise AntifieldExportV2Error(f"floating-point value forbidden at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise AntifieldExportV2Error(f"non-string object key at {path}")
            _exact_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _exact_payload(child, f"{path}[{index}]")


def _fraction(value: object, label: str) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and type(value["numerator"]) is int
        and type(value["denominator"]) is int
        and value["denominator"] != 0
    ):
        return Fraction(value["numerator"], value["denominator"])
    raise AntifieldExportV2Error(f"{label} is not an exact rational")


def _grading(value: Mapping[str, Any]) -> Grading:
    return Grading(
        value["ghost_number"],
        value["antifield_number"],
        value["form_degree"],
        value["Grassmann_parity"],
        _fraction(value["mass_dimension"], "mass_dimension"),
        _fraction(value["Weyl_weight"], "Weyl_weight"),
    )


def _add(target: Polynomial, monomial: Monomial, coefficient: Fraction) -> None:
    if not coefficient:
        return
    total = target.get(monomial, Fraction()) + coefficient
    if total:
        target[monomial] = total
    else:
        target.pop(monomial, None)


def _canonical_product(
    factors: Iterable[str], atoms: Mapping[str, dict[str, Any]]
) -> tuple[Monomial | None, int]:
    ordered: list[str] = []
    sign = 1
    for factor in factors:
        if factor not in atoms:
            raise AntifieldExportV2Error(f"unknown expression atom: {factor}")
        parity = atoms[factor]["Grassmann_parity"]
        order = atoms[factor]["canonical_order"]
        position = len(ordered)
        while position and atoms[ordered[position - 1]]["canonical_order"] > order:
            if parity and atoms[ordered[position - 1]]["Grassmann_parity"]:
                sign *= -1
            position -= 1
        ordered.insert(position, factor)
    for left, right in zip(ordered, ordered[1:]):
        if left == right and atoms[left]["Grassmann_parity"] == 1:
            return None, 0
    return tuple(ordered), sign


def _poly_add(*values: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            _add(output, monomial, coefficient)
    return output


def _poly_scale(value: Polynomial, coefficient: Fraction) -> Polynomial:
    return {
        monomial: coefficient * scalar
        for monomial, scalar in value.items()
        if coefficient * scalar
    }


def _poly_multiply(
    left: Polynomial,
    right: Polynomial,
    atoms: Mapping[str, dict[str, Any]],
) -> Polynomial:
    output: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial, sign = _canonical_product(
                left_monomial + right_monomial, atoms
            )
            if monomial is not None:
                _add(
                    output,
                    monomial,
                    sign * left_coefficient * right_coefficient,
                )
    return output


def _parse_polynomial(
    value: object,
    atoms: Mapping[str, dict[str, Any]],
    *,
    label: str,
) -> Polynomial:
    if not isinstance(value, dict) or set(value) != {"terms"} or not isinstance(
        value["terms"], list
    ):
        raise AntifieldExportV2Error(f"{label} is not a canonical polynomial AST")
    output: Polynomial = {}
    previous: tuple[int, ...] | None = None
    for term in value["terms"]:
        if not isinstance(term, dict) or set(term) != {"coefficient", "factors"}:
            raise AntifieldExportV2Error(f"{label} contains a malformed term")
        coefficient = _fraction(term["coefficient"], f"{label} coefficient")
        factors = term["factors"]
        if not coefficient or not isinstance(factors, list) or any(
            not isinstance(factor, str) for factor in factors
        ):
            raise AntifieldExportV2Error(f"{label} retains a zero or malformed term")
        monomial, sign = _canonical_product(factors, atoms)
        if monomial is None:
            raise AntifieldExportV2Error(f"{label} retains a nilpotent odd square")
        if list(monomial) != factors or sign != 1:
            raise AntifieldExportV2Error(f"{label} factors are not in canonical super-order")
        signature = tuple(atoms[factor]["canonical_order"] for factor in monomial)
        if previous is not None and signature <= previous:
            raise AntifieldExportV2Error(f"{label} terms are not strictly ordered")
        previous = signature
        _add(output, monomial, coefficient)
    return output


def _monomial_grading(
    monomial: Monomial, atom_gradings: Mapping[str, Grading]
) -> Grading:
    value = Grading(0, 0, 0, 0, Fraction(), Fraction())
    for factor in monomial:
        value = value.product(atom_gradings[factor])
    return value


def _apply_component(
    polynomial: Polynomial,
    rows: Mapping[str, Polynomial],
    atoms: Mapping[str, dict[str, Any]],
) -> Polynomial:
    output: Polynomial = {}
    for monomial, coefficient in polynomial.items():
        preceding_parity = 0
        for index, factor in enumerate(monomial):
            image = rows[factor]
            if image:
                left = {monomial[:index]: Fraction(1)}
                right = {monomial[index + 1 :]: Fraction(1)}
                term = _poly_multiply(
                    _poly_multiply(left, image, atoms), right, atoms
                )
                _add_sign = -1 if preceding_parity else 1
                output = _poly_add(
                    output, _poly_scale(term, coefficient * _add_sign)
                )
            preceding_parity ^= atoms[factor]["Grassmann_parity"]
    return output


def _verify_pinned(
    repository_root: Path,
    classical_commit: str,
    reference: Mapping[str, Any],
) -> None:
    relative = reference["path"]
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise AntifieldExportV2Error(f"unsafe pinned path: {relative}")
    root = repository_root.resolve()
    working = (root / path).resolve()
    try:
        working.relative_to(root)
        data = working.read_bytes()
    except (ValueError, OSError) as exc:
        raise AntifieldExportV2Error(f"missing pinned artifact: {relative}") from exc
    if hashlib.sha256(data).hexdigest() != reference["sha256"]:
        raise AntifieldExportV2Error(f"working-tree artifact hash mismatch: {relative}")
    try:
        _, committed = read_attached_blob(
            classical_commit,
            relative,
            reference["sha256"],
            root=root,
        )
    except ProvenanceResolutionError as exc:
        raise AntifieldExportV2Error(
            f"artifact absent at classical commit: {relative}: {exc}"
        ) from exc
    if hashlib.sha256(committed).hexdigest() != reference["sha256"]:
        raise AntifieldExportV2Error(f"classical-commit artifact hash mismatch: {relative}")


def _reference(value: object, label: str) -> dict[str, str]:
    if (
        not isinstance(value, dict)
        or set(value) != {"path", "sha256"}
        or not isinstance(value["path"], str)
        or not value["path"]
        or Path(value["path"]).is_absolute()
        or ".." in Path(value["path"]).parts
        or not isinstance(value["sha256"], str)
        or len(value["sha256"]) != 64
        or any(character not in "0123456789abcdef" for character in value["sha256"])
    ):
        raise AntifieldExportV2Error(f"{label} is not a safe content-addressed reference")
    return value


def _component_rows(
    component: object,
    *,
    expected_shift: int | None,
    atoms: Mapping[str, dict[str, Any]],
    atom_gradings: Mapping[str, Grading],
    label: str,
) -> tuple[int | None, dict[str, Polynomial]]:
    if not isinstance(component, dict) or set(component) != {"antifield_number_shift", "rows"}:
        raise AntifieldExportV2Error(f"{label} component fields drifted")
    shift = component["antifield_number_shift"]
    if expected_shift is not None and shift != expected_shift:
        raise AntifieldExportV2Error(f"{label} has the wrong antifield-number shift")
    if expected_shift is None and shift is not None:
        raise AntifieldExportV2Error("total Q must declare a mixed antifield shift as null")
    rows = component["rows"]
    if not isinstance(rows, list) or [row.get("source_atom") for row in rows if isinstance(row, dict)] != list(atoms):
        raise AntifieldExportV2Error(f"{label} rows do not exactly cover ordered atoms")
    parsed: dict[str, Polynomial] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"source_atom", "image"}:
            raise AntifieldExportV2Error(f"{label} contains a malformed row")
        source = row["source_atom"]
        image = _parse_polynomial(row["image"], atoms, label=f"{label}[{source}]")
        source_grading = atom_gradings[source]
        for monomial in image:
            target = _monomial_grading(monomial, atom_gradings)
            if (
                target.ghost != source_grading.ghost + 1
                or target.form != source_grading.form
                or target.parity != 1 - source_grading.parity
                or target.dimension != source_grading.dimension
                or target.weight != source_grading.weight
                or (shift is not None and target.antifield != source_grading.antifield + shift)
            ):
                raise AntifieldExportV2Error(f"{label}[{source}] violates exact grading")
        parsed[source] = image
    return shift, parsed


def _dry_run_adapter(
    atoms: Mapping[str, dict[str, Any]],
    atom_gradings: Mapping[str, Grading],
    components: Mapping[int, Mapping[str, Polynomial]],
    scope: Mapping[str, Any],
) -> dict[str, Any]:
    ghost_min, ghost_max = scope["ghost_number_range"]
    dimension_bound = _fraction(
        scope["engineering_dimension_bound"], "engineering_dimension_bound"
    )

    def admitted(monomial: Monomial) -> bool:
        grading = _monomial_grading(monomial, atom_gradings)
        derivative_order = sum(
            atoms[factor]["covariant_derivative_order"] for factor in monomial
        )
        return (
            ghost_min <= grading.ghost <= ghost_max
            and 0 <= grading.antifield <= scope["antifield_number_maximum"]
            and 0 <= grading.form <= scope["maximum_form_degree"]
            and grading.dimension <= dimension_bound
            and derivative_order <= scope["derivative_order_bound"]
        )

    monomials: set[Monomial] = {(atom,) for atom in atoms}
    for rows in components.values():
        for image in rows.values():
            monomials.update(monomial for monomial in image if admitted(monomial))
    projected: set[Monomial] = set()
    for _ in range(16):
        added: set[Monomial] = set()
        for monomial in monomials:
            polynomial = {monomial: Fraction(1)}
            for rows in components.values():
                for target in _apply_component(polynomial, rows, atoms):
                    if admitted(target):
                        added.add(target)
                    else:
                        projected.add(target)
        if added <= monomials:
            break
        monomials.update(added)
        if len(monomials) > 4096:
            raise AntifieldExportV2Error("filtered adapter closure exceeded 4096 monomials")
    else:
        raise AntifieldExportV2Error("filtered adapter closure did not stabilize")

    by_degree: dict[FilteredDegree, list[Monomial]] = defaultdict(list)
    for monomial in sorted(
        monomials,
        key=lambda item: tuple(atoms[factor]["canonical_order"] for factor in item),
    ):
        grading = _monomial_grading(monomial, atom_gradings)
        by_degree[FilteredDegree(grading.antifield, grading.ghost, grading.form)].append(monomial)
    spaces = {
        degree: tuple("*".join(monomial) or "1" for monomial in basis)
        for degree, basis in by_degree.items()
    }
    q_blocks: dict[tuple[FilteredDegree, int], SparseMatrix] = {}
    for source_degree, source_basis in by_degree.items():
        for shift, rows in components.items():
            target_afn = source_degree.antifield_number + shift
            if target_afn < 0:
                continue
            target_degree = FilteredDegree(
                target_afn, source_degree.ghost_number + 1, source_degree.form_degree
            )
            target_basis = by_degree.get(target_degree, [])
            target_index = {monomial: index for index, monomial in enumerate(target_basis)}
            entries: dict[tuple[int, int], Fraction] = {}
            for column, monomial in enumerate(source_basis):
                image = _apply_component({monomial: Fraction(1)}, rows, atoms)
                for target, coefficient in image.items():
                    if not admitted(target):
                        projected.add(target)
                        continue
                    if target not in target_index:
                        raise AntifieldExportV2Error("filtered adapter target escaped closure")
                    entries[(target_index[target], column)] = coefficient
            q_blocks[(source_degree, shift)] = SparseMatrix(
                len(target_basis), len(source_basis), entries
            )
    complex_ = FilteredLocalComplex(spaces, q_blocks, {})
    checks = complex_.verify_filtered_identities()
    afn0 = complex_.afn0_view().verify_bicomplex()
    manifest = complex_.block_manifest()
    return {
        "status": "FILTERED_LOCAL_COMPLEX_DRY_RUN_VERIFIED",
        "monomial_count": len(monomials),
        "filtered_space_count": len(spaces),
        "afn0_space_count": sum(
            bool(labels) for degree, labels in spaces.items() if degree.antifield_number == 0
        ),
        "scope_projection": {
            "status": "DECLARED_GRADED_WINDOW_ENFORCED",
            "ghost_number_range": list(scope["ghost_number_range"]),
            "antifield_number_maximum": scope["antifield_number_maximum"],
            "maximum_form_degree": scope["maximum_form_degree"],
            "engineering_dimension_bound": scope["engineering_dimension_bound"],
            "derivative_order_bound": scope["derivative_order_bound"],
            "projected_monomial_count": len(projected),
            "projected_manifest_sha256": _digest(
                sorted(
                    (list(monomial) for monomial in projected),
                    key=lambda factors: tuple(
                        atoms[factor]["canonical_order"] for factor in factors
                    ),
                )
            ),
        },
        "checks": {**checks, **afn0},
        "block_manifest_sha256": _digest(manifest),
    }


def validate_export_v2(
    payload: dict[str, Any],
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Validate and independently execute a v2 classical antifield export."""

    _exact_payload(payload)
    if set(payload) != TOP_LEVEL_FIELDS:
        raise AntifieldExportV2Error("v2 export has the wrong top-level field set")
    if (
        payload["schema"] != SCHEMA_ID
        or payload["result_id"] != "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2"
        or payload["result_state"] != "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
        or payload["expression_schema_version"] != "canonical-superpolynomial-atoms-v1"
    ):
        raise AntifieldExportV2Error("v2 export identity or scope drifted")
    commit = payload["classical_commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise AntifieldExportV2Error("classical_commit must be a full lowercase Git id")

    scope = payload["scope"]
    required_scope = {
        "spacetime_dimension",
        "maximum_form_degree",
        "ghost_number_range",
        "antifield_number_maximum",
        "engineering_dimension_bound",
        "derivative_order_bound",
        "coefficient_field",
        "locality",
        "parity_sectors",
        "identity_convention_hashes",
    }
    if not isinstance(scope, dict) or set(scope) != required_scope:
        raise AntifieldExportV2Error("v2 scope is incomplete")
    dimension_bound = _fraction(
        scope["engineering_dimension_bound"], "engineering_dimension_bound"
    )
    ghost_min, ghost_max = scope["ghost_number_range"]
    if (
        scope["spacetime_dimension"] != 4
        or scope["maximum_form_degree"] != 4
        or scope["coefficient_field"] != "Q"
        or scope["locality"] != "SUPPORT_LOCAL_POLYNOMIAL_JETS"
        or scope["parity_sectors"] != ["even", "odd"]
        or not isinstance(scope["ghost_number_range"], list)
        or len(scope["ghost_number_range"]) != 2
        or any(type(value) is not int for value in scope["ghost_number_range"])
        or type(scope["antifield_number_maximum"]) is not int
        or type(scope["derivative_order_bound"]) is not int
        or ghost_min > ghost_max
        or scope["antifield_number_maximum"] < 2
        or scope["derivative_order_bound"] < 0
        or dimension_bound < 0
    ):
        raise AntifieldExportV2Error("v2 declared bounds or locality drifted")
    conventions = scope["identity_convention_hashes"]
    if not isinstance(conventions, dict) or set(conventions) != {
        "graded_commutativity",
        "integration_by_parts",
        "bianchi",
        "four_dimensional_antisymmetrization",
        "hodge_duality",
    }:
        raise AntifieldExportV2Error("identity convention hash inventory drifted")
    for name, digest in conventions.items():
        _reference({"path": name, "sha256": digest}, f"{name} convention")

    references = payload["dependency_refs"]
    if not isinstance(references, dict) or set(references) != DEPENDENCY_KEYS:
        raise AntifieldExportV2Error("v2 dependency inventory drifted")
    references = {name: _reference(value, name) for name, value in references.items()}

    generators = payload["generators"]
    generator_fields = {
        "symbol",
        "role",
        "sector",
        "tensor_type",
        "ghost_number",
        "antifield_number",
        "form_degree",
        "Grassmann_parity",
        "mass_dimension",
        "Weyl_weight",
    }
    if not isinstance(generators, list) or len(generators) < 6:
        raise AntifieldExportV2Error("complete minimal generator dictionary is absent")
    by_symbol: dict[str, dict[str, Any]] = {}
    by_role: dict[str, dict[str, Any]] = {}
    for generator in generators:
        if not isinstance(generator, dict) or set(generator) != generator_fields:
            raise AntifieldExportV2Error("generator field set drifted")
        symbol, role = generator["symbol"], generator["role"]
        if not isinstance(symbol, str) or not symbol or symbol in by_symbol:
            raise AntifieldExportV2Error("generator symbols are not unique")
        if role not in {*REQUIRED_ROLES, "other_minimal", "nonminimal", "auxiliary"}:
            raise AntifieldExportV2Error(f"unknown generator role: {role}")
        if role in REQUIRED_ROLES and role in by_role:
            raise AntifieldExportV2Error(f"duplicate required role: {role}")
        if generator["sector"] not in {"minimal", "nonminimal", "auxiliary"}:
            raise AntifieldExportV2Error(f"{symbol}: invalid sector")
        tensor = generator["tensor_type"]
        if not isinstance(tensor, dict) or set(tensor) != {
            "covariant_rank",
            "contravariant_rank",
            "symmetry",
        }:
            raise AntifieldExportV2Error(f"{symbol}: strict tensor type absent")
        grading = _grading(generator)
        if (
            not ghost_min <= grading.ghost <= ghost_max
            or not 0 <= grading.antifield <= scope["antifield_number_maximum"]
            or not 0 <= grading.form <= scope["maximum_form_degree"]
            or grading.parity not in {0, 1}
            or grading.dimension > dimension_bound
        ):
            raise AntifieldExportV2Error(f"{symbol}: invalid grading")
        by_symbol[symbol] = generator
        if role in REQUIRED_ROLES:
            by_role[role] = generator
    if set(by_role) != set(REQUIRED_ROLES):
        raise AntifieldExportV2Error("minimal field/ghost/antifield roles are incomplete")
    for role, expected in REQUIRED_ROLES.items():
        generator = by_role[role]
        observed = (
            generator["ghost_number"],
            generator["antifield_number"],
            generator["form_degree"],
            generator["Grassmann_parity"],
        )
        if generator["sector"] != "minimal" or observed != expected:
            raise AntifieldExportV2Error(f"{role}: canonical minimal grading drifted")

    raw_atoms = payload["atoms"]
    atom_fields = {
        "atom_id",
        "origin",
        "tensor_signature",
        "covariant_derivative_order",
        "ghost_number",
        "antifield_number",
        "form_degree",
        "Grassmann_parity",
        "mass_dimension",
        "Weyl_weight",
        "canonical_order",
    }
    if not isinstance(raw_atoms, list) or not raw_atoms:
        raise AntifieldExportV2Error("v2 atom dictionary is empty")
    atoms: dict[str, dict[str, Any]] = {}
    atom_gradings: dict[str, Grading] = {}
    generator_origins: set[str] = set()
    for expected_order, atom in enumerate(raw_atoms):
        if not isinstance(atom, dict) or set(atom) != atom_fields:
            raise AntifieldExportV2Error("atom field set drifted")
        atom_id = atom["atom_id"]
        if not isinstance(atom_id, str) or not atom_id or atom_id in atoms:
            raise AntifieldExportV2Error("atom ids are not unique")
        if atom["canonical_order"] != expected_order:
            raise AntifieldExportV2Error("atom canonical order is not contiguous")
        origin = atom["origin"]
        if not isinstance(origin, dict) or set(origin) != {"kind", "id"} or origin["kind"] not in {"generator", "derived"} or not isinstance(origin["id"], str) or not origin["id"]:
            raise AntifieldExportV2Error(f"{atom_id}: malformed atom origin")
        if origin["kind"] == "generator":
            if origin["id"] not in by_symbol:
                raise AntifieldExportV2Error(f"{atom_id}: unknown generator origin")
            generator_origins.add(origin["id"])
            if _grading(atom) != _grading(by_symbol[origin["id"]]):
                raise AntifieldExportV2Error(f"{atom_id}: generator atom grading drifted")
        tensor = atom["tensor_signature"]
        if not isinstance(tensor, dict) or set(tensor) != {
            "covariant_rank",
            "contravariant_rank",
            "symmetry",
            "spacetime_parity",
        }:
            raise AntifieldExportV2Error(f"{atom_id}: strict tensor signature absent")
        if type(atom["covariant_derivative_order"]) is not int or not 0 <= atom["covariant_derivative_order"] <= scope["derivative_order_bound"]:
            raise AntifieldExportV2Error(f"{atom_id}: derivative order escaped scope")
        grading = _grading(atom)
        if (
            not ghost_min <= grading.ghost <= ghost_max
            or not 0 <= grading.antifield <= scope["antifield_number_maximum"]
            or not 0 <= grading.form <= scope["maximum_form_degree"]
            or grading.parity not in {0, 1}
            or grading.dimension > dimension_bound
        ):
            raise AntifieldExportV2Error(f"{atom_id}: invalid atom grading")
        atoms[atom_id] = atom
        atom_gradings[atom_id] = grading
    if generator_origins != set(by_symbol):
        raise AntifieldExportV2Error("not every declared generator has a canonical atom")

    differential = payload["differential"]
    if not isinstance(differential, dict) or set(differential) != {"delta", "gamma", "Q_gt0", "Q"}:
        raise AntifieldExportV2Error("v2 differential component inventory drifted")
    _, delta = _component_rows(
        differential["delta"], expected_shift=-1, atoms=atoms,
        atom_gradings=atom_gradings, label="delta"
    )
    _, gamma = _component_rows(
        differential["gamma"], expected_shift=0, atoms=atoms,
        atom_gradings=atom_gradings, label="gamma"
    )
    _, total_q = _component_rows(
        differential["Q"], expected_shift=None, atoms=atoms,
        atom_gradings=atom_gradings, label="Q"
    )
    higher: dict[int, dict[str, Polynomial]] = {}
    if not isinstance(differential["Q_gt0"], list):
        raise AntifieldExportV2Error("Q_gt0 must be an ordered component list")
    previous_shift = 0
    for component in differential["Q_gt0"]:
        shift = component.get("antifield_number_shift") if isinstance(component, dict) else None
        if type(shift) is not int or shift <= previous_shift:
            raise AntifieldExportV2Error("Q_gt0 shifts are not strictly positive and ordered")
        _, rows = _component_rows(
            component, expected_shift=shift, atoms=atoms,
            atom_gradings=atom_gradings, label=f"Q_gt0[{shift}]"
        )
        higher[shift] = rows
        previous_shift = shift

    all_components: dict[int, dict[str, Polynomial]] = {-1: delta, 0: gamma, **higher}
    reconstructed: dict[str, Polynomial] = {}
    for atom in atoms:
        reconstructed[atom] = _poly_add(
            delta[atom], gamma[atom], *(rows[atom] for rows in higher.values())
        )
        if reconstructed[atom] != total_q[atom]:
            raise AntifieldExportV2Error(f"Q decomposition does not reconstruct on {atom}")

    for atom in atoms:
        delta_square = _apply_component(delta[atom], delta, atoms)
        if delta_square:
            raise AntifieldExportV2Error(f"delta^2 is nonzero on {atom}")
        anticommutator = _poly_add(
            _apply_component(gamma[atom], delta, atoms),
            _apply_component(delta[atom], gamma, atoms),
        )
        if anticommutator:
            raise AntifieldExportV2Error(f"delta-gamma anticommutator is nonzero on {atom}")
        if _apply_component(total_q[atom], total_q, atoms):
            raise AntifieldExportV2Error(f"Q^2 is nonzero on {atom}")

    checks = payload["producer_checks"]
    if not isinstance(checks, list) or [check.get("check_id") for check in checks if isinstance(check, dict)] != sorted(PRODUCER_CHECKS):
        raise AntifieldExportV2Error("producer check inventory drifted")
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"check_id", "status", "proof_artifact"} or check["status"] != "VERIFIED":
            raise AntifieldExportV2Error("producer check row is malformed or unverified")
        _reference(check["proof_artifact"], check["check_id"])

    expected_hashes = {
        "scope_hash": _digest(scope),
        "generator_hash": _digest(generators),
        "atom_hash": _digest(raw_atoms),
        "differential_hash": _digest(differential),
        "dependency_hash": _digest(references),
    }
    if payload["canonical_hashes"] != expected_hashes:
        raise AntifieldExportV2Error("v2 canonical hashes do not reproduce")

    if repository_root is not None:
        for reference in references.values():
            _verify_pinned(repository_root, commit, reference)
        for check in checks:
            _verify_pinned(repository_root, commit, check["proof_artifact"])

    adapter = _dry_run_adapter(atoms, atom_gradings, all_components, scope)
    return {
        "status": "EXECUTABLE_V2_EXPORT_INDEPENDENTLY_REPLAYED",
        "classical_commit": commit,
        "generator_count": len(generators),
        "atom_count": len(atoms),
        "component_shifts": sorted(all_components),
        "independent_checks": {
            "Q_decomposition_sums_to_Q": "VERIFIED",
            "delta_squared_zero": "VERIFIED",
            "delta_gamma_anticommutator_zero": "VERIFIED",
            "Q_squared_zero": "VERIFIED",
        },
        "producer_proofs_used_as_authority": False,
        "proof_artifact_integrity": "VERIFIED" if repository_root is not None else "NOT_CHECKED",
        "filtered_complex_adapter": adapter,
        "canonical_hashes": expected_hashes,
    }


def _polynomial(terms: Iterable[tuple[int, Iterable[str]]]) -> dict[str, Any]:
    return {
        "terms": [
            {"coefficient": coefficient, "factors": list(factors)}
            for coefficient, factors in terms
        ]
    }


def synthetic_fixture() -> dict[str, Any]:
    """Return a nontrivial six-generator fixture for contract regression."""

    generator_rows = (
        ("g", "metric", 0, 0, 0, 0),
        ("xi", "diffeomorphism_ghost", 1, 0, 0, 1),
        ("omega", "weyl_ghost", 1, 0, 0, 1),
        ("g_star", "metric_antifield", -1, 1, 4, 1),
        ("xi_star", "diffeomorphism_ghost_antifield", -2, 2, 4, 0),
        ("omega_star", "weyl_ghost_antifield", -2, 2, 4, 0),
    )
    generators = [
        {
            "symbol": symbol,
            "role": role,
            "sector": "minimal",
            "tensor_type": {
                "covariant_rank": 0,
                "contravariant_rank": 0,
                "symmetry": "fixture_scalarized",
            },
            "ghost_number": ghost,
            "antifield_number": antifield,
            "form_degree": form,
            "Grassmann_parity": parity,
            "mass_dimension": 0,
            "Weyl_weight": 0,
        }
        for symbol, role, ghost, antifield, form, parity in generator_rows
    ]
    derived = (
        ("E_g", "metric_Euler_row", 0, 0, 4, 0),
        ("N_xi", "diffeomorphism_Noether_row", -1, 1, 4, 1),
        ("N_omega", "Weyl_Noether_row", -1, 1, 4, 1),
    )
    atoms = []
    for order, (symbol, _role, ghost, antifield, form, parity) in enumerate(generator_rows):
        atoms.append(
            {
                "atom_id": symbol,
                "origin": {"kind": "generator", "id": symbol},
                "tensor_signature": {
                    "covariant_rank": 0,
                    "contravariant_rank": 0,
                    "symmetry": "fixture_scalarized",
                    "spacetime_parity": "even",
                },
                "covariant_derivative_order": 0,
                "ghost_number": ghost,
                "antifield_number": antifield,
                "form_degree": form,
                "Grassmann_parity": parity,
                "mass_dimension": 0,
                "Weyl_weight": 0,
                "canonical_order": order,
            }
        )
    for offset, (atom_id, row_id, ghost, antifield, form, parity) in enumerate(derived, len(atoms)):
        atoms.append(
            {
                "atom_id": atom_id,
                "origin": {"kind": "derived", "id": row_id},
                "tensor_signature": {
                    "covariant_rank": 0,
                    "contravariant_rank": 0,
                    "symmetry": "fixture_scalarized",
                    "spacetime_parity": "even",
                },
                "covariant_derivative_order": 0,
                "ghost_number": ghost,
                "antifield_number": antifield,
                "form_degree": form,
                "Grassmann_parity": parity,
                "mass_dimension": 0,
                "Weyl_weight": 0,
                "canonical_order": offset,
            }
        )
    atom_ids = [atom["atom_id"] for atom in atoms]
    zero = _polynomial(())
    delta_images = {
        "g_star": _polynomial(((1, ("E_g",)),)),
        "xi_star": _polynomial(((1, ("N_xi",)),)),
        "omega_star": _polynomial(((1, ("N_omega",)),)),
    }
    gamma_images = {
        "g": _polynomial(((1, ("g", "omega")),)),
        "g_star": _polynomial(((1, ("omega", "g_star")),)),
        "xi_star": _polynomial(((1, ("omega", "xi_star")),)),
        "omega_star": _polynomial(((1, ("omega", "omega_star")),)),
        "E_g": _polynomial(((1, ("omega", "E_g")),)),
        "N_xi": _polynomial(((1, ("omega", "N_xi")),)),
        "N_omega": _polynomial(((1, ("omega", "N_omega")),)),
    }

    def clone_polynomial(value: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "terms": [
                {
                    "coefficient": term["coefficient"],
                    "factors": list(term["factors"]),
                }
                for term in value["terms"]
            ]
        }

    def rows(images: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"source_atom": atom, "image": clone_polynomial(images.get(atom, zero))}
            for atom in atom_ids
        ]

    q_images: dict[str, dict[str, Any]] = {}
    for atom in atom_ids:
        terms = []
        for image in (delta_images.get(atom, zero), gamma_images.get(atom, zero)):
            terms.extend(clone_polynomial(image)["terms"])
        terms.sort(key=lambda term: tuple(atom_ids.index(factor) for factor in term["factors"]))
        q_images[atom] = {"terms": terms}
    references = {
        name: {"path": f"proof/{name}.json", "sha256": "0" * 64}
        for name in sorted(DEPENDENCY_KEYS)
    }
    scope = {
        "spacetime_dimension": 4,
        "maximum_form_degree": 4,
        "ghost_number_range": [-2, 1],
        "antifield_number_maximum": 2,
        "engineering_dimension_bound": 4,
        "derivative_order_bound": 4,
        "coefficient_field": "Q",
        "locality": "SUPPORT_LOCAL_POLYNOMIAL_JETS",
        "parity_sectors": ["even", "odd"],
        "identity_convention_hashes": {
            name: "0" * 64
            for name in (
                "graded_commutativity",
                "integration_by_parts",
                "bianchi",
                "four_dimensional_antisymmetrization",
                "hodge_duality",
            )
        },
    }
    differential = {
        "delta": {"antifield_number_shift": -1, "rows": rows(delta_images)},
        "gamma": {"antifield_number_shift": 0, "rows": rows(gamma_images)},
        "Q_gt0": [],
        "Q": {"antifield_number_shift": None, "rows": rows(q_images)},
    }
    checks = [
        {
            "check_id": check_id,
            "status": "VERIFIED",
            "proof_artifact": {
                "path": f"proof/{check_id}.json",
                "sha256": "0" * 64,
            },
        }
        for check_id in sorted(PRODUCER_CHECKS)
    ]
    return {
        "schema": SCHEMA_ID,
        "result_id": "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
        "result_state": "EXPORTED_EXECUTABLE_MINIMAL_BV_FILTRATION",
        "classical_commit": "0" * 40,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "expression_schema_version": "canonical-superpolynomial-atoms-v1",
        "scope": scope,
        "dependency_refs": references,
        "generators": generators,
        "atoms": atoms,
        "differential": differential,
        "producer_checks": checks,
        "canonical_hashes": {
            "scope_hash": _digest(scope),
            "generator_hash": _digest(generators),
            "atom_hash": _digest(atoms),
            "differential_hash": _digest(differential),
            "dependency_hash": _digest(references),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--repository-root", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.export.read_text())
        result = validate_export_v2(payload, repository_root=args.repository_root)
    except (OSError, json.JSONDecodeError, AntifieldExportV2Error) as exc:
        print(f"ANTIFIELD_EXPORT_V2_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
