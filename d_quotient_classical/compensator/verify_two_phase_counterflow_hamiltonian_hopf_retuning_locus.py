#!/usr/bin/env python3
"""Independent consumer for the counterflow retuning-locus no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json"
SCHEMA = ROOT / "d_quotient_classical/compensator/schema/two-phase-counterflow-hamiltonian-hopf-retuning-locus-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/compensator/schema/two-phase-counterflow-hamiltonian-hopf-retuning-locus-payload-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    payload = json.loads(PAYLOAD.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    Draft202012Validator(json.loads(PAYLOAD_SCHEMA.read_text())).validate(payload)
    if payload["content_sha256"] != _digest({key: value for key, value in payload.items() if key != "content_sha256"}):
        raise AssertionError("payload content digest failed")
    if certificate["payload_ref"]["sha256"] != _sha(PAYLOAD):
        raise AssertionError("payload byte digest failed")
    for record in certificate["imports"].values():
        path = ROOT / record["path"]
        if _sha(path) != record["sha256"] or json.loads(path.read_text()).get("result_id") != record["result_id"]:
            raise AssertionError("import drifted")

    q, x, energy, alpha_b, m2, v0, w, z, t = sp.symbols("q x C alpha_B M2 V0 w z t")
    b0 = (1 - q) ** 2 * x**2 / 6
    b1 = (1 - q) * (1 - 3 * q) * x**2 / 6
    b2 = (1 - q) * (5 * q - 1) * x**2 / 6
    scalar = (4 - q) * x / 2
    stationary = {
        alpha_b: 2 * energy / (q * x**2),
        m2: 2 * energy * (4 * q - 1) / (3 * q * x),
        v0: -energy * (q**2 - 5 * q + 1) / (3 * q),
    }
    equations = [
        alpha_b * b0 + m2 * scalar / 2 - energy / 2 - v0,
        alpha_b * b1 - m2 * q * x / 4 - energy / 2 + v0,
        alpha_b * b2 + m2 * (3 * q - 4) * x / 4 - energy / 2 + v0,
    ]
    if any(sp.factor(row.subs(stationary)) != 0 for row in equations):
        raise AssertionError("stationary family does not solve the action equations")

    factors = [sp.sympify(row["polynomial"], locals={"q": q, "w": w}) for row in payload["physical_quotient"]["factors"]]
    f2_discriminant = sp.factor(sp.discriminant(factors[1], w))
    if f2_discriminant != 256 * q**5 * (9 * q - 8):
        raise AssertionError("F2 discriminant drifted")
    if sp.Poly(f2_discriminant, q).count_roots(sp.Rational(3, 20), sp.Rational(1, 4)) != 0 or sp.sign(f2_discriminant.subs(q, sp.Rational(1, 5))) != -1:
        raise AssertionError("F2 sign certificate failed")

    matrix_record = payload["physical_quotient"]["physical_matrix"]
    if matrix_record["sha256"] != _digest({"shape": matrix_record["shape"], "entries": matrix_record["entries"]}):
        raise AssertionError("physical matrix digest failed")
    matrix = sp.zeros(*matrix_record["shape"])
    for row, column, raw in matrix_record["entries"]:
        matrix[row, column] = sp.sympify(raw, locals={"t": t, "z": z})
    determinant = sp.factor(sp.cancel(matrix.det(method="domain-ge")))
    divisor = sp.prod(value.subs({q: t**2, w: z**2}) ** 2 for value in factors)
    if sp.factor(determinant / divisor - determinant.subs(z, 0) / divisor.subs(z, 0)) != 0:
        raise AssertionError("stored matrix does not have the declared divisor")

    resultants = payload["spectral_classification"]["resultants"]
    expected_counts = {"R12": 0, "R13": 0, "R14": 1, "R23": 0, "R24": 0, "R34": 2}
    for left in range(4):
        for right in range(left + 1, 4):
            key = f"R{left + 1}{right + 1}"
            actual = sp.factor(sp.resultant(factors[left], factors[right], w))
            stored = sp.sympify(resultants[key]["polynomial"], locals={"q": q})
            if sp.factor(actual - stored) != 0 or sp.Poly(actual, q).count_roots(sp.Rational(3, 20), sp.Rational(1, 4)) != expected_counts[key]:
                raise AssertionError(f"resultant audit failed for {key}")

    residue = payload["unstable_residue_pairing"]
    numerator = sp.sympify(residue["N_q_w"], locals={"q": q, "w": w})
    residue_resultant = sp.factor(sp.resultant(factors[1], numerator, w))
    if sp.factor(residue_resultant - sp.sympify(residue["resultant_F2_N"], locals={"q": q})) != 0:
        raise AssertionError("residue resultant drifted")
    if sp.Poly(residue_resultant, q).count_roots(sp.Rational(3, 20), sp.Rational(1, 4)) != 0:
        raise AssertionError("residue exceptional point entered the component")
    if payload["unstable_energy_signature"]["two_copy_inertia_positive_negative_zero"] != [4, 4, 0]:
        raise AssertionError("energy signature drifted")
    if certificate["terminal_verdict"]["stable_exact_retuned_fixture"] is not None:
        raise AssertionError("a stable fixture was silently promoted")
    print("TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_V1_INDEPENDENT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
