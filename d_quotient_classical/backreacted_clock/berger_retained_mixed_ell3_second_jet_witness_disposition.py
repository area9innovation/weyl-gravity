#!/usr/bin/env python3
"""Supersede the mixed-ell3 order-two obstruction by an exact jet-two mutation.

The former 22-row functional was exhaustively transposed only through the
zero- and first-input-jet cyclic columns.  The derivative-aware cotangent
convention has lower PBW-order commutator tails, so a second-input-jet column
can enter its page-one support.  This producer records the first exact
counterexample and returns the complete bounded cyclic class to ``OPEN``.

Dependency tag: LOCAL-ALGEBRAIC.  Generality: G0.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

from d_quotient_classical.backreacted_clock import (
    berger_positive_jet_super_cotangent_redefinition_convention as lift,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_bounded_cyclic_scan as scan,
)
from d_quotient_classical.backreacted_clock import (
    berger_retained_mixed_ell3_positive_jet_full_bv_obstruction as old,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-retained-mixed-ell3-second-jet-witness-disposition-v1.md"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-witness-disposition-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_second_jet_witness_disposition.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_retained_mixed_ell3_second_jet_witness_disposition.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _repo_path(path: Path) -> str:
    return str(Path("physics/symplectic-reconstruction") / path.relative_to(ROOT))


def counterexample() -> tuple[dict[tuple[int, tuple], sp.Expr], sp.Expr]:
    column = lift.cotangent_column(4, ((27, (1, 1)), (28, ())))
    pairing = scan._expanded_column_pairing("F2", column)
    return column, sp.factor(pairing)


def _component(output: int, atoms: tuple, coefficient: sp.Expr) -> dict[str, object]:
    return {
        "output": output,
        "atoms": [
            {"field": field, "PBW_word": list(word)} for field, word in atoms
        ],
        "coefficient": str(sp.factor(coefficient)),
    }


def build() -> dict[str, object]:
    old_value = json.loads(old.OUTPUT.read_text())
    column, pairing = counterexample()
    if pairing != sp.Rational(755, 9):
        raise ValueError("second-jet counterexample pairing drifted")
    if len(column) != 5:
        raise ValueError("cyclic cotangent column support drifted")
    source_paths = (
        Path(__file__).resolve(),
        Path(scan.__file__),
        VERIFIER,
        TESTS,
        SCHEMA,
    )
    return {
        "schema": "pure-weyl-berger-retained-mixed-ell3-second-jet-witness-disposition-v1",
        "result_id": "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1",
        "result_state": "ORDER_TWO_OBSTRUCTION_WITHDRAWN_COMPLETE_BOUNDED_CYCLIC_CLASS_OPEN",
        "lifecycle_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "mode_scope": {
            "theory": "pure-Weyl gravity plus rotating Berger clocks and Maxwell",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": "fixed-coupling retained sector with K_Berger=D-omega R",
            "carrier": "typed retained full-BV gravity-clock-Maxwell carrier; mixed quartic action sector represented by ell3",
            "degree": "all BV degrees reached by the declared cyclic F2/F3 cotangent column",
            "parity": "graded mixed gravity-Maxwell",
            "ell": "NO_CERTIFIED_MAP from local PBW jets to Berger harmonics",
            "m": "NO_CERTIFIED_MAP",
            "k": "local PBW derivative axis 1 in the counterexample; no mode covector crosswalk",
            "omega": "NO_CERTIFIED_MAP; the local column is not a K_Berger eigenmode",
        },
        "declared_complex": {
            "coefficient_field": "Q(sqrt(10))",
            "cochains": "support-local mixed-bundle cyclic super-cotangent F2/F3 Taylor maps with nonnegative input PBW words and summed input order at most two",
            "differential": "delta(F2,F3)=[q1,F3]+[q2,F2], evaluated by the native graded coderivation and exact Berger PBW reduction",
            "filtration": "summed pre-reduction input PBW order 0,1,2",
            "equivalence": "q3 is identified with q3+delta(F2,F3) after canonical PBW reduction through output order two",
            "critical_non_strictness": "PBW reduction of differentiated cotangent columns has lower-order commutator tails; input order two therefore contributes to output page one",
        },
        "superseded_result": {
            "result_id": old_value["result_id"],
            "path": str(old.OUTPUT.relative_to(ROOT)),
            "sha256": _sha(old.OUTPUT),
            "retained_subclaim": "the normalized functional annihilates all 5,984 zero-page labels and all 14,998 first-jet labels on each axis",
            "withdrawn_claim": "the same functional obstructs every nonnegative filtered order-two or higher cyclic profile",
            "reason": "the exhaustive transpose omitted admissible second-input-jet columns whose PBW commutator tails enter page one",
        },
        "exact_counterexample": {
            "kind": "F2",
            "base_output": 4,
            "base_atoms": [
                {"field": 27, "PBW_word": [1, 1]},
                {"field": 28, "PBW_word": []},
            ],
            "cotangent_components": [
                _component(output, atoms, coefficient)
                for (output, atoms), coefficient in sorted(column.items())
            ],
            "cotangent_component_count": 5,
            "native_page_one_term_count": 252,
            "old_witness_pairing": "755/9",
            "normalized_witness_cancellation_coefficient": "-9/755",
            "control_mutation": {
                "replacement_word": [0, 0],
                "old_witness_pairing": "0",
            },
        },
        "full_class_disposition": {
            "zero_first_jet_subcomplex": "OBSTRUCTED by the retained 22-row functional",
            "complete_order_two_bounded_cyclic_complex": "OPEN",
            "complete_trivializing_cochain": "NOT_CONSTRUCTED",
            "replacement_full_cokernel_witness": "NOT_CONSTRUCTED",
            "physical_order_two_primitive": "CERTIFIED only after projection to the physical Euler complex; it is not a full-BV cyclic primitive",
            "obvious_lift_attempt": "the physical primitive plus the three known ghost shears leaves 1,380 exact page-zero residual coefficients and is not a trivialization",
        },
        "branch_repair_disposition": {
            "status": "NO_CERTIFIED_MAP",
            "reason": "no landed noncontractible branch repair supplies a crosswalk for this local PBW column; no branch label is assigned",
        },
        "claim_flags": {
            "SECOND_JET_COLUMN_ADMISSIBLE": True,
            "OLD_WITNESS_ANNIHILATES_COMPLETE_ORDER_TWO_COMPLEX": False,
            "ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED": False,
            "COMPLETE_ORDER_TWO_TRIVIALIZATION_EXISTS": False,
            "COMPLETE_ORDER_TWO_CLASS_NONZERO": False,
            "BRANCH_PROJECTION_DECIDED": False,
            "RESIDUAL_COHOMOLOGY_OPERATION_NONZERO": False,
            "QUANTUM_CLAIM": False,
        },
        "source_manifest": {_repo_path(path): _git_blob(path) for path in source_paths},
        "sha256_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in source_paths
        },
        "verification_commands": [
            "PYTHONPYCACHEPREFIX=/tmp/berger-ell3-disposition PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_second_jet_witness_disposition.py --check --guards",
            "PYTHONPYCACHEPREFIX=/tmp/berger-ell3-disposition-verify PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_second_jet_witness_disposition.py",
            "PYTHONPYCACHEPREFIX=/tmp/berger-ell3-disposition-test PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_second_jet_witness_disposition",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-second-jet-witness-disposition-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1.json",
            "PYTHONPYCACHEPREFIX=/tmp/berger-ell3-candidate-page0 PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_retained_mixed_ell3_bounded_cyclic_scan.py --candidate-residual --max-page 0",
        ],
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC disposition disproves the promotion of the retained 22-row functional from the exhaustively checked zero/first-jet subcomplex to the declared derivative-aware cyclic complex through summed input PBW order two. The five-component cyclic cotangent lift of F2^4(D_1D_1 phi_27,phi_28) has native page-one pairing 755/9 with that functional. Hence the old order-two obstruction and all higher-profile consequence are withdrawn, while the exact zero/first-jet annihilation ledger remains valid. This result does not construct a complete trivializing cochain, prove the full class nonzero, identify a residual or physical branch, or make a causal, particle, stability, scattering, all-orders, or quantum claim."
        ),
    }


def validate(value: dict[str, object]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    if flags["SECOND_JET_COLUMN_ADMISSIBLE"] is not True:
        raise ValueError("counterexample lost admissibility")
    for name in (
        "OLD_WITNESS_ANNIHILATES_COMPLETE_ORDER_TWO_COMPLEX",
        "ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED",
        "COMPLETE_ORDER_TWO_TRIVIALIZATION_EXISTS",
        "COMPLETE_ORDER_TWO_CLASS_NONZERO",
        "BRANCH_PROJECTION_DECIDED",
        "RESIDUAL_COHOMOLOGY_OPERATION_NONZERO",
        "QUANTUM_CLAIM",
    ):
        if flags[name] is not False:
            raise ValueError(f"fail-closed flag crossed: {name}")


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Berger retained mixed-ell3 second-jet witness disposition

## Exact result

The former 22-row functional is not a functional on the cokernel of the
declared cyclic deformation complex through input PBW order two.  The
admissible cyclic cotangent column generated by

```text
F2 output 4; inputs (field 27, PBW word (1,1)) and (field 28, empty word)
```

has five exact cotangent components.  Native coderivation replay produces
252 page-one terms, and its pairing with the stored functional is `755/9`.
Multiplying this column by `-9/755` cancels the old normalized witness value.

The mechanism is the lower-order commutator tail in derivative-aware
cotangent transposition and Berger PBW reduction.  The old exhaustive rail
checked 5,984 zero-page and 14,998 first-jet labels per axis, but it did not
check the second-input-jet columns that can feed page one.  Its exact
zero/first-jet subcomplex result remains valid; the claimed order-two and
higher-profile obstruction does not.

## Fail-closed disposition

The complete bounded cyclic class is `OPEN`.  This counterexample kills the
only certified dual witness but does not by itself solve the full coboundary
equation.  Conversely, lifting the certified physical Euler primitive and
adding the three known ghost shears is not a full-BV solution: the attempted
composite leaves 1,380 exact page-zero residual coefficients.  A coupled
zero/first/second-jet full-BV solve or a replacement full-cokernel witness is
still required.

No noncontractible branch repair or local-to-harmonic crosswalk has landed
for this column, so every branch interpretation remains `NO_CERTIFIED_MAP`.

EVIDENCE: `BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1`, its independent native-coderivation verifier, strict schema, scoped mutation tests, tier receipt, and the regenerated nonlinear atlas fragment.

CLOSE-OUT: OBSTRUCTED — the exact second-jet column invalidates the only claimed order-two cokernel witness, but neither a complete bounded cyclic trivializing cochain nor a replacement full-cokernel functional has been constructed; the complete class is therefore `OPEN`.
"""


def _guards(value: dict[str, object]) -> None:
    for name in (
        "OLD_WITNESS_ANNIHILATES_COMPLETE_ORDER_TWO_COMPLEX",
        "ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED",
        "COMPLETE_ORDER_TWO_TRIVIALIZATION_EXISTS",
        "COMPLETE_ORDER_TWO_CLASS_NONZERO",
        "BRANCH_PROJECTION_DECIDED",
        "RESIDUAL_COHOMOLOGY_OPERATION_NONZERO",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["claim_flags"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("second-jet witness disposition outputs drifted")
    if args.guards:
        _guards(value)
    print("BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1: PASS")


if __name__ == "__main__":
    main()
