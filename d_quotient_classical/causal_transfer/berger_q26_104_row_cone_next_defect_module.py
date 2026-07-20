#!/usr/bin/env python3
"""Close the next defect module of the obstructed 104-row cone lift.

For the canonical doubled cone, equivariance would require ``D q = q A``.
The obstruction is the image of ``q A`` on ``ker(q)``.  Cyclic completion
also requires the algebraic-dual obstruction.  This module evaluates those
two spaces in the exact spin-four representation and closes them under
``q``, ``A`` and their transposed free-dual actions.

The closure is again the full 936-dimensional represented carrier.  Thus
repairing this cone architecture requires another complete 104-row free
orbit.  This is not a lower bound for arbitrary non-cone completions.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import numpy as np

from d_quotient_classical.causal_transfer import (
    berger_q26_finite_row_module_closure as base,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = "BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_cone_next_defect_module_v1/"
    "spin4_next_defect_closure_witness.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-cone-next-defect-module-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-cone-next-defect-module-v1.schema.json"
)
VERIFIER = HERE / "verify_berger_q26_104_row_cone_next_defect_module.py"
TESTS = (
    HERE / "tests/test_berger_q26_104_row_cone_next_defect_module.py"
)
CONE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json"
)
CONE_PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_canonical_cone_lift_obstruction_v1/"
    "rational_trivial_representation_witness.json"
)
PRIME = 1009
SEED = 26072104


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _kernel(value: np.ndarray) -> np.ndarray:
    reduced, pivots = base._rref(value, PRIME)
    free = [
        column
        for column in range(value.shape[1])
        if column not in pivots
    ]
    result = np.zeros((value.shape[1], len(free)), dtype=np.int64)
    for local, column in enumerate(free):
        result[column, local] = 1
        for row, pivot in enumerate(pivots):
            result[pivot, local] = -reduced[row, column] % PRIME
    if np.any(value @ result % PRIME):
        raise AssertionError("kernel construction failed")
    return result


def _rank(value: np.ndarray) -> int:
    return len(base._rref(value, PRIME)[1])


@lru_cache(maxsize=1)
def closure_audit() -> dict[str, Any]:
    q_value, evolution = base._load_operators()
    representation = base._spin_representation(4, PRIME)
    q = base._evaluate_matrix(q_value, representation, PRIME)
    A = base._evaluate_matrix(evolution, representation, PRIME)
    kernel = _kernel(q)
    left_kernel = _kernel(q.T)
    right_defect = q @ A % PRIME @ kernel % PRIME
    left_defect = (left_kernel.T @ A % PRIME @ q % PRIME).T
    raw_ranks = {
        "q": _rank(q),
        "kernel_q": kernel.shape[1],
        "right_lift_cokernel_image": _rank(right_defect),
        "left_adjoint_cokernel_image": _rank(left_defect),
        "combined_next_defect": _rank(
            np.concatenate([right_defect, left_defect], axis=1)
        ),
    }
    if raw_ranks != {
        "q": 351,
        "kernel_q": 585,
        "right_lift_cokernel_image": 27,
        "left_adjoint_cokernel_image": 70,
        "combined_next_defect": 97,
    }:
        raise AssertionError(f"next defect ranks drifted: {raw_ranks}")
    generator = np.random.default_rng(SEED)
    closure = base._compress(
        [right_defect, left_defect], generator, 97, PRIME
    )
    levels = []
    for _ in range(8):
        witness = base._leading_minor_witness(closure, PRIME)
        levels.append(witness)
        if witness["certified_independent_columns"] == 936:
            break
        closure = base._compress(
            [
                closure,
                q @ closure % PRIME,
                A @ closure % PRIME,
                q.T @ closure % PRIME,
                A.T @ closure % PRIME,
            ],
            generator,
            150,
            PRIME,
        )
    dimensions = [
        level["certified_independent_columns"] for level in levels
    ]
    if dimensions != [97, 344, 856, 936]:
        raise AssertionError(f"next defect closure drifted: {dimensions}")
    if levels[-1]["minor_determinant_mod_prime"] != 411:
        raise AssertionError("next defect full minor drifted")
    return {
        "schema": (
            "pure-weyl-berger-q26-spin4-cone-next-defect-closure-"
            "witness-v1"
        ),
        "result_id": (
            "BERGER_Q26_SPIN4_CONE_NEXT_DEFECT_CLOSURE_WITNESS_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "prime": PRIME,
        "specialization": base.SPECIALIZATION,
        "representation": (
            "9-dimensional rational spin-4 harmonic-polynomial "
            "representation"
        ),
        "representation_dimension": 9,
        "ambient_dimension": 936,
        "next_defect_definition": {
            "right": "Im(q*A restricted to ker(q))",
            "left_adjoint": (
                "transpose of Im(ker(q^T)^T*A*q)"
            ),
            "closure_actions": ["q", "A", "q^vee", "A^vee"],
        },
        "raw_ranks": raw_ranks,
        "seed": SEED,
        "closure_levels": levels,
        "full_closure": True,
        "forced_additional_free_rows_in_cone_tower_at_least": 104,
    }


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    cone = _load(CONE)
    if (
        cone.get("result_id")
        != "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1"
        or cone["classification"][
            "canonical_doubled_cone_evolution_lift_exists"
        ]
    ):
        raise AssertionError("canonical cone input drifted")
    payload = closure_audit()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-cone-next-defect-module-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "CANONICAL_CONE_LIFT_DEFECT_REGENERATES_FULL_104_ROW_"
            "FREE_ORBIT"
        ),
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "charge_sector": (
                "unquotiented retained-26 formal companion/Cauchy carrier"
            ),
            "carrier": (
                "canonical same-profile doubled-cone repair tower only"
            ),
            "degree": (
                "each free orbit has profile (-1:12,0:40,1:40,2:12)"
            ),
            "parity": "right lift plus free algebraic-dual lift",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "all finite-order Berger PBW derivatives",
            "omega": "stationary A104 formal evolution; no spectral split",
        },
        "pinned_inputs": {
            "canonical_cone_obstruction": _artifact(
                CONE,
                "BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1",
            ),
            "canonical_cone_rational_witness": _artifact(
                CONE_PAYLOAD,
                (
                    "BERGER_Q26_CANONICAL_CONE_RATIONAL_TRIVIAL_"
                    "REPRESENTATION_WITNESS_V1"
                ),
            ),
            "module_lower_bound": _artifact(
                base.OUTPUT,
                "BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1",
            ),
        },
        "next_defect_module": {
            "right_generator": "Im(q*A|ker(q))",
            "left_adjoint_generator": (
                "transpose Im(ker(q^T)^T*A*q)"
            ),
            "spin4_raw_ranks": payload["raw_ranks"],
            "closure_actions": ["q", "A104", "q^vee", "A104^vee"],
            "level_independent_columns": [
                item["certified_independent_columns"]
                for item in payload["closure_levels"]
            ],
            "ambient_dimension": 936,
            "full_closure": True,
            "full_minor_determinant_mod_1009": 411,
            "additional_free_rows_in_this_tower_at_least": 104,
            "canonical_tower_total_added_rows_at_least": 208,
            "canonical_tower_total_carrier_rows_at_least": 312,
        },
        "proof": {
            "finite_field_lift": (
                "All denominators are invertible modulo 1009. The nonzero "
                "936-by-936 minor proves rational rank 936."
            ),
            "row_bound": (
                "One free PBW row evaluates to at most nine dimensions, so "
                "the regenerated 936-dimensional orbit needs at least 104 "
                "additional rows."
            ),
            "scope": (
                "The generator is the residual Dq=qA/free-adjoint cokernel "
                "of the canonical cone, not the complete general non-cone "
                "104-row equation system."
            ),
        },
        "exact_payload": {
            "artifact_id": payload["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(payload_text.encode()).hexdigest(),
        },
        "classification": {
            "canonical_cone_next_defect_closure_full_on_spin4": True,
            "canonical_same_profile_cone_tower_needs_at_least_208_new_rows": True,
            "canonical_same_profile_cone_tower_312_row_carrier_constructed": False,
            "all_non_cone_104_row_completions_obstructed": False,
            "global_minimum_added_rows_raised_above_104": False,
            "no_finite_closure_theorem": False,
            "physical_Cauchy_pairing_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": (
            "LEAVE_THE_CANONICAL_CONE_TOWER_AND_SOLVE_THE_COMPLETE_"
            "NON_CONE_104_ROW_FACTOR_SYSTEM"
        ),
        "claim_boundary": (
            "This exact representation/module theorem proves that the next "
            "right/adjoint lift defect of the canonical same-profile cone "
            "regenerates a full free orbit and therefore forces at least "
            "another 104 rows in that architecture. It does not prove that "
            "a general non-cone 104-row completion fails, does not raise the "
            "global 104-row lower bound, and constructs no 312-row carrier, "
            "physical pairing, retained contraction, Hadamard state, QME or "
            "quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "berger_q26_104_row_cone_next_defect_module "
                    "--check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer."
                    "verify_berger_q26_104_row_cone_next_defect_module"
                ),
                (
                    "PYTHONPATH=. python3 -m unittest "
                    "d_quotient_classical.causal_transfer.tests."
                    "test_berger_q26_104_row_cone_next_defect_module"
                ),
                (
                    "npx --yes ajv-cli@5 validate --spec=draft2020 "
                    "--strict=true -s d_quotient_classical/schema/"
                    "berger-q26-104-row-cone-next-defect-module-v1."
                    "schema.json -d d_quotient_classical/certificates/"
                    f"{RESULT_ID}.json"
                ),
            ],
        },
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Berger q26 canonical-cone next defect module

The canonical 104-row doubled cone is nilpotent, but evolution compatibility
requires \(Dq=qA\).  Its unresolved right defect is

\[
\operatorname{Im}\!\left(qA\big|_{\ker q}\right),
\]

and cyclic/free-adjoint completion supplies the transposed left defect.

In the exact nine-dimensional spin-four representation over
\(\mathbf F_{1009}\), their ranks are 27 and 70 and their combined rank is
97.  Closing that combined space under \(q\), \(A_{104}\), and their
free-dual actions gives

\[
97\longrightarrow344\longrightarrow856\longrightarrow936.
\]

The last exact minor has determinant \(411\pmod{1009}\).  Thus this next
defect is again a full represented free orbit.  One row supplies at most nine
represented dimensions, so the canonical same-profile cone repair requires
at least another 104 rows: at least 208 added rows and 312 total rows in that
architecture.

This is not a global 208-new-row lower bound.  General non-cone off-diagonal
104-row factorizations remain open, and no physical pairing, retained
contraction, Hadamard or quantum object is constructed.
"""


def _guards(value: dict[str, Any]) -> None:
    mutations = [
        (
            "classification",
            "all_non_cone_104_row_completions_obstructed",
            True,
        ),
        (
            "classification",
            "global_minimum_added_rows_raised_above_104",
            True,
        ),
        ("classification", "Hadamard_or_quantum_claim", True),
    ]
    for section, field, replacement in mutations:
        mutant = deepcopy(value)
        mutant[section][field] = replacement
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation survived: {section}.{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = closure_audit()
    value = build()
    validate(value)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if PAYLOAD.read_text() != _render(payload):
            raise AssertionError("next-defect payload drifted")
        if OUTPUT.read_text() != _render(value):
            raise AssertionError("next-defect certificate drifted")
        if REPORT.read_text() != _report():
            raise AssertionError("next-defect report drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
