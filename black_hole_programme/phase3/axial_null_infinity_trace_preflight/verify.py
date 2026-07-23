"""Independent semantic verifier for the axial null-trace preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_matrix(rows: list[list[str]]) -> tuple[sp.Matrix, sp.Symbol]:
    omega = sp.Symbol("omega", real=True)
    return sp.Matrix([[sp.sympify(x, locals={"omega": omega, "I": sp.I}) for x in row]
                      for row in rows]), omega


def verify_document(doc: dict[str, Any], *, verify_hashes: bool = True) -> None:
    try:
        jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(doc)
    except jsonschema.ValidationError as exc:
        fail(f"schema violation: {exc.message}")

    J, omega = parse_matrix(doc["exact_radial_current"]["matrix_without_pi_alpha"])
    dagger = J.conjugate().T
    if any(sp.simplify((J + dagger)[i, j]) != 0 for i in range(6) for j in range(6)):
        fail("radial matrix lost anti-Hermiticity")
    expected_det = sp.Rational(195689447424, 15625) / (4 * omega**2 + 1)
    if sp.simplify(J.det() - expected_det) != 0:
        fail("radial determinant drift")

    permutation = doc["exact_radial_current"]["anchor_permutation"]
    H = (-sp.I * J).subs(omega, sp.Rational(1, 2)).extract(permutation, permutation)
    previous = sp.Integer(1)
    pivots = []
    for size in range(1, 7):
        minor = sp.factor(H[:size, :size].det())
        pivots.append(sp.factor(minor / previous))
        previous = minor
    recorded = [sp.sympify(x) for x in doc["exact_radial_current"]["anchor_ldl_pivots_without_pi_alpha"]]
    inertia = [sum(1 for x in pivots if x.is_positive),
               sum(1 for x in pivots if x.is_negative)]
    if pivots != recorded or inertia != [3, 3]:
        fail("Hermitian anchor inertia drift")

    polarizations = doc["endpoint_polarizations"]
    if set(polarizations["Iminus_incoming_rate_zero"]) & set(polarizations["Iplus_outgoing_rate_minus_2Iomega"]):
        fail("Iplus and Iminus trace polarizations overlap")
    if set(polarizations["Iminus_incoming_rate_zero"] + polarizations["Iplus_outgoing_rate_minus_2Iomega"]) != {
        "XI0", "XI1", "XI2", "XI3", "EI0", "EI2"
    }:
        fail("infinity endpoint polarization partition incomplete")
    if doc["current_and_topology_distinction"]["all_six_raw_test_disposition"] != "INVALID_ENDPOINT_MIXING":
        fail("raw Fv test was promoted to a null trace")

    flags = doc["claim_flags"]
    if any(flags[name] for name in (
        "wavepacket_trace_constructed", "global_connection_constructed",
        "scattering_channels_classified", "stability_or_CPT_established",
    )):
        fail("preflight overpromotes an unconstructed physical object")
    if doc["first_missing_estimate"]["status"] != "CERTIFIED_MISSING_DEPENDENCY":
        fail("missing wave-packet estimate hidden")

    if verify_hashes:
        for item in doc["imports"].values():
            path = ROOT / item["path"]
            if not path.is_file() or sha256(path) != item["sha256"]:
                fail(f"input drift: {item['path']}")

    limitations = " ".join(doc["does_not_establish"]).lower()
    for required in ("wave-packet", "matching", "scattering", "stability", "cpt"):
        if required not in limitations:
            fail(f"missing limitation: {required}")


def main() -> None:
    verify_document(json.loads(CERTIFICATE.read_text()))
    print("PASS: independent axial null-infinity trace preflight verification")


if __name__ == "__main__":
    main()
