#!/usr/bin/env python3
"""Obstruct the A104 lift on the exact rational non-cone witness.

The preceding feasibility witness supplies a square-zero 208-row differential
with the retained cohomology ranks.  This module proves that this particular
differential cannot carry any chain endomorphism whose old-old compression is
the frozen A104 evolution.  The proof is a one-coordinate boundary-cokernel
witness at the left endpoint; it does not restrict the unspecified new-row
blocks of the putative evolution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
RESULT_ID = (
    "BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1"
)
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_evolution_extension_obstruction_v1/"
    "boundary_cokernel_witness.json"
)
REPORT = (
    ROOT
    / "d_quotient_classical/reports/"
    "berger-q26-104-row-noncone-evolution-extension-obstruction-v1.md"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "berger-q26-104-row-noncone-evolution-extension-obstruction-v1."
    "schema.json"
)
VERIFIER = (
    HERE
    / "verify_berger_q26_104_row_noncone_evolution_extension_obstruction.py"
)
TESTS = (
    HERE
    / "tests/"
    "test_berger_q26_104_row_noncone_evolution_extension_obstruction.py"
)
NONCONE_CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1.json"
)
NONCONE_DIFFERENTIAL = (
    ROOT
    / "d_quotient_classical/generated/"
    "berger_q26_104_row_noncone_rational_nilpotence_feasibility_v1/"
    "rational_noncone_differential.json"
)
A104_CERTIFICATE = (
    ROOT
    / "quantum-weyl/lorentzian/certificates/"
    "BERGER_A104_ENDPOINT_COMPLETION.json"
)
A104_OPERATOR = (
    ROOT
    / "quantum-weyl/lorentzian/generated/"
    "berger_a104_endpoint_completion/global_A104.json"
)

SPECIALIZATION = {"alpha_B": 2, "u": 1, "v": 3}
DEGREES_104 = tuple([-1] * 6 + [0] * 20 + [1] * 20 + [2] * 6) * 2
SOURCE_INDEX = 16
PURE_OLD_BOUNDARY_INDEX = 5
BOUNDARY_COKERNEL_INDEX = 25


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _rational_matrix(record: dict[str, Any]) -> sp.Matrix:
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body):
        raise AssertionError("rational matrix internal hash drifted")
    result = sp.zeros(*record["shape"])
    for row, column, numerator, denominator in record["entries"]:
        result[row, column] = sp.Rational(numerator, denominator)
    return result


def _constant_a104() -> sp.Matrix:
    record = _load(A104_OPERATOR)
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _digest(body):
        raise AssertionError("A104 internal hash drifted")
    alpha_B, u, v = sp.symbols("alpha_B u v")
    substitutions = {
        alpha_B: sp.Rational(SPECIALIZATION["alpha_B"]),
        u: sp.Rational(SPECIALIZATION["u"]),
        v: sp.Rational(SPECIALIZATION["v"]),
    }
    result = sp.zeros(104)
    for row, column, terms in record["entries"]:
        for exponents, coefficient_text in terms:
            if sum(exponents):
                continue
            coefficient = sp.sympify(
                coefficient_text,
                locals={"alpha_B": alpha_B, "u": u, "v": v},
            )
            result[row, column] += coefficient.subs(substitutions)
    return result


def _sparse_vector(value: sp.Matrix) -> list[list[int | str]]:
    if value.cols != 1:
        raise ValueError("expected a column vector")
    return [
        [row, str(value[row, 0])]
        for row in range(value.rows)
        if value[row, 0]
    ]


def exact_witness() -> dict[str, Any]:
    noncone = _load(NONCONE_DIFFERENTIAL)
    differential = _rational_matrix(
        noncone["matrices"]["degree_minus1_to_0"]
    )
    if differential.shape != (80, 24):
        raise AssertionError("left differential shape drifted")

    source = sp.eye(24)[:, SOURCE_INDEX]
    image = differential * source
    expected_image = sp.zeros(80, 1)
    expected_image[PURE_OLD_BOUNDARY_INDEX, 0] = 1
    if image != expected_image:
        raise AssertionError("pure-old boundary witness drifted")

    old_projection = differential[:40, :]
    cokernel = sp.eye(40)[:, BOUNDARY_COKERNEL_INDEX]
    if cokernel.T * old_projection != sp.zeros(1, 24):
        raise AssertionError("boundary cokernel witness drifted")

    degree_zero_indices = [
        index for index, degree in enumerate(DEGREES_104) if degree == 0
    ]
    evolution = _constant_a104().extract(
        degree_zero_indices, degree_zero_indices
    )
    old_boundary = image[:40, :]
    evolved_boundary = evolution * old_boundary
    obstruction = (cokernel.T * evolved_boundary)[0]
    if obstruction != sp.Rational(-51, 2):
        raise AssertionError(
            f"evolution obstruction drifted: {obstruction}"
        )

    body = {
        "schema": (
            "pure-weyl-berger-q26-104-row-noncone-evolution-"
            "boundary-cokernel-witness-v1"
        ),
        "result_id": (
            "BERGER_Q26_104_ROW_NONCONE_EVOLUTION_BOUNDARY_"
            "COKERNEL_WITNESS_V1"
        ),
        "coefficient_field": "QQ",
        "specialization": SPECIALIZATION,
        "degree": {
            "source": -1,
            "target": 0,
            "old_target_dimension": 40,
            "new_target_dimension": 40,
        },
        "source_vector": _sparse_vector(source),
        "differential_image": _sparse_vector(image),
        "boundary_cokernel_covector": _sparse_vector(cokernel),
        "evolved_old_boundary": _sparse_vector(evolved_boundary),
        "identities": {
            "d_source_is_pure_old_e5": True,
            "cokernel_annihilates_old_boundary_projection": True,
            "cokernel_on_A104_e5": "-51/2",
        },
    }
    return {**body, "sha256": _digest(body)}


def _artifact(path: Path, artifact_id: str) -> dict[str, str]:
    return {
        "artifact_id": artifact_id,
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def build() -> dict[str, Any]:
    noncone = _load(NONCONE_CERTIFICATE)
    a104 = _load(A104_CERTIFICATE)
    if (
        noncone.get("result_id")
        != "BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1"
    ):
        raise AssertionError("non-cone feasibility input drifted")
    if a104.get("result_id") != "BERGER_A104_ENDPOINT_COMPLETION":
        raise AssertionError("A104 input drifted")

    witness = exact_witness()
    witness_text = json.dumps(witness, indent=2, sort_keys=True) + "\n"
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
    }
    return {
        "schema": (
            "pure-weyl-berger-q26-104-row-noncone-evolution-"
            "extension-obstruction-v1"
        ),
        "result_id": RESULT_ID,
        "result_state": (
            "EXACT_RATIONAL_BOUNDARY_COKERNEL_OBSTRUCTS_A104_CHAIN_"
            "EXTENSION_ON_THE_NONCONE_FEASIBILITY_WITNESS"
        ),
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "scope": {
            "theory": "retained minimal pure-Weyl Berger BV complex",
            "background": "fixed rational positive Berger clock",
            "boundaries": "R_t x compact Berger S3; no spatial boundary",
            "carrier": (
                "the exact rational 208-row non-cone nilpotence "
                "feasibility witness only"
            ),
            "charge_sector": "unquotiented retained-26 formal Cauchy carrier",
            "degree": "left endpoint -1 -> 0",
            "parity": "BV grading; no pairing imposed",
            "ell": "not harmonic-reduced",
            "m": "not harmonic-reduced",
            "k": "derivative generators specialized to zero",
            "omega": "stationary A104 compression",
        },
        "pinned_inputs": {
            "noncone_feasibility_certificate": _artifact(
                NONCONE_CERTIFICATE, noncone["result_id"]
            ),
            "noncone_rational_differential": _artifact(
                NONCONE_DIFFERENTIAL,
                "BERGER_Q26_104_ROW_NONCONE_RATIONAL_"
                "DIFFERENTIAL_WITNESS_V1",
            ),
            "A104_certificate": _artifact(
                A104_CERTIFICATE, a104["result_id"]
            ),
            "A104_operator": _artifact(
                A104_OPERATOR, "BERGER_A104_EXACT_SPARSE_OPERATOR"
            ),
        },
        "exact_obstruction": {
            "artifact_id": witness["result_id"],
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(witness_text.encode()).hexdigest(),
            "source_basis_index": SOURCE_INDEX,
            "pure_old_boundary_index": PURE_OLD_BOUNDARY_INDEX,
            "boundary_cokernel_index": BOUNDARY_COKERNEL_INDEX,
            "normalized_pairing": "-51/2",
            "free_new_evolution_blocks_eliminated": True,
        },
        "theorem": {
            "hypothesis": (
                "E is any degree-zero chain endomorphism of the fixed "
                "rational 208-row differential whose old-old degree-zero "
                "compression equals the specialized frozen A104 block"
            ),
            "identity": "E_0 d_-1 = d_-1 E_-1",
            "contradiction": (
                "the cokernel covector kills the old projection of "
                "im(d_-1), but evaluates to -51/2 on A104 e5"
            ),
            "conclusion": (
                "no such chain endomorphism E exists on this fixed "
                "non-cone feasibility differential"
            ),
        },
        "classification": {
            "fixed_noncone_witness_A104_chain_extension_exists": False,
            "all_104_row_noncone_differentials_obstructed": False,
            "rational_PBW_operator_completion_constructed": False,
            "cyclic_pairing_constructed": False,
            "real_involution_constructed": False,
            "retained_SDR_constructed": False,
            "Hadamard_or_quantum_claim": False,
        },
        "next_gate": (
            "SOLVE_THE_SIMULTANEOUS_NILPOTENCE_AND_A104_EQUIVARIANCE_"
            "SYSTEM_BEFORE_IMPOSING_CYCLIC_FREE_ADJOINTNESS"
        ),
        "claim_boundary": (
            "This exact boundary-cokernel witness obstructs every A104 "
            "chain extension of the one serialized rational non-cone "
            "nilpotence/cohomology feasibility differential, including "
            "completely unrestricted new-row evolution blocks. It does not "
            "obstruct all 104-new-row non-cone differentials, raise the "
            "global 104-row lower bound, or construct a PBW operator, cyclic "
            "pairing, real involution, retained SDR, Hadamard state or "
            "quantum theory."
        ),
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer.berger_q26_104_row_noncone_"
                    "evolution_extension_obstruction --check --guards"
                ),
                (
                    "PYTHONPATH=. python3 -m d_quotient_classical."
                    "causal_transfer.verify_berger_q26_104_row_noncone_"
                    "evolution_extension_obstruction"
                ),
                (
                    "PYTHONPATH=. python3 -m unittest "
                    "d_quotient_classical.causal_transfer.tests."
                    "test_berger_q26_104_row_noncone_evolution_"
                    "extension_obstruction"
                ),
                (
                    "npx --yes ajv-cli@5 validate --spec=draft2020 "
                    "--strict=true -s d_quotient_classical/schema/"
                    "berger-q26-104-row-noncone-evolution-extension-"
                    "obstruction-v1.schema.json -d "
                    f"d_quotient_classical/certificates/{RESULT_ID}.json"
                ),
            ],
        },
    }


def report_text() -> str:
    return r"""# Berger q26 non-cone evolution-extension obstruction

The exact rational non-cone feasibility differential is nilpotent and has
the retained cohomology dimensions, but it cannot carry the frozen \(A_{104}\)
evolution.

At the left endpoint, source basis vector \(e_{16}\) has differential

\[
d_{-1}e_{16}=(e_5,0),
\]

where the first component is old and the second is new.  The old covector
\(e_{25}^*\) annihilates the old projection of the entire boundary space:

\[
e_{25}^*\,\operatorname{pr}_{\rm old}d_{-1}=0.
\]

But the specialized frozen evolution satisfies

\[
A_{104}^{(0)}e_5=-\frac{51}{2}e_{25}
                  +\frac{111}{4}e_{35},
\qquad
e_{25}^*A_{104}^{(0)}e_5=-\frac{51}{2}.
\]

If \(E\) were any chain endomorphism with old-old degree-zero compression
\(A_{104}^{(0)}\), then the old projection of
\(E_0d_{-1}e_{16}\) would be \(A_{104}^{(0)}e_5\), while the old projection
of \(d_{-1}E_{-1}e_{16}\) would lie in
\(\operatorname{pr}_{\rm old}\operatorname{im}d_{-1}\).  Applying
\(e_{25}^*\) gives \(-51/2=0\), a contradiction.  The argument eliminates
all new-row blocks of \(E\) without solving for them.

This closes only the serialized rational feasibility witness.  It is not a
no-go theorem for every 104-new-row non-cone differential.  The next solve
must impose nilpotence and \(A_{104}\)-equivariance simultaneously before
cyclicity, reality and the retained SDR are tested.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    witness = exact_witness()
    certificate = build()
    witness_text = json.dumps(witness, indent=2, sort_keys=True) + "\n"
    certificate_text = json.dumps(
        certificate, indent=2, sort_keys=True
    ) + "\n"
    if args.check:
        if PAYLOAD.read_text() != witness_text:
            raise AssertionError("boundary-cokernel witness drifted")
        if OUTPUT.read_text() != certificate_text:
            raise AssertionError("certificate drifted")
        if REPORT.read_text() != report_text():
            raise AssertionError("report drifted")
    else:
        _write(PAYLOAD, witness_text)
        _write(OUTPUT, certificate_text)
        _write(REPORT, report_text())
    schema = _load(SCHEMA)
    Draft202012Validator(schema).validate(certificate)
    if args.guards:
        mutated = json.loads(certificate_text)
        mutated["classification"][
            "all_104_row_noncone_differentials_obstructed"
        ] = True
        try:
            Draft202012Validator(schema).validate(mutated)
        except Exception:
            pass
        else:
            raise AssertionError("schema accepted global no-go promotion")
    print(f"{RESULT_ID}: PASS normalized_obstruction=-51/2")


if __name__ == "__main__":
    main()
