#!/usr/bin/env python3
"""Transport the scoped C-G4 phase plane to the two detector memories."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA.json"
SCHEMA = PACKAGE / "schema/berger-cg4-two-record-poisson-algebra-v1.schema.json"
REPORT = PACKAGE / "reports/berger-cg4-two-record-poisson-algebra.md"
DEPENDENCIES = {
    "observer_morphism": PACKAGE / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json",
    "detector_transfer": PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
    "cg4": ROOT / "d_quotient_classical/certificates/BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_cg4_record_poisson_algebra.py",
    "tests": PACKAGE / "tests/test_berger_cg4_record_poisson_algebra.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def algebra_audit(*, clone_detector_polarization: bool = False) -> dict[str, Any]:
    beta = 2 * sp.sqrt(10) / 3
    S0, C0, S1, C1 = sp.symbols("S_0 C_0 S_1 C_1", real=True)
    if clone_detector_polarization:
        matrix = beta * sp.Matrix([[-S0, -C0], [-S0, -C0]])
    else:
        matrix = beta * sp.Matrix([[-S0, -C0], [C1, -S1]])
    determinant = sp.factor(matrix.det())
    expected = sp.factor(beta**2 * (S0 * S1 + C0 * C1))
    if not clone_detector_polarization and sp.simplify(determinant - expected) != 0:
        raise AssertionError("C-G4 detector determinant formula failed")

    # Point-supported specialization is used only as an independent exact
    # coefficient fixture.  Positivity for the actual smooth windows is the
    # uniform double-integral bound recorded below.
    t0, t1 = sp.Rational(1, 4), sp.Rational(1, 2)
    point_subs = {S0: sp.sin(beta * t0), C0: sp.cos(beta * t0), S1: sp.sin(beta * t1), C1: sp.cos(beta * t1)}
    point_det = sp.trigsimp(determinant.subs(point_subs))
    point_expected = sp.trigsimp(beta**2 * sp.cos(beta * (t0 - t1)))
    if not clone_detector_polarization and sp.trigsimp(point_det - point_expected) != 0:
        raise AssertionError("point detector determinant specialization failed")

    bracket_xy = -sp.Rational(1, 32) / sp.pi**2
    bracket_records = sp.factor(determinant * bracket_xy)
    m0, m1 = sp.symbols("m_0 m_1")
    if clone_detector_polarization:
        inverse_coordinates = None
        hamiltonian = None
    else:
        inverse = sp.simplify(matrix.inv())
        coordinates = inverse * sp.Matrix([m0, m1])
        hamiltonian = sp.factor(128 * sp.sqrt(10) * sp.pi**2 * (coordinates.dot(coordinates)) / 9)
        inverse_coordinates = [sp.sstr(value) for value in coordinates]
        # The transported constant bracket must reproduce the C-G4 bracket.
        Jm = sp.Matrix([[0, bracket_records], [-bracket_records, 0]])
        reproduced = sp.simplify((inverse * Jm * inverse.T)[0, 1])
        if sp.simplify(reproduced - bracket_xy) != 0:
            raise AssertionError("transported record Poisson bracket failed")
    return {
        "beta": sp.sstr(beta),
        "moment_definitions": {
            "S_a": "integral rho_a(t,R) sin(beta t) dvol_gHat",
            "C_a": "integral rho_a(t,R) cos(beta t) dvol_gHat",
        },
        "basis_map_N": [[sp.sstr(value) for value in matrix.row(i)] for i in range(2)],
        "determinant": sp.sstr(determinant),
        "point_specialization_determinant": sp.sstr(point_det),
        "rank": matrix.rank(),
        "inverse_coordinates_x_y": inverse_coordinates,
        "record_bracket": sp.sstr(bracket_records),
        "relational_hamiltonian_in_records": None if hamiltonian is None else sp.sstr(hamiltonian),
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["observer_morphism"]["flags"]["COEFFICIENTWISE_OBSERVER_EVALUATION_MORPHISM_CERTIFIED"] is not True:
        raise AssertionError("observer morphism input drifted")
    if values["detector_transfer"]["transfer_matrix"]["rank"] != 2:
        raise AssertionError("detector transfer input drifted")
    for flag in ("BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE", "BERGER_CLOCK_LIFTED_REDUCED_BRACKET"):
        if values["cg4"]["flags"][flag] is not True:
            raise AssertionError(f"C-G4 input drifted: {flag}")
    audit = algebra_audit()
    clone = algebra_audit(clone_detector_polarization=True)
    if clone["rank"] != 1:
        raise AssertionError("cloned-polarization mutation escaped")

    max_difference = sp.Rational(7, 24)
    beta = 2 * sp.sqrt(10) / 3
    phase_bound = sp.simplify(beta * max_difference)
    if not (phase_bound < sp.Rational(7, 9) < sp.Rational(3, 2)):
        raise AssertionError("detector phase bound failed")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL result imports the scoped C-G4 retarded two-phase Maxwell observable and evaluates its circular phase basis with the two certified clock-labelled detector polarizations. The resulting moment matrix N has determinant beta^2(S0 S1+C0 C1), a strictly positive double average of cos(beta(t0-t1)) on the actual detector windows. It therefore identifies the C-G4 (x,y) plane with the two persistent memories. Transporting {x,y}=-1/(32 pi^2) gives a nonzero constant record bracket and makes every C-G4 quadrature and the quadratic relational Hamiltonian an element of the localized polynomial record algebra. This certifies multiplicative and Poisson closure for the scoped two-phase, coefficientwise affine-K family. It does not construct the full apparatus Dirac bracket outside that plane, a complete harmonic signal algebra, full q4 or higher brackets, fixed-background linear-K descent, finite-r Green hyperbolicity, localized emitter worldtubes, recoil, a quantum state, or any quantum claim."
    )
    return {
        "schema": "closed-universe-berger-cg4-two-record-poisson-algebra-v1",
        "result_id": "BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA",
        "setting_id": values["observer_morphism"]["setting_id"],
        "claim_status": "CERTIFIED_SCOPED_TWO_RECORD_CLASSICAL_POISSON_ALGEBRA",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "detector_window_positivity": {
            "physical_time_windows": [["11/48", "13/48"], ["23/48", "25/48"]],
            "maximum_pairwise_time_difference": "7/24",
            "maximum_phase_difference": sp.sstr(phase_bound),
            "exact_bound_chain": "beta*7/24=7*sqrt(10)/36 < 7/9 < 3/2 < pi/2",
            "determinant_integral": "det N=beta^2 double_integral rho_0(t)rho_1(s) cos(beta(t-s)) dt ds > 0",
            "strictly_positive": True,
        },
        "phase_plane_to_records": audit,
        "record_algebra": {
            "coefficient_ring": "Q(sqrt(10),pi,S0,C0,S1,C1,Delta^-1)[[r,kappa]] with Delta=det N",
            "algebra": "A_Ob,C-G4=coefficient_ring[m_0,m_1]",
            "multiplication": "ordinary commutative product of persistent gauge-invariant memory functionals",
            "poisson_rule": "{f,g}_Ob={m0,m1}(partial_m0 f partial_m1 g-partial_m1 f partial_m0 g)",
            "quadrature_embedding": "Q(tau),P(tau) are linear polynomials after substituting the certified inverse x(m),y(m)",
            "redshift_embedding": "the C-G4 energy/redshift reading is quadratic in x,y and hence quadratic in m0,m1 after the same inverse",
            "product_closed": True,
            "poisson_closed": True,
            "record_bracket_nonzero": True,
        },
        "mutation_results": [{"name": "clone_detector_polarization", "observed_rank": clone["rank"], "expected_rank": 1, "detected": True}],
        "flags": {
            "CG4_PHASE_PLANE_TO_TWO_RECORDS_ISOMORPHISM_CERTIFIED": True,
            "TWO_RECORD_MULTIPLICATIVE_ALGEBRA_CERTIFIED": True,
            "TWO_RECORD_POISSON_ALGEBRA_CERTIFIED": True,
            "CG4_QUADRATURES_AND_REDSHIFT_EMBEDDED": True,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "COMPLETE_HARMONIC_SIGNAL_ALGEBRA_CERTIFIED": False,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_TWO_SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES_AND_RECOMPUTE_THE_RANK_TWO_RECORD_MATRIX_OR_RETURN_THE_EXACT_COMPACT_CAUSAL_OBSTRUCTION",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale C-G4 record Poisson algebra certificate")
    print("BERGER_CG4_TWO_RECORD_POISSON_ALGEBRA generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
