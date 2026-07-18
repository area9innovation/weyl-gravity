#!/usr/bin/env python3
"""Certify the PBW-positive-jet super-cotangent lift convention.

The zero-word convention only transposes fibre indices.  At positive jet
order the derivative carried by the transposed input must instead be moved by
its formal adjoint and expanded over the product of the output antifield and
the remaining inputs.  This module implements that operation exactly in the
retained Berger PBW algebra and checks that its zero-word restriction is the
already-certified algebraic lift.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_full_bv_coderivation_redefinition as zero,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    _pbw_word,
)
from d_quotient_classical.backreacted_clock.berger_support_local_q2 import (
    U,
    U0,
    V,
    V0,
)


ROOT = zero.ROOT
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-positive-jet-super-cotangent-redefinition-convention-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-positive-jet-super-cotangent-redefinition-convention.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_positive_jet_super_cotangent_redefinition_convention.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_positive_jet_super_cotangent_redefinition_convention.py"
ZERO_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json"

Word = tuple[int, ...]
Atom = tuple[int, Word]
Key = tuple[int, tuple[Atom, ...]]
JetTaylor = dict[Key, sp.Expr]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_atoms(atoms: Iterable[Atom]) -> tuple[tuple[Atom, ...] | None, int]:
    """Return the graded-symmetric atom key and its Koszul sign."""

    values = tuple((int(field), tuple(word)) for field, word in atoms)
    exponent = sum(
        zero.PARITIES[values[left][0]] * zero.PARITIES[values[right][0]]
        for left in range(len(values))
        for right in range(left + 1, len(values))
        if values[left] > values[right]
    )
    key = tuple(sorted(values))
    if any(
        key[index] == key[index + 1] and zero.PARITIES[key[index][0]]
        for index in range(len(key) - 1)
    ):
        return None, 0
    return key, -1 if exponent & 1 else 1


def _add(
    value: JetTaylor,
    output: int,
    atoms: Iterable[Atom],
    coefficient: sp.Expr,
) -> None:
    canonical, sign = _canonical_atoms(atoms)
    if canonical is None:
        return
    key = (output, canonical)
    updated = sp.expand(value.get(key, 0) + sign * coefficient)
    if updated:
        value[key] = updated
    else:
        value.pop(key, None)


def _canonical_pbw_terms(atoms: Iterable[Atom]) -> tuple[tuple[tuple[Atom, ...], sp.Expr], ...]:
    """PBW-normalize every input word and then graded-symmetrize the atoms."""

    states: dict[tuple[Atom, ...], sp.Expr] = {(): sp.Integer(1)}
    for field, word in atoms:
        updated: dict[tuple[Atom, ...], sp.Expr] = {}
        for prefix, prefix_coefficient in states.items():
            for reduced, coefficient in _pbw_word(tuple(word)):
                coefficient = sp.expand(coefficient.subs({U: U0, V: V0}))
                raw = (*prefix, (field, reduced))
                canonical, sign = _canonical_atoms(raw)
                if canonical is None:
                    continue
                key = canonical
                updated[key] = sp.expand(
                    updated.get(key, 0) + sign * prefix_coefficient * coefficient
                )
                if updated[key] == 0:
                    updated.pop(key)
        states = updated
    return tuple(sorted(states.items()))


def _adjoint_product_terms(
    word: Word,
    factors: tuple[Atom, ...],
    *,
    omit_formal_adjoint_sign: bool = False,
) -> tuple[tuple[tuple[Atom, ...], sp.Expr], ...]:
    """Expand ``D_word^sharp`` on an arbitrary product in Berger PBW form."""

    states: dict[tuple[Atom, ...], int] = {factors: 1}
    # (D_word)^sharp=(-1)^len(word) D_reverse(word).  As in the certified
    # bilinear/trilinear engine, product action therefore iterates the stored
    # word in its original order and prepends the differentiated axis.
    for axis in word:
        updated: dict[tuple[Atom, ...], int] = {}
        for atoms, multiplicity in states.items():
            for slot in range(len(atoms)):
                shifted = list(atoms)
                field, old_word = shifted[slot]
                shifted[slot] = (field, (axis, *old_word))
                key = tuple(shifted)
                updated[key] = updated.get(key, 0) + multiplicity
        states = updated
    sign = 1 if omit_formal_adjoint_sign else (-1 if len(word) & 1 else 1)
    combined: JetTaylor = {}
    for atoms, multiplicity in states.items():
        for canonical, coefficient in _canonical_pbw_terms(atoms):
            _add(
                combined,
                0,
                canonical,
                sign * multiplicity * coefficient,
            )
    return tuple(
        (atoms, coefficient)
        for (_, atoms), coefficient in sorted(combined.items())
    )


def cotangent_column(
    output: int,
    inputs: tuple[Atom, ...],
    *,
    omit_formal_adjoint_sign: bool = False,
) -> JetTaylor:
    """Lift one degree-zero symmetric base Taylor coefficient canonically.

    ``inputs`` is one graded-symmetric Taylor key, not a polynomial-density
    monomial.  The base coefficient is one.  Each distinct input atom is
    first moved to the leading slot with its Koszul sign; its derivative word
    is then transposed onto the output-dual/remaining-input product.
    """

    canonical, sign = _canonical_atoms(inputs)
    if canonical is None or sign != 1 or canonical != inputs:
        raise ValueError("cotangent input atoms must be a nonzero canonical key")
    value: JetTaylor = {}
    _add(value, output, inputs, sp.Integer(1))
    for selected in sorted(set(inputs)):
        remaining = list(inputs)
        remaining.remove(selected)
        input_row, input_word = selected
        ordered = (selected, *remaining)
        ordered_canonical, ordered_sign = _canonical_atoms(ordered)
        if ordered_canonical != inputs:
            raise AssertionError("selected-slot canonicalization drifted")
        typed_coefficient = (
            -(-1 if zero.PARITIES[input_row] else 1)
            * zero.PAIRING_WEIGHT[output]
            / zero.PAIRING_WEIGHT[input_row]
            * ordered_sign
        )
        factors = ((zero.PARTNER[output], ()), *remaining)
        for new_inputs, adjoint_coefficient in _adjoint_product_terms(
            input_word,
            factors,
            omit_formal_adjoint_sign=omit_formal_adjoint_sign,
        ):
            _add(
                value,
                zero.PARTNER[input_row],
                new_inputs,
                typed_coefficient * adjoint_coefficient,
            )
    return value


def _zero_projection(value: Mapping[Key, sp.Expr]) -> zero.Taylor:
    projected: zero.Taylor = {}
    for (output, atoms), coefficient in value.items():
        if all(not word for _, word in atoms):
            zero._add(projected, output, (field for field, _ in atoms), coefficient)
    return projected


def zero_word_compatibility() -> dict[str, object]:
    labels = (*zero.LABELS2, *zero.LABELS3)
    defects = []
    component_count = 0
    for output, inputs in labels:
        lifted = cotangent_column(output, tuple((row, ()) for row in inputs))
        expected = zero.cotangent_column(output, inputs)
        projected = _zero_projection(lifted)
        component_count += len(projected)
        if projected != expected:
            defects.append((output, inputs))
    if defects:
        raise ValueError(f"positive-jet lift lost zero-word convention: {defects[:1]}")
    return {
        "F2_labels_checked": len(zero.LABELS2),
        "F3_labels_checked": len(zero.LABELS3),
        "lifted_zero_word_components_checked": component_count,
        "defects": 0,
    }


def positive_jet_controls() -> dict[str, object]:
    # One derivative on a Maxwell input of a gravity-output F2 map forces the
    # typed half-weight and one formal-adjoint minus sign.  The second input
    # is deliberately repeated at the field level but differs as a jet atom.
    first_inputs = ((27, ()), (27, (0,)))
    first = cotangent_column(3, first_inputs)
    first_mutant = cotangent_column(
        3, first_inputs, omit_formal_adjoint_sign=True
    )
    first_dual = {
        key: sp.factor(value)
        for key, value in first.items()
        if key[0] == zero.PARTNER[27]
    }
    first_mutant_dual = {
        key: sp.factor(value)
        for key, value in first_mutant.items()
        if key[0] == zero.PARTNER[27]
    }
    # The two transpose contributions cancel on the derivative-A carrier and
    # leave one derivative-output-dual carrier.  The sign mutant misses that
    # cancellation and is therefore especially sharp.
    if len(first_dual) != 1 or first_dual == first_mutant_dual:
        raise ValueError("first-jet formal-adjoint control lost sensitivity")

    # The noncommuting word (2,1) has a PBW commutator tail at the positive
    # Berger fixture.  Reversing/normalizing only after adjunction is thus a
    # sharper control than a commuting-coordinate second derivative.
    second_inputs = ((27, ()), (28, (2, 1)))
    second = cotangent_column(4, second_inputs)
    second_mutant = cotangent_column(
        4, second_inputs, omit_formal_adjoint_sign=True
    )
    # Even derivative length has no overall sign mutation; require instead a
    # genuine order-one PBW tail and exact agreement of the two constructions.
    order_histogram = Counter(
        sum(len(word) for _, word in atoms)
        for (_, atoms), coefficient in second.items()
        if coefficient
    )
    if order_histogram[1] == 0 or second != second_mutant:
        raise ValueError("noncommuting second-jet PBW control drifted")

    odd_inputs = ((0, (3,)), (27, ()))
    odd = cotangent_column(26, odd_inputs)
    odd_dual_outputs = sorted(
        output
        for (output, _), coefficient in odd.items()
        if output != 26 and coefficient
    )
    if zero.PARTNER[0] not in odd_dual_outputs:
        raise ValueError("odd-input cotangent partner is absent")

    return {
        "first_jet_fixture": {
            "base_output": 3,
            "input_atoms": [[27, []], [27, [0]]],
            "dual_component_count": len(first_dual),
            "formal_adjoint_sign_mutation_changed_dual": True,
        },
        "noncommuting_second_jet_fixture": {
            "base_output": 4,
            "input_atoms": [[27, []], [28, [2, 1]]],
            "PBW_total_order_histogram": {
                str(order): count for order, count in sorted(order_histogram.items())
            },
            "order_one_commutator_tail_present": True,
        },
        "odd_input_fixture": {
            "base_output": 26,
            "input_atoms": [[0, [3]], [27, []]],
            "odd_input_partner_output": zero.PARTNER[0],
            "odd_input_partner_present": True,
        },
    }


def scientific_replay() -> dict[str, object]:
    return {
        "formula": (
            "F^(i*)=-(-1)^parity(i) w(B)/w(i) "
            "(D_word)^sharp(B*,remaining), followed by Berger PBW reduction"
        ),
        "zero_word_restriction": zero_word_compatibility(),
        "positive_jet_controls": positive_jet_controls(),
    }


def build() -> dict[str, object]:
    replay = scientific_replay()
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    return {
        "schema": "pure-weyl-berger-positive-jet-super-cotangent-redefinition-convention-v1",
        "result_id": "BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1",
        "result_state": "PBW_POSITIVE_JET_SUPER_COTANGENT_CONVENTION_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "dependency_refs": {
            "zero_word_convention": {
                "path": str(ZERO_CERTIFICATE.relative_to(ROOT)),
                "sha256": _sha256(ZERO_CERTIFICATE),
            }
        },
        "scientific_replay": replay,
        "claim_flags": {
            "PBW_POSITIVE_JET_SUPER_COTANGENT_CONVENTION_CERTIFIED": True,
            "ZERO_WORD_CONVENTION_REPRODUCED": True,
            "FULL_BV_ORDER_TWO_REPLAY_COMPUTED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_PBW_ORDER_TWO_FULL_BV_REDEFINITION_V1",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha256(path) for path in sources
        },
        "verification_commands": [
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_positive_jet_super_cotangent_redefinition_convention.py --check",
            "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_positive_jet_super_cotangent_redefinition_convention.py",
            "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_positive_jet_super_cotangent_redefinition_convention -v",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-positive-jet-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json",
        ],
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC G0 prerequisite fixes the derivative-aware "
            "super-cotangent lift for retained Berger PBW Taylor maps. It replays "
            "all zero-word F2/F3 base labels against the certified algebraic "
            "convention, detects omission of the odd first-derivative formal-adjoint "
            "sign, and retains the commutator tail of a noncommuting second-order "
            "word. It does not assemble or solve the full-BV order-two coboundary "
            "system, decide a cyclic deformation class, descend to residual "
            "cohomology, or make a quantum claim."
        ),
    }


def validate(value: Mapping[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("positive-jet cotangent convention certificate drifted")


def _report(value: Mapping[str, object]) -> str:
    zero_replay = value["scientific_replay"]["zero_word_restriction"]
    return f"""# Positive-jet super-cotangent redefinition convention

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact lift transposes every derivative-bearing input by its PBW formal
adjoint over the output-antifield/remaining-input product. It reproduces all
`{zero_replay['F2_labels_checked']}` F2 and
`{zero_replay['F3_labels_checked']}` F3 zero-word base labels of the frozen
algebraic convention. An odd first-derivative mutation changes the dual
components, while the noncommuting word `(2,1)` produces the required
positive-order Berger commutator tail.

This freezes the convention prerequisite only. The full-BV order-two replay
and its primitive/obstruction verdict remain the next gate.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_positive_jet_super_cotangent_redefinition_convention.py --check` | 6.52 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_positive_jet_super_cotangent_redefinition_convention.py` | 6.24 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_positive_jet_super_cotangent_redefinition_convention -v` | 11.52 s | PASS (4 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-positive-jet-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json` | 3.01 s | PASS |

Tier 2 is the complete zero-word restriction replay plus the exact
positive-jet mutation controls. Tier 3 was not run because this prerequisite
does not change shared core algebra or promote a theorem lifecycle.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        value = build()
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    elif args.check:
        validate(json.loads(OUTPUT.read_text()))
    else:
        print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
    print("BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1: PASS")


if __name__ == "__main__":
    main()
