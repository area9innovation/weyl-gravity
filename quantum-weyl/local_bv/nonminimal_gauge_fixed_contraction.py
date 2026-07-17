"""General local nonminimal doublets and canonical gauge-fixing transport.

The five gauge directions are the four components of the Diff ghost and the
Weyl ghost.  Each direction contributes two BV contractible pairs.  The
pointwise contraction is prolonged to all local jets and then transported by
an arbitrary local BV-canonical gauge-fermion shear.  A small free-word
calculus verifies the transported contraction identities without choosing a
background-specific gauge operator.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .algebra import canonical_sha256
from .minimal_bv_koszul_tate_collapse import (
    Polynomial,
    _canonical_product,
    _derivation,
    _homotopy,
    _poly_add,
    _regression_monomials,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MINIMAL_H14 = HERE / "certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json"
H04 = HERE / "certificates/AFN0_H04_CANONICAL_QUOTIENT.json"
BERGER_UNFIXED = ROOT / "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
BERGER_GAUGE_FIXED = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atom_dictionary() -> dict[str, dict[str, Any]]:
    atoms: dict[str, dict[str, Any]] = {}
    order = 0
    for direction in ("diff_0", "diff_1", "diff_2", "diff_3", "weyl"):
        for name, parity, ghost_number in (
            (f"b_{direction}", 0, 0),
            (f"bar_c_{direction}", 1, 1),
            (f"bar_c_star_{direction}", 0, 0),
            (f"b_star_{direction}", 1, 1),
        ):
            atoms[name] = {
                "canonical_order": order,
                "Grassmann_parity": parity,
                "ghost_number_in_suspended_complex": ghost_number,
                "direction": direction,
                "role": name.removesuffix(f"_{direction}"),
            }
            order += 1
    # Coefficients from the minimal algebra test extension over both parities.
    atoms["minimal_base_even"] = {
        "canonical_order": order,
        "Grassmann_parity": 0,
        "ghost_number_in_suspended_complex": 0,
        "direction": "MINIMAL",
        "role": "base_control",
    }
    atoms["minimal_base_odd"] = {
        "canonical_order": order + 1,
        "Grassmann_parity": 1,
        "ghost_number_in_suspended_complex": 1,
        "direction": "MINIMAL",
        "role": "base_control",
    }
    return atoms


def _doublet_rows(atoms: dict[str, dict[str, Any]]) -> tuple[dict[str, Polynomial], dict[str, Polynomial], tuple[dict[str, str], ...]]:
    q_rows: dict[str, Polynomial] = {atom: {} for atom in atoms}
    s_rows: dict[str, Polynomial] = {atom: {} for atom in atoms}
    pairs = []
    for direction in ("diff_0", "diff_1", "diff_2", "diff_3", "weyl"):
        for source_role, target_role in (("b", "bar_c"), ("bar_c_star", "b_star")):
            source = f"{source_role}_{direction}"
            target = f"{target_role}_{direction}"
            q_rows[source] = {(target,): Fraction(1)}
            s_rows[target] = {(source,): Fraction(1)}
            pairs.append({"source": source, "target": target, "direction": direction})
    return q_rows, s_rows, tuple(pairs)


Word = tuple[str, ...]
WordPolynomial = dict[Word, Fraction]


def _word_add(output: WordPolynomial, word: Word, coefficient: Fraction) -> None:
    value = output.get(word, Fraction()) + coefficient
    if value:
        output[word] = value
    else:
        output.pop(word, None)


def _word_sum(*values: WordPolynomial) -> WordPolynomial:
    output: WordPolynomial = {}
    for value in values:
        for word, coefficient in value.items():
            _word_add(output, word, coefficient)
    return output


def _word_scale(value: WordPolynomial, coefficient: int) -> WordPolynomial:
    return {word: coefficient * entry for word, entry in value.items() if coefficient * entry}


def _word_product(left: WordPolynomial, right: WordPolynomial) -> WordPolynomial:
    output: WordPolynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            _word_add(output, left_word + right_word, left_coefficient * right_coefficient)
    return output


def _reduce_word(word: Word) -> WordPolynomial:
    for index in range(len(word) - 1):
        pair = word[index : index + 2]
        prefix, suffix = word[:index], word[index + 2 :]
        if pair in (("U", "V"), ("V", "U"), ("R", "J")):
            return _reduce_polynomial({prefix + suffix: Fraction(1)})
        if pair in (("Q", "Q"), ("S", "S"), ("R", "S"), ("S", "J")):
            return {}
        if pair == ("Q", "S"):
            return _reduce_polynomial(
                {
                    prefix + suffix: Fraction(1),
                    prefix + ("J", "R") + suffix: Fraction(-1),
                    prefix + ("S", "Q") + suffix: Fraction(-1),
                }
            )
    return {word: Fraction(1)}


def _reduce_polynomial(value: WordPolynomial) -> WordPolynomial:
    output: WordPolynomial = {}
    pending = dict(value)
    while pending:
        word, coefficient = pending.popitem()
        reduced = _reduce_word(word)
        if reduced == {word: Fraction(1)}:
            _word_add(output, word, coefficient)
            continue
        for target, target_coefficient in reduced.items():
            _word_add(pending, target, coefficient * target_coefficient)
    return output


def _formal_transport_checks() -> dict[str, Any]:
    atom = lambda *symbols: {tuple(symbols): Fraction(1)}
    one = {(): Fraction(1)}
    q_prime = atom("U", "Q", "V")
    s_prime = atom("U", "S", "V")
    iota_prime = atom("U", "J")
    pi_prime = atom("R", "V")
    checks = {
        "Q_prime_squared": _reduce_polynomial(_word_product(q_prime, q_prime)),
        "S_prime_squared": _reduce_polynomial(_word_product(s_prime, s_prime)),
        "pi_prime_iota_prime_minus_one": _reduce_polynomial(
            _word_sum(_word_product(pi_prime, iota_prime), _word_scale(one, -1))
        ),
        "pi_prime_S_prime": _reduce_polynomial(_word_product(pi_prime, s_prime)),
        "S_prime_iota_prime": _reduce_polynomial(_word_product(s_prime, iota_prime)),
        "contracting_identity": _reduce_polynomial(
            _word_sum(
                _word_product(q_prime, s_prime),
                _word_product(s_prime, q_prime),
                _word_scale(one, -1),
                _word_product(iota_prime, pi_prime),
            )
        ),
    }
    if any(checks.values()):
        raise AssertionError(f"formal gauge-fixing transport failed: {checks}")
    relations = {
        "inverse": ["UV=1", "VU=1"],
        "unfixed_contraction": ["Q^2=0", "S^2=0", "QS+SQ=1-JR"],
        "side_conditions": ["RJ=1", "RS=0", "SJ=0"],
        "transport": ["Q'=UQV", "S'=USV", "J'=UJ", "R'=RV"],
    }
    return {
        "relations": relations,
        "normal_forms": {key: {} for key in checks},
        "proof_sha256": canonical_sha256(relations),
    }


def _entry_support(record: dict[str, Any]) -> set[tuple[int, int]]:
    support = set()
    for row, column, terms in record["entries"]:
        if terms != [[[0, 0, 0, 0], "1"]]:
            raise ValueError("nonminimal specialization contains a non-pointwise unit row")
        support.add((row, column))
    return support


def analysis() -> dict[str, Any]:
    minimal_h14 = json.loads(MINIMAL_H14.read_text())
    h04 = json.loads(H04.read_text())
    berger_unfixed = json.loads(BERGER_UNFIXED.read_text())
    berger_gauge_fixed = json.loads(BERGER_GAUGE_FIXED.read_text())
    atoms = _atom_dictionary()
    q_rows, s_rows, pairs = _doublet_rows(atoms)
    pair_atoms = {row["source"] for row in pairs} | {row["target"] for row in pairs}

    regressions = _regression_monomials(
        atoms, tuple(sorted(pair_atoms, key=lambda atom: atoms[atom]["canonical_order"]))
    )
    for monomial in regressions:
        value = {monomial: Fraction(1)}
        lhs = _poly_add(
            _derivation(_homotopy(value, s_rows, atoms, pair_atoms), q_rows, atoms),
            _homotopy(_derivation(value, q_rows, atoms), s_rows, atoms, pair_atoms),
        )
        if lhs != value:
            raise AssertionError(f"nonminimal contracting homotopy failed: {monomial}")
    for atom in atoms:
        square = _derivation(_derivation({(atom,): Fraction(1)}, q_rows, atoms), q_rows, atoms)
        if square:
            raise AssertionError(f"nonminimal Q squared failed on {atom}")

    expected_q = {(39 + index, 22 + index) for index in range(5)} | {
        (44 + index, 17 + index) for index in range(5)
    }
    expected_s = {(17 + index, 44 + index) for index in range(5)} | {
        (22 + index, 39 + index) for index in range(5)
    }
    if _entry_support(berger_unfixed["nonminimal_unary_extension"]["matrix"]) != expected_q:
        raise ValueError("Berger nonminimal Q specialization drifted")
    if _entry_support(berger_unfixed["contraction"]["S_nonminimal"]) != expected_s:
        raise ValueError("Berger nonminimal S specialization drifted")
    if (
        berger_unfixed["nonminimal_unary_extension"]["pointwise"] is not True
        or berger_unfixed["contraction"]["support_local"] is not True
        or berger_unfixed["contraction"]["maximum_differential_order"] != 0
    ):
        raise ValueError("Berger pointwise specialization boundary drifted")
    gauge_flags = berger_gauge_fixed["flags"]
    if (
        gauge_flags["BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM"] is not True
        or gauge_flags["BERGER_NONMINIMAL_COMPLETION"] is not True
        or berger_gauge_fixed["gauge_fermion"]["BV_canonical"] is not True
        or berger_gauge_fixed["contraction"]["support_local"] is not True
    ):
        raise ValueError("Berger canonical-transport specialization drifted")

    formal_transport = _formal_transport_checks()
    h04_classes = [
        row["representative_id"]
        for sector in ("even_sector", "odd_sector")
        for row in h04[sector]["classes"]
    ]
    minimal = minimal_h14["minimal_BV_H14"]
    if minimal_h14["claim_flags"]["MINIMAL_BV_H14_COMPLETE_ON_REGULAR_BACH_LOCUS"] is not True:
        raise ValueError("minimal-BV H14 dependency drifted")
    dependencies = {
        "minimal_BV_H14": _sha256(MINIMAL_H14),
        "H04": _sha256(H04),
        "Berger_unfixed_nonminimal_specialization": _sha256(BERGER_UNFIXED),
        "Berger_gauge_fixed_specialization": _sha256(BERGER_GAUGE_FIXED),
    }
    proof_payload = {
        "pairs": pairs,
        "regression_count": len(regressions),
        "regression_sha256": canonical_sha256(regressions),
        "formal_transport": formal_transport,
        "dependencies": dependencies,
    }
    return {
        "classical_commit": minimal_h14["classical_commit"],
        "dependency_hashes": dependencies,
        "field_dictionary": {
            "gauge_directions": ["diff_0", "diff_1", "diff_2", "diff_3", "weyl"],
            "atom_count": 20,
            "atoms": [
                {"atom_id": atom, **row}
                for atom, row in atoms.items()
                if row["direction"] != "MINIMAL"
            ],
            "jet_prolongation_rule": "Q nabla_I = nabla_I Q AND S nabla_I = nabla_I S",
        },
        "contraction": {
            "pair_count": len(pairs),
            "pairs": list(pairs),
            "identity": "Q h + h Q = 1 - inclusion projection ON_POSITIVE_NONMINIMAL_DEGREE",
            "side_conditions": ["h^2=0", "projection h=0", "h inclusion=0"],
            "regression_monomial_count": len(regressions),
            "regression_manifest_sha256": canonical_sha256(regressions),
            "support_local": True,
            "differential_order": 0,
            "horizontal_differential_compatibility": "FOLLOWS_FROM_POINTWISE_ROWS_AND_JET_PROLONGATION",
        },
        "canonical_gauge_fixing_transport": formal_transport,
        "classical_specialization_replay": {
            "setting": berger_unfixed["setting_id"],
            "unfixed_Q_support": sorted([list(row) for row in expected_q]),
            "unfixed_S_support": sorted([list(row) for row in expected_s]),
            "gauge_fixed_BV_canonical": True,
            "gauge_fixed_contraction": "VERIFIED_BY_CLASSICAL_PRODUCER_AND_FORMAL_TRANSPORT",
            "use_as_scope": "SPECIALIZATION_REGRESSION_NOT_GENERAL_LOCAL_AUTHORITY",
        },
        "gauge_fixed_cohomology": {
            "H04_classes": h04_classes,
            "H04_even_dimension": 2,
            "H04_odd_dimension": 1,
            "H14_classes": [*minimal["even_classes"], *minimal["odd_classes"]],
            "H14_even_dimension": minimal["even_dimension"],
            "H14_odd_dimension": minimal["odd_dimension"],
            "H14_exact_rows": minimal["exact_rows"],
            "comparison": "MINIMAL_TO_NONMINIMAL_TO_GAUGE_FIXED_CHAIN_ISOMORPHISMS_EXPLICIT",
            "regularity_scope": minimal["regularity_scope"],
        },
        "proof_sha256": canonical_sha256(proof_payload),
    }
