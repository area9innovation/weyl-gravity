#!/usr/bin/env python3
"""Independent verifier for the parameter-deformation cohomology audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
R, W, M = sp.symbols("r omega M", nonzero=True)
QW, QM = sp.symbols("q_omega q_M")
I = sp.I


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(
        value,
        locals={"r": R, "omega": W, "M": M, "I": I},
    )


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def zero(value: sp.Expr) -> bool:
    return sp.cancel(sp.together(value)) == 0


def matrix_zero(value: sp.Matrix) -> bool:
    return all(zero(entry) for entry in value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def residue_at_infinity(value: sp.Expr) -> sp.Expr:
    z = sp.Symbol("z")
    return sp.factor(
        -sp.residue(value.subs(R, 1 / z) / z**2, z, 0)
    )


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-qnm-parameter-deformation-cohomology-v1"
    ):
        errors.append("schema drift")
    if document.get("status") != "PARAMETER_SHORTCUT_REFUSED":
        errors.append("status was promoted or changed")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
    ]:
        errors.append("dependency boundary drift")

    imports = {}
    for name, reference in document.get("imports", {}).items():
        path = ROOT / reference["path"]
        if not path.is_file() or sha256(path) != reference["sha256"]:
            errors.append(f"input hash drift: {name}")
            continue
        imports[name] = json.loads(path.read_text())
    if len(imports) != 3:
        return errors

    triangular = imports["triangular_factorization"]
    complete = imports["complete_reconstruction"]
    extension_preflight = imports["extension_preflight"]
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
    if not matrix_zero(
        extension
        - matrix(extension_preflight["exact_local_extension"]["matrix"])
    ):
        errors.append("authoritative extension import mismatch")
    if not matrix_zero(extension - matrix(document["extension"]["matrix"])):
        errors.append("recorded extension mismatch")
    if extension.rank() != 1:
        errors.append("extension rank drift")

    # Independent reconstruction of the M-family.
    f = 1 - 2 * M / R
    potential = f * (6 / R**2 - 6 * M / R**3)
    scalar_a = sp.cancel(sp.diff(f, R) / f + 2 * I * W / f)
    scalar_b = sp.cancel(-potential / f**2)
    connection_m = sp.Matrix(
        [[0, 1], [-scalar_b, -scalar_a]]
    ).applyfunc(lambda value: sp.cancel(sp.together(value)))
    if not matrix_zero(
        connection_m
        - matrix(document["mass_family_derivation"]["companion_A_M"])
    ):
        errors.append("M-dependent companion drift")

    connection = connection_m.subs(M, 1).applyfunc(sp.cancel)
    d_omega = connection_m.diff(W).subs(M, 1).applyfunc(sp.cancel)
    d_mass = connection_m.diff(M).subs(M, 1).applyfunc(sp.cancel)
    candidate = extension - QW * d_omega - QM * d_mass
    trace_candidate = sp.cancel(sp.trace(candidate))
    residues = {
        "r=0": sp.residue(trace_candidate, R, 0),
        "r=2": sp.residue(trace_candidate, R, 2),
        "r=2*I/omega": sp.residue(
            trace_candidate, R, 2 * I / W
        ),
        "r=infinity": residue_at_infinity(trace_candidate),
    }
    recorded_residues = document["trace_residue_audit"]["residues"]
    for name, value in residues.items():
        if not zero(value - parse(recorded_residues[name])):
            errors.append(f"residue drift: {name}")
    relation = QW + W * QM
    if not zero(residues["r=2"] - 4 * I * relation):
        errors.append("horizon relation drift")
    if not zero(residues["r=infinity"] + 4 * I * relation):
        errors.append("infinity relation drift")
    if document["trace_residue_audit"]["necessary_relation"] != (
        "q_omega+omega*q_M=0"
    ):
        errors.append("necessary coefficient relation drift")

    scale_gauge = -R * connection - sp.diag(0, 1)
    coboundary = (
        scale_gauge.diff(R)
        + scale_gauge * connection
        - connection * scale_gauge
    )
    if not matrix_zero(coboundary - (d_mass - W * d_omega)):
        errors.append("scale coboundary identity failed")
    if not matrix_zero(
        scale_gauge - matrix(document["scale_coboundary"]["gauge_B_scale"])
    ):
        errors.append("recorded scale gauge drift")

    X, OMEGA = sp.symbols("x Omega", nonzero=True)
    dimensionless_a = sp.cancel(
        M * scalar_a.subs({R: M * X, W: OMEGA / M})
    )
    dimensionless_b = sp.cancel(
        M**2 * scalar_b.subs({R: M * X, W: OMEGA / M})
    )
    if sp.diff(dimensionless_a, M) or sp.diff(dimensionless_b, M):
        errors.append("dimensionless scaling still depends on M")

    conclusion = document["cohomology_conclusion"]
    if conclusion["parameter_span_dimension"] != 1:
        errors.append("parameter span dimension drift")
    if not conclusion["admissible_candidate_combination_is_exact"]:
        errors.append("exact scaling combination was demoted")
    if conclusion["pure_E_RW_coboundary_status"] != "NOT_DECIDED":
        errors.append("pure extension coboundary was overclaimed")

    refusals = document["scope_refusals"]
    if not refusals["Lambda"].startswith("UNDEFINED:"):
        errors.append("undefined Lambda derivative was admitted")
    if not refusals["ell"].startswith("REFUSED_AS_PHYSICAL_PARAMETER:"):
        errors.append("discrete ell derivative was admitted")

    flags = document["claim_flags"]
    for name in (
        "dimensionful_mass_family_derived",
        "trace_residue_constraint_certified",
        "mass_scaling_combination_rationally_exact",
    ):
        if flags[name] is not True:
            errors.append(f"certified flag demoted: {name}")
    for name in (
        "mass_adds_independent_deformation_class",
        "pure_E_RW_coboundary_decided",
        "beta_n_computed",
        "QNM_Smith_type_selected",
    ):
        if flags[name] is not False:
            errors.append(f"open or negative flag promoted: {name}")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    found = verify()
    if found:
        for error in found:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print(
        "verified=true parameter_shortcut_refused=true "
        "pure_E_RW_coboundary=NOT_DECIDED beta_n_computed=false"
    )
