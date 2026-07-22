"""Independent semantic verifier for the Phase-3 boundary/flux contract."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


class VerificationError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise VerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _det2(matrix: list[list[str]]) -> Fraction:
    return Fraction(matrix[0][0]) * Fraction(matrix[1][1]) - Fraction(matrix[0][1]) * Fraction(matrix[1][0])


def verify_document(doc: dict[str, Any], *, verify_hashes: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    try:
        jsonschema.Draft202012Validator(schema).validate(doc)
    except jsonschema.ValidationError as exc:
        _fail(f"schema violation: {exc.message}")

    orientation = doc["action_derived_current"]["orientation"]
    if orientation["boundary_identity"] != "J_Hplus + J_Iplus - J_Hminus - J_Iminus = 0":
        _fail("oriented Stokes identity drift")
    if set(orientation["incoming"]) & set(orientation["outgoing"]):
        _fail("incoming and outgoing endpoint labels overlap")
    if set(orientation["incoming"] + orientation["outgoing"]) != {"Hplus", "Hminus", "Iplus", "Iminus"}:
        _fail("four-endpoint partition incomplete")

    flags = doc["claim_flags"]
    forbidden_true = [
        "global_endpoint_spaces_populated", "connection_matrix_constructed",
        "scattering_matrix_constructed", "flux_inertia_computed",
        "stability_or_CPT_established",
    ]
    if any(flags[name] for name in forbidden_true):
        _fail("contract overpromotes an unconstructed global object")
    if doc["phase2_application"]["global_channel_status"] != "UNPOPULATED_NOT_ZERO":
        _fail("absence of endpoint trace maps was converted into a zero channel count")

    control = doc["basis_invariance"]["independent_rational_control"]
    if Fraction(control["basis_determinant"]) == 0:
        _fail("singular basis mutation accepted")
    for stem in ("finite_dimension", "flux_rank", "quotient_dimension", "radical_dimension"):
        if control[f"{stem}_before"] != control[f"{stem}_after"]:
            _fail(f"basis invariant changed: {stem}")
    if _det2(control["J_prime"]) == 0 or control["flux_rank_after"] != 2:
        _fail("rational congruence control lost nondegeneracy")

    if doc["exceptional_strata"]["polar_Q21"]["not_a_second_wall"] is not True:
        _fail("single certified Q21 locus split into two walls")
    if "SEPARATE_STATIC_STRATUM" not in doc["exceptional_strata"]["omega_zero"]["disposition"]:
        _fail("omega=0 imported by continuity")

    if verify_hashes:
        for item in doc["input_snapshot"].values():
            path = ROOT / item["path"]
            if not path.is_file() or _sha256(path) != item["sha256"]:
                _fail(f"input snapshot drift: {item['path']}")

    limitations = " ".join(doc["does_not_establish"]).lower()
    for required in ("matching", "scattering", "stability", "cpt"):
        if required not in limitations:
            _fail(f"missing claim limitation: {required}")


def main() -> None:
    doc = json.loads(CERTIFICATE.read_text())
    verify_document(doc)
    print("PASS: independent Phase-3 boundary/flux contract verification")


if __name__ == "__main__":
    main()

