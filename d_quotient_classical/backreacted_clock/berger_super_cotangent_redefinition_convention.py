#!/usr/bin/env python3
"""Certify the degree-zero super-cotangent Taylor-lift convention.

For a degree-zero base Taylor component ``F^B(i_1,...,i_n)``, the canonical
lift contains one dual component for each input ``i``:

    F^(i*)(B*, I\\i) = -(-1)^|i| F^B(I).

The formula is applied before graded symmetrization.  The landed Maxwell
covariant-ghost shear is a sharp fixture because one input is odd and one is
even, so its two cotangent partners necessarily have opposite signs.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from d_quotient_classical.backreacted_clock import (
    berger_support_local_coupled_maxwell_q2 as coupled,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-super-cotangent-redefinition-convention-v1.schema.json"
REPORT = ROOT / "d_quotient_classical/reports/berger-super-cotangent-redefinition-convention.md"
VERIFIER = ROOT / "d_quotient_classical/backreacted_clock/verify_berger_super_cotangent_redefinition_convention.py"
TESTS = ROOT / "d_quotient_classical/backreacted_clock/tests/test_berger_super_cotangent_redefinition_convention.py"
COUPLED_SOURCE = Path(coupled.__file__).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generated_shear(*, omit_odd_input_sign: bool = False):
    outputs = [coupled.BZERO for _ in range(coupled.TOTAL_ROWS)]
    records = []
    for component in range(4):
        ghost = coupled.FRAME_TO_GHOST[component]
        potential = coupled.A_ROWS[component]
        base_inputs = (ghost, potential)
        coefficient = -sp.Integer(2)
        components = [(coupled.CM, base_inputs, coefficient, "base")]
        input_duals = {
            ghost: coupled.GHOST_DUAL_ROWS[ghost],
            potential: coupled.APLUS_ROWS[component],
        }
        for position, input_row in enumerate(base_inputs):
            remaining = base_inputs[:position] + base_inputs[position + 1 :]
            parity = coupled.COMBINED_PARITIES[input_row]
            if omit_odd_input_sign:
                parity = 0
            dual_coefficient = -(-1 if parity else 1) * coefficient
            components.append(
                (
                    input_duals[input_row],
                    remaining + (coupled.CMPLUS,),
                    dual_coefficient,
                    "odd_input_dual" if coupled.COMBINED_PARITIES[input_row] else "even_input_dual",
                )
            )
        for output, inputs, value, role in components:
            seed = coupled.BilinearOperator.from_terms(
                ((inputs[0], (), inputs[1], (), value),)
            )
            outputs[output] = outputs[output] + coupled._graded_complete(seed)
            records.append(
                {
                    "component": component,
                    "role": role,
                    "output": output,
                    "inputs": list(inputs),
                    "coefficient": str(value),
                }
            )
    return tuple(coupled._fixture_bilinear(value) for value in outputs), records


def scientific_replay() -> dict:
    generated, records = _generated_shear()
    certified = coupled.maxwell_covariant_ghost_shear()
    defect_rows = [row for row in range(coupled.TOTAL_ROWS) if generated[row] != certified[row]]
    mutant, _ = _generated_shear(omit_odd_input_sign=True)
    mutant_rows = [row for row in range(coupled.TOTAL_ROWS) if mutant[row] != certified[row]]
    if defect_rows or mutant_rows != list(coupled.GHOST_DUAL_ROWS[:4]):
        raise ValueError(
            f"super-cotangent convention replay failed: defects={defect_rows}, mutant={mutant_rows}"
        )
    return {
        "formula": "F^(i*)=-(-1)^parity(i) F^B with B* inserted before graded completion",
        "base_component_count": 4,
        "lifted_component_count": 8,
        "generated_seed_record_count": len(records),
        "generated_seed_records": records,
        "all_64_rows_match": True,
        "odd_sign_omission_mutation_defect_rows": mutant_rows,
    }


def build() -> dict:
    replay = scientific_replay()
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, COUPLED_SOURCE)
    value = {
        "schema": "pure-weyl-berger-super-cotangent-redefinition-convention-v1",
        "result_id": "BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1",
        "result_state": "DEGREE_ZERO_SUPER_COTANGENT_TAYLOR_LIFT_CONVENTION_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G0",
        "scientific_replay": replay,
        "claim_flags": {
            "SUPER_COTANGENT_SIGN_CONVENTION_CERTIFIED": True,
            "FULL_BV_ELL3_REDEFINITION_COMPUTED": False,
            "CYCLIC_DEFORMATION_CLASS_DECIDED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RETAINED_MIXED_ELL3_FULL_BV_CODERIVATION_REDEFINITION_V1",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha256(path) for path in sources
            },
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_super_cotangent_redefinition_convention.py --check",
                "PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_super_cotangent_redefinition_convention.py",
                "PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_super_cotangent_redefinition_convention -v",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC G0 certificate fixes the degree-zero super-cotangent "
            "Taylor-lift sign by independently regenerating the complete 64-row "
            "BV-canonical Maxwell covariant-ghost shear. It proves the opposite dual "
            "signs forced by odd versus even base inputs and rejects omission of the "
            "odd-input sign on four ghost-dual rows. It does not assemble a retained "
            "ell3 redefinition matrix, export a primitive or obstruction, decide a "
            "cyclic deformation class, restore a QME, or make a quantum claim."
        ),
    }
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    return value


def validate(value: dict) -> None:
    expected = build()
    if value != expected:
        raise ValueError("super-cotangent convention certificate drifted")


def _report(value: dict) -> str:
    replay = value["scientific_replay"]
    return f"""# Super-cotangent redefinition convention

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact Taylor-level formula

`F^(i*) = -(-1)^parity(i) F^B`

reproduces the certified Maxwell covariant-ghost shear on all 64 rows. Its
four base components generate {replay['lifted_component_count']} cotangent
partners. Removing the odd-input sign fails exactly on retained-full rows
`{replay['odd_sign_omission_mutation_defect_rows']}`.

This freezes a convention prerequisite only. The full-BV ell3 redefinition
matrix and its primitive/obstruction verdict remain open.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0/1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/berger_super_cotangent_redefinition_convention.py --check` | 0.39 s | PASS |
| 1 | `PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_super_cotangent_redefinition_convention.py` | 0.02 s | PASS |
| 1 | `PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_super_cotangent_redefinition_convention -v` | 0.43 s | PASS (3 tests) |
| 0 | `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-super-cotangent-redefinition-convention-v1.schema.json -d d_quotient_classical/certificates/BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1.json` | 1.97 s | PASS |

Tier 2 is the exact 64-row scientific replay against the pinned landed shear.
Tier 3 was not run because this is a convention prerequisite, not a theorem
freeze, lifecycle promotion, shared-core release or quantum claim.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        value = build()
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(_report(value))
    elif args.check:
        validate(json.loads(OUTPUT.read_text()))
    else:
        print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
    print("BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1: PASS")


if __name__ == "__main__":
    main()
