#!/usr/bin/env python3
"""Independent verifier for the spin-two extension preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega")
I = sp.I


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-spin-two-scattering-extension-preflight-v1"
    ):
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("status") != "METHOD_SHORTFALL":
        errors.append("method shortfall was promoted")
    declaration = document["declaration"]
    if (declaration["time_phase"] != "exp(+I*omega*t)"
            or declaration["damped_QNM_half_plane"] != "Im(omega)>0"):
        errors.append("frequency convention drift")

    imports = {}
    for name, reference in document["imports"].items():
        path = ROOT / reference["path"]
        if not path.is_file() or sha256(path) != reference["sha256"]:
            errors.append(f"input hash drift: {name}")
            continue
        imports[name] = json.loads(path.read_text())
    if len(imports) != 3:
        return errors

    triangular = imports["triangular_factorization"]
    complete = imports["complete_reconstruction"]
    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    source = flow6[4:, :4]
    embedding = matrix(
        triangular["carrier_exact_sequence"]["RW_embedding_J"]
    )
    master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )
    extension = (master * source * embedding).applyfunc(
        lambda value: sp.cancel(sp.together(value))
    )
    recorded = matrix(document["exact_local_extension"]["matrix"])
    if any(not zero(extension[i, j] - recorded[i, j])
           for i in range(2) for j in range(2)):
        errors.append("exact local extension mismatch")
    if extension.rank() != 1 or not zero(extension.det()):
        errors.append("extension rank-one identity failed")

    rw = triangular["operators"]["L_RW"]
    a, b = parse(rw["a"]), parse(rw["b"])
    connection = sp.Matrix([[0, 1], [-b, -a]])
    derivative = connection.diff(W)
    recorded_derivative = matrix(
        document["exact_local_extension"]["spectral_derivative_matrix"]
    )
    if any(not zero(derivative[i, j] - recorded_derivative[i, j])
           for i in range(2) for j in range(2)):
        errors.append("spectral derivative mismatch")
    if document["exact_local_extension"][
        "pointwise_scalar_multiple_of_domega_A_RW"
    ]:
        errors.append("false pointwise derivative proportionality")

    q = sp.Symbol("q")
    residue = sp.factor(sp.residue(
        sp.trace(extension) - q * sp.trace(derivative), R, 2
    ))
    recorded_residue = parse(
        document["rational_gauge_trace_test"]["residue_at_r=2"]
    ).subs(sp.Symbol("q"), q)
    if not zero(residue - recorded_residue) or not zero(residue - 4 * I * q):
        errors.append("rational-gauge residue mismatch")
    if document["rational_gauge_trace_test"]["zero_residue_forces"] != [
        "q=0"
    ]:
        errors.append("rational q obstruction drift")
    antiderivative = parse(
        document["rational_gauge_trace_test"][
            "rational_antiderivative_of_trace_E"
        ]
    )
    if not zero(sp.diff(antiderivative, R) - sp.trace(extension)):
        errors.append("trace antiderivative mismatch")
    if "not the quotient class" not in document[
        "rational_gauge_trace_test"
    ]["relation_to_scattering_q"]:
        errors.append("operator/scattering q distinction lost")

    invariant = document["local_filtration_invariant"]
    if (invariant["class"] !=
            "[c] in O/(A_in_2), defined up to multiplication by a unit"
            or "c -> u*c+a*d" not in invariant["frame_law"]):
        errors.append("filtration invariant drift")

    congruence = document["spectral_derivative_congruence"]
    if congruence["existence_at_a_simple_zero"] != "TAUTOLOGICALLY_TRUE":
        errors.append("simple-zero quotient algebra drift")
    # Exact model of O/(a) for a simple a=u*delta+O(delta^2): both a and
    # delta generate the maximal ideal, while a' maps to the unit u.
    delta, unit, c0 = sp.symbols("delta unit c0", nonzero=True)
    a_local = unit * delta
    derivative_class = sp.diff(a_local, delta).subs(delta, 0)
    q_class = sp.cancel(c0 / derivative_class)
    if not zero(q_class * derivative_class - c0):
        errors.append("simple-zero derivative class is not invertible")
    if (congruence["physical_q_computed"]
            or congruence["smith_case_selected"]):
        errors.append("open scattering class was promoted")

    flags = document["claim_flags"]
    for name in (
        "exact_local_RW_to_RW_extension_extracted",
        "filtration_invariant_class_defined",
        "unquantified_simple_zero_congruence_is_tautological",
        "nonzero_rational_operator_derivative_coefficient_ruled_out",
    ):
        if flags[name] is not True:
            errors.append(f"proved flag demoted: {name}")
    for name in (
        "scattering_extension_coefficient_c_computed",
        "Fredholm_pairing_computed",
        "spectral_derivative_q_nonzero_certified",
        "simple_QNM_Smith_case_selected",
    ):
        if flags[name] is not False:
            errors.append(f"open flag promoted: {name}")
    missing = set(document["jost_data_audit"]["missing"])
    if not any("adjoint QNM" in item for item in missing):
        errors.append("adjoint-QNM dependency omitted")
    if not any("Fredholm pairing" in item for item in missing):
        errors.append("Fredholm-pairing dependency omitted")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    found = verify()
    if found:
        for error in found:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print("verified=true status=METHOD_SHORTFALL exact_local_extension=true")
