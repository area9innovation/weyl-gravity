"""Exact Koszul--Tate collapse for the imported minimal-BV atom algebra.

The classical export uses regular adapted coordinates.  Its six nonzero
Koszul--Tate rows form covariant contractible pairs.  This module constructs
the conjugate odd derivation, verifies the Euler identity on generators and
representative supermonomials, and records the resulting antifield spectral
sequence collapse.  It deliberately does not fill the still-open pure-Diff
or mixed AFN0 total-complex basis.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations_with_replacement
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPORT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
IMPORT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
H04 = HERE / "certificates/AFN0_H04_CANONICAL_QUOTIENT.json"
H14_EVEN = HERE / "certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json"
H14_ODD = HERE / "certificates/AFN0_H14_ODD_CANONICAL_QUOTIENT.json"


Monomial = tuple[str, ...]
Polynomial = dict[Monomial, Fraction]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: object) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError("coefficient is not exact rational data")


def _canonical_product(
    factors: Iterable[str], atoms: Mapping[str, Mapping[str, Any]]
) -> tuple[Monomial | None, int]:
    ordered: list[str] = []
    sign = 1
    for factor in factors:
        parity = atoms[factor]["Grassmann_parity"]
        order = atoms[factor]["canonical_order"]
        position = len(ordered)
        while position and atoms[ordered[position - 1]]["canonical_order"] > order:
            if parity and atoms[ordered[position - 1]]["Grassmann_parity"]:
                sign *= -1
            position -= 1
        ordered.insert(position, factor)
    if any(
        left == right and atoms[left]["Grassmann_parity"] == 1
        for left, right in zip(ordered, ordered[1:])
    ):
        return None, 0
    return tuple(ordered), sign


def _add(output: Polynomial, monomial: Monomial, coefficient: Fraction) -> None:
    total = output.get(monomial, Fraction()) + coefficient
    if total:
        output[monomial] = total
    else:
        output.pop(monomial, None)


def _derivation(
    polynomial: Polynomial,
    rows: Mapping[str, Polynomial],
    atoms: Mapping[str, Mapping[str, Any]],
) -> Polynomial:
    output: Polynomial = {}
    for monomial, coefficient in polynomial.items():
        preceding_parity = 0
        for index, factor in enumerate(monomial):
            for image, image_coefficient in rows[factor].items():
                target, reorder_sign = _canonical_product(
                    monomial[:index] + image + monomial[index + 1 :], atoms
                )
                if target is not None:
                    sign = -1 if preceding_parity else 1
                    _add(
                        output,
                        target,
                        coefficient * image_coefficient * sign * reorder_sign,
                    )
            preceding_parity ^= atoms[factor]["Grassmann_parity"]
    return output


def _poly_add(*polynomials: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for polynomial in polynomials:
        for monomial, coefficient in polynomial.items():
            _add(output, monomial, coefficient)
    return output


def _poly_scale(polynomial: Polynomial, coefficient: Fraction) -> Polynomial:
    return {
        monomial: coefficient * value
        for monomial, value in polynomial.items()
        if coefficient * value
    }


def _parse_rows(
    component: Mapping[str, Any], atoms: Mapping[str, Mapping[str, Any]]
) -> dict[str, Polynomial]:
    rows: dict[str, Polynomial] = {}
    for row in component["rows"]:
        polynomial: Polynomial = {}
        for term in row["image"]["terms"]:
            monomial, sign = _canonical_product(term["factors"], atoms)
            if monomial is None:
                raise ValueError("delta row contains an odd square")
            _add(polynomial, monomial, sign * _fraction(term["coefficient"]))
        rows[row["source_atom"]] = polynomial
    if set(rows) != set(atoms):
        raise ValueError("delta rows do not cover the imported atom dictionary")
    return rows


def _single_atom_image(polynomial: Polynomial, source: str) -> tuple[Fraction, str]:
    if len(polynomial) != 1:
        raise ValueError(f"{source}: Koszul--Tate row is not a single adapted coordinate")
    (monomial, coefficient), = polynomial.items()
    if len(monomial) != 1:
        raise ValueError(f"{source}: Koszul--Tate target is not an atom")
    return coefficient, monomial[0]


def _homotopy(
    polynomial: Polynomial,
    sigma_rows: Mapping[str, Polynomial],
    atoms: Mapping[str, Mapping[str, Any]],
    pair_atoms: set[str],
) -> Polynomial:
    output: Polynomial = {}
    for monomial, coefficient in polynomial.items():
        pair_degree = sum(factor in pair_atoms for factor in monomial)
        if pair_degree:
            image = _derivation({monomial: coefficient}, sigma_rows, atoms)
            output = _poly_add(output, _poly_scale(image, Fraction(1, pair_degree)))
    return output


def _regression_monomials(
    atoms: Mapping[str, Mapping[str, Any]], pair_atoms: tuple[str, ...]
) -> tuple[Monomial, ...]:
    pair_monomials: set[Monomial] = set()
    for degree in range(1, 5):
        for factors in combinations_with_replacement(pair_atoms, degree):
            monomial, sign = _canonical_product(factors, atoms)
            if monomial is not None and sign:
                pair_monomials.add(monomial)
    base_atoms = tuple(atom for atom in atoms if atom not in pair_atoms)
    regressions = set(pair_monomials)
    for base in base_atoms:
        for pair_monomial in pair_monomials:
            monomial, sign = _canonical_product((base, *pair_monomial), atoms)
            if monomial is not None and sign:
                regressions.add(monomial)
    return tuple(
        sorted(
            regressions,
            key=lambda monomial: tuple(atoms[factor]["canonical_order"] for factor in monomial),
        )
    )


def _classes(h04: dict[str, Any], even: dict[str, Any], odd: dict[str, Any]) -> dict[str, Any]:
    h04_classes = [*h04["even_sector"]["classes"], *h04["odd_sector"]["classes"]]
    h14_classes = [*even["classes"], *odd["classes"]]
    return {
        "H04_covariant_candidate_classes": [
            {
                "representative_id": row["representative_id"],
                "AFN0_status": row["relative_cohomology_status"],
                "minimal_KT_lift_status": "LIFTS_UNCHANGED_ON_REGULAR_BACH_LOCUS",
            }
            for row in h04_classes
        ],
        "H14_Weyl_ghost_candidate_classes": [
            {
                "representative_id": row["representative_id"],
                "AFN0_status": row["relative_cohomology_status"],
                "minimal_KT_lift_status": "LIFTS_UNCHANGED_ON_REGULAR_BACH_LOCUS",
            }
            for row in h14_classes
        ],
        "exact_rows": [
            {
                "representative_id": row["representative_id"],
                "AFN0_status": row["relative_cohomology_status"],
                "minimal_KT_lift_status": "REMAINS_D_H_EXACT",
            }
            for row in h04["even_sector"]["exact_classes"]
        ] + [
            {
                "representative_id": row["representative_id"],
                "AFN0_status": row["relative_cohomology_status"],
                "minimal_KT_lift_status": "REMAINS_Q_EXACT_MOD_D_H",
            }
            for row in even["exact_classes"]
        ],
    }


def analysis() -> dict[str, Any]:
    export = json.loads(EXPORT.read_text())
    imported = json.loads(IMPORT.read_text())
    h04 = json.loads(H04.read_text())
    h14_even = json.loads(H14_EVEN.read_text())
    h14_odd = json.loads(H14_ODD.read_text())
    euler_reference = export["dependency_refs"]["euler_lagrange_rows"]
    euler_path = ROOT / euler_reference["path"]
    if _sha256(euler_path) != euler_reference["sha256"]:
        raise ValueError("Euler--Lagrange adapted-coordinate input drifted")
    euler = json.loads(euler_path.read_text())
    regular_statement = euler.get("regular_coordinate_statement")
    if regular_statement != (
        "E_g and its differential consequences replace the transverse-tracefree "
        "highest metric jets on the regular Bach locus"
    ):
        raise ValueError("regular Bach-locus coordinate statement drifted")
    if (
        imported["classical_commit"] != export["classical_commit"]
        or imported["claim_flags"]["CLASSICAL_ANTIFIELD_EXPORT_IMPORTED"] is not True
        or imported["claim_flags"]["CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT"] is not True
    ):
        raise ValueError("accepted classical antifield import is absent or drifted")
    atoms = {row["atom_id"]: row for row in export["atoms"]}
    delta_rows = _parse_rows(export["differential"]["delta"], atoms)
    nonzero = {source: image for source, image in delta_rows.items() if image}
    if len(nonzero) != 6 or export["differential"]["Q_gt0"]:
        raise ValueError("minimal Koszul--Tate pair inventory drifted")

    pairs: list[dict[str, Any]] = []
    sigma_rows: dict[str, Polynomial] = {atom: {} for atom in atoms}
    pair_atoms: set[str] = set()
    for source, image in nonzero.items():
        coefficient, target = _single_atom_image(image, source)
        if delta_rows[target]:
            raise ValueError(f"{source}: target is not delta closed")
        source_atom, target_atom = atoms[source], atoms[target]
        tensor_keys = (
            "covariant_rank",
            "contravariant_rank",
            "symmetry",
            "spacetime_parity",
        )
        if (
            any(
                source_atom["tensor_signature"][key]
                != target_atom["tensor_signature"][key]
                for key in tensor_keys
            )
            or source_atom["antifield_number"] != target_atom["antifield_number"] + 1
            or source_atom["ghost_number"] + 1 != target_atom["ghost_number"]
            or source_atom["form_degree"] != target_atom["form_degree"]
            or _fraction(source_atom["mass_dimension"]) != _fraction(target_atom["mass_dimension"])
            or _fraction(source_atom["Weyl_weight"]) != _fraction(target_atom["Weyl_weight"])
            or source_atom["Grassmann_parity"] == target_atom["Grassmann_parity"]
        ):
            raise ValueError(f"{source}: covariant pair grading drifted")
        sigma_rows[target] = {(source,): Fraction(1, 1) / coefficient}
        pair_atoms.update((source, target))
        pairs.append(
            {
                "source": source,
                "target": target,
                "delta_coefficient": {
                    "numerator": coefficient.numerator,
                    "denominator": coefficient.denominator,
                },
                "source_antifield_number": source_atom["antifield_number"],
                "target_antifield_number": target_atom["antifield_number"],
                "tensor_signature": source_atom["tensor_signature"],
            }
        )

    positive_atoms = {
        atom for atom, row in atoms.items() if row["antifield_number"] > 0
    }
    if positive_atoms != {atom for atom in pair_atoms if atoms[atom]["antifield_number"] > 0}:
        raise ValueError("positive-antifield atom coverage is incomplete")

    generator_checks = {}
    for atom in atoms:
        identity = _poly_add(
            _derivation(_derivation({(atom,): Fraction(1)}, sigma_rows, atoms), delta_rows, atoms),
            _derivation(_derivation({(atom,): Fraction(1)}, delta_rows, atoms), sigma_rows, atoms),
        )
        expected = {(atom,): Fraction(1)} if atom in pair_atoms else {}
        if identity != expected:
            raise ValueError(f"Koszul--Tate Euler identity failed on {atom}")
        generator_checks[atom] = "PAIR_EULER" if atom in pair_atoms else "BASE_ZERO"

    pair_order = tuple(sorted(pair_atoms, key=lambda atom: atoms[atom]["canonical_order"]))
    regressions = _regression_monomials(atoms, pair_order)
    for monomial in regressions:
        value = {monomial: Fraction(1)}
        lhs = _poly_add(
            _derivation(_homotopy(value, sigma_rows, atoms, pair_atoms), delta_rows, atoms),
            _homotopy(_derivation(value, delta_rows, atoms), sigma_rows, atoms, pair_atoms),
        )
        if lhs != value:
            raise ValueError(f"contracting homotopy failed on {monomial}")

    positive_form_degrees = {
        row["form_degree"] for row in atoms.values() if row["antifield_number"] > 0
    }
    if positive_form_degrees != {4}:
        raise ValueError("positive antifields no longer saturate top form degree")

    dependencies = {
        "classical_export": _sha256(EXPORT),
        "quantum_import": _sha256(IMPORT),
        "AFN0_H04": _sha256(H04),
        "AFN0_H14_even": _sha256(H14_EVEN),
        "AFN0_H14_odd": _sha256(H14_ODD),
        "euler_lagrange_adapted_coordinates": _sha256(euler_path),
    }
    proof_payload = {
        "pairs": pairs,
        "generator_checks": generator_checks,
        "regression_monomial_count": len(regressions),
        "regression_manifest_sha256": _canonical_hash([list(row) for row in regressions]),
        "positive_antifield_atoms": sorted(positive_atoms),
        "positive_form_degrees": sorted(positive_form_degrees),
        "dependencies": dependencies,
    }
    return {
        "classical_commit": export["classical_commit"],
        "dependency_hashes": dependencies,
        "contractible_pairs": pairs,
        "pair_atom_count": len(pair_atoms),
        "base_atom_count": len(atoms) - len(pair_atoms),
        "positive_antifield_atom_count": len(positive_atoms),
        "generator_euler_identity": generator_checks,
        "regression_monomial_count": len(regressions),
        "regression_manifest_sha256": proof_payload["regression_manifest_sha256"],
        "spectral_sequence": {
            "filtration": "ANTIFIELD_NUMBER_0_TO_2",
            "E0_differential": "delta",
            "E1_positive_antifield_columns": "ZERO_BY_EXPLICIT_CONTRACTION",
            "E1_antifield_zero": "AFN0_MOD_EULER_NOETHER_IDEAL",
            "positive_Q_components": "ABSENT",
            "collapse_page": "E2",
            "relative_form_argument": "ALL_POSITIVE_ANTIFIELD_ATOMS_HAVE_FORM_DEGREE_4_SO_NO_POSITIVE_AFN_LOWER_FORM_CARRIER_EXISTS",
            "regular_coordinate_input": regular_statement,
            "AFN0_basis_separation": "CURVATURE_TENSOR_CANDIDATE_BASES_ARE_INDEPENDENT_OF_THE_E_G_PAIR_COORDINATES_ON_THE_REGULAR_BACH_LOCUS",
        },
        "lift_ledger": _classes(h04, h14_even, h14_odd),
        "open_sectors": {
            "H04": "KT_COMPLETE_COVARIANT_AFN0_CANDIDATE_QUOTIENT_LIFTS",
            "H14_Weyl": "KT_COMPLETE_AFN0_WEYL_GHOST_CANDIDATE_QUOTIENT_LIFTS",
            "H14_pure_Diff": "AFN0_AMBIENT_TOP_AND_TOTAL_COMPLEX_OPEN",
            "H14_mixed_Diff_Weyl": "AFN0_AMBIENT_TOTAL_COMPLEX_OPEN",
            "full_minimal_BV_H14": "NOT_COMPUTED",
        },
        "proof_sha256": _canonical_hash(proof_payload),
    }
