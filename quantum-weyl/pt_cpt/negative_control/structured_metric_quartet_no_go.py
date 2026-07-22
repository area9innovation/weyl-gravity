#!/usr/bin/env python3
"""Build the structured-metric contract and counterflow quartet no-go.

This is a finite exact preflight.  It separates a positive pseudo-Hermitian
metric from a Mannheim C operator, corrects the BRST compatibility gate, and
uses the frozen j=1/2 counterflow Smith sector as a broken-PT negative control.
It does not construct a state, a field-theoretic C operator, or unitarity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json"
SCHEMA = HERE / "schema/structured-metric-quartet-no-go-v1.schema.json"

INPUTS = {
    "selected_jhalf": {
        "path": ROOT
        / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1.json",
        "sha256": "43595d6e974dd3ff852db658014fb34dcd1521f050a752e5732fb0c3b5f27797",
        "result_id": "TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_FIRST_GENERIC_ISOTYPICAL_HEALTH_OBSTRUCTION_PAYLOAD_V1",
    },
    "healthy_family": {
        "path": ROOT
        / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1.json",
        "sha256": "88e5f9a25ff3a5cfbbdbbbe1492ec879f6bfb1f495aed3aa4241b8e58e413508",
        "result_id": "TWO_PHASE_COUNTERFLOW_HAMILTONIAN_HOPF_RETUNING_LOCUS_PAYLOAD_V1",
    },
    "retained_operator": {
        "path": ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json",
        "sha256": "296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77",
        "result_id": "BERGER_RETAINED_MINIMAL_OPERATOR",
    },
}

Z = sp.symbols("z")
Q = sp.symbols("q", positive=True, real=True)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _expr(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(value))


def _matrix(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[_expr(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    refs: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, spec in INPUTS.items():
        path = spec["path"]
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != spec["sha256"] or value.get("result_id") != spec["result_id"]:
            raise AssertionError(f"{role} frozen input drifted")
        refs[role] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": actual,
            "result_id": spec["result_id"],
            "input_commit": "4a212883aefa5525cc847d0c12763c74c1c3411a",
        }
        values[role] = value
    retained_ref = values["selected_jhalf"]["imports"]["retained_operator"]
    if (
        retained_ref["sha256"] != INPUTS["retained_operator"]["sha256"]
        or retained_ref["result_id"] != INPUTS["retained_operator"]["result_id"]
    ):
        raise AssertionError("selected physical quotient lost its retained-operator pin")
    return refs, values


def _structured_contract() -> dict[str, Any]:
    return {
        "eta_candidate_required_data": {
            "declared_carrier_basis_and_adjoint": True,
            "exact_Hermitian_matrix_or_operator": True,
            "strict_positivity_certificate": "exact LDL/congruence, principal-minor, sum-of-squares, or equivalent exact proof; numerical eigenvalues are not accepted",
            "pseudo_Hermiticity": "H^dagger*eta=eta*H on a declared invariant domain",
            "invariant_commutant_membership": "eta commutes with every declared spatial/internal symmetry generator",
            "real_structure": "for r(v)=R*conjugate(v), require R*conjugate(R)=1 and R^dagger*eta*R=conjugate(eta)",
            "momentum_frequency_compatibility": "opposite momentum/frequency blocks are related by the declared real-field involution, not fitted independently",
            "parameter_regularness": "eta and eta inverse are nonsingular on the entire declared parameter locus; singular limiting metrics are separate strata",
            "causal_covariance_gate": "a field-theoretic promotion additionally verifies the CCR under the new adjoint and the declared wavefront/support properties",
        },
        "C_operator_additional_required_data": {
            "eta_is_not_C_by_definition": True,
            "involution": "C^2=1",
            "dynamics": "[C,H]=0",
            "PT_relation": "P and the anti-linear T are independently declared; [C,PT]=0 and the convention relating eta, P, and C is proved",
            "symmetry_real_and_sector_compatibility": True,
            "BRST_chain_map": "C_(n+1)*Q_n=Q_n*C_n in every degree, including any nontrivial ghost action",
        },
        "BRST_compatibility": {
            "rejected_gate": "Q^dagger*eta=eta*Q with eta>0 on a nonzero nilpotent BRST complex",
            "rejection_reason": "positive-metric self-adjointness plus Q^2=0 forces ||Qv||_eta^2=<v,Q^2v>_eta=0 for every v, hence Q=0",
            "accepted_chain_gate": "C preserves ker(Q) and im(Q), preferably by an explicit graded chain map; this induces C on H^0(Q)",
            "accepted_cohomology_gate": "supply explicit pi and i with pi*i=1, Q*i=0, pi*Q=0 (or a proved Hodge representative), then prove positivity of i^dagger*eta*i on H^0(Q)",
            "exact_states_not_positive_null_vectors": "a strictly positive metric has no nonzero null vectors, so exact states are removed by cohomology rather than declared null",
            "full_complex_pairing": "an indefinite BV/Krein pairing may remain on the nonphysical complex; positivity is a separate cohomology statement",
        },
        "forbidden_shortcuts": [
            "manufacture eta by diagonalizing each finite matrix independently",
            "call a positive eta a C operator without C^2=1 and the declared P/T relation",
            "infer a field-theoretic state or unitarity theorem from a finite reduced block",
            "replace chain-map/cohomology descent by positive-metric BRST self-adjointness",
        ],
    }


def _nilpotent_theorem() -> dict[str, Any]:
    nilpotent_fixture = sp.Matrix([[0, 1], [0, 0]])
    if nilpotent_fixture**2 != sp.zeros(2) or nilpotent_fixture == sp.zeros(2):
        raise AssertionError("nilpotent fixture drifted")
    return {
        "theorem": "If eta is strictly positive Hermitian, Q^2=0, and Q^dagger*eta=eta*Q, then Q=0.",
        "proof_identity": "||Qv||_eta^2=<Qv,Qv>_eta=<v,Q^2v>_eta=0",
        "strict_positivity_step": "||Qv||_eta=0 implies Qv=0 for every v",
        "nonzero_nilpotent_fixture_Q": _matrix(nilpotent_fixture),
        "fixture_square": _matrix(nilpotent_fixture**2),
        "nontrivial_BRST_positive_self_adjoint_gate_feasible": False,
    }


def _selected_negative_control(selected: dict[str, Any]) -> dict[str, Any]:
    unstable = selected["unstable_sector"]
    if unstable["local_Smith_sector"] != "two copies of 40*D^4+773*D^2+3748":
        raise AssertionError("selected Smith sector drifted")
    a = sp.Integer(unstable["principal_time_order_four_matrix"][0][0])
    b = sp.Integer(unstable["time_order_two_matrix"][0][0])
    c = sp.Integer(unstable["fixed_isotype_spatial_potential_matrix"][0][0])
    factor = a * Z**4 + b * Z**2 + c
    source_factor = sp.sympify(
        selected["terminal_verdict"]["complex_frequency_factor"].replace("^", "**"),
        locals={"z": Z},
    )
    if sp.expand(factor - source_factor) != 0:
        raise AssertionError("selected characteristic factor drifted")
    complete_characteristic = sp.sympify(
        selected["physical_quotient"]["characteristic_determinant_monic"],
        locals={"z": Z},
    )
    if sp.rem(sp.Poly(complete_characteristic, Z), sp.Poly(factor**2, Z)) != 0:
        raise AssertionError("quartet factor lost multiplicity two in the physical Hessian")

    companion = sp.Matrix(
        [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [-c / a, 0, -b / a, 0],
        ]
    )
    schrodinger = sp.I * companion
    characteristic = sp.factor((Z * sp.eye(4) - companion).det())
    if sp.factor(a * characteristic - factor) != 0:
        raise AssertionError("companion characteristic polynomial mismatch")
    discriminant = sp.factor(b**2 - 4 * a * c)
    if discriminant != -sp.Integer(2151):
        raise AssertionError("quartet discriminant drifted")
    y_roots = [(-b + 3 * sp.I * sp.sqrt(239)) / (2 * a), (-b - 3 * sp.I * sp.sqrt(239)) / (2 * a)]
    if any(sp.simplify(a * root**2 + b * root + c) != 0 for root in y_roots):
        raise AssertionError("exact y roots failed")

    return {
        "source_sector": unstable["local_Smith_sector"],
        "source_physical_H_sha256": selected["physical_quotient"]["maps"]["physical_H"]["sha256"],
        "source_complete_characteristic_determinant_monic": selected["physical_quotient"]["characteristic_determinant_monic"],
        "multiplicity": "two identical physical polarizations; one companion block is displayed",
        "coefficient_domain": "Q(i,sqrt(239))",
        "scalar_operator_coefficients": {"D4": str(a), "D2": str(b), "D0": str(c)},
        "real_companion_generator_A": _matrix(companion),
        "Schrodinger_generator_H_equals_iA": _matrix(schrodinger),
        "characteristic_polynomial_A_monic": _expr(characteristic),
        "source_characteristic_factor": _expr(factor),
        "y_equals_z_squared_discriminant": str(discriminant),
        "y_roots": [_expr(root) for root in y_roots],
        "root_class": "HAMILTONIAN_HOPF_QUARTET_NONZERO_REAL_AND_IMAGINARY_PARTS",
        "spectral_infeasibility_theorem": "eta>0 and H^dagger*eta=eta*H would make every H eigenvalue real; H=iA has nonreal eigenvalues because every A root z has nonzero real part",
        "positive_eta_feasible": False,
        "C_operator_claimed": False,
        "broken_PT_negative_control": True,
        "norm_only_rescue_possible": False,
    }


def _family_negative_control(family: dict[str, Any]) -> dict[str, Any]:
    q = Q
    a = 16 * q**2
    b = 24 * q * (3 - 2 * q**2)
    c = 32 * q**3 - 108 * q**2 + 81
    discriminant = sp.factor(b**2 - 4 * a * c)
    if discriminant != 256 * q**5 * (9 * q - 8):
        raise AssertionError("family discriminant identity failed")
    imported = family["terminal_verdict"]
    if imported["structural_reason"] != "disc_w(F2)=256*q^5*(9*q-8)<0 for every 0<q<1/4":
        raise AssertionError("family spectral reason drifted")
    return {
        "parameter": "q",
        "trace_healthy_component": family["parameter_family"]["causal_trace_healthy_component"]["conditions"],
        "F2_coefficients_in_w": {"w2": _expr(a), "w1": _expr(b), "w0": _expr(c)},
        "discriminant": _expr(discriminant),
        "exact_sign_reason": "q>0 and q<1/4 imply q^5>0 and 9*q-8<0",
        "positive_eta_feasible_everywhere_on_component": False,
        "familywide_causal_or_quantum_promotion": False,
    }


def build() -> dict[str, Any]:
    refs, values = _load_inputs()
    certificate = {
        "$schema": "../schema/structured-metric-quartet-no-go-v1.schema.json",
        "schema": "pure-weyl-structured-metric-quartet-no-go-v1",
        "result_id": "STRUCTURED_METRIC_QUARTET_NO_GO_V1",
        "result_state": "STRUCTURED_METRIC_CONTRACT_FIXED_AND_COUNTERFLOW_POSITIVE_ETA_INFEASIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "same-field two-phase counterflow changed theory, used only as a negative control",
            "background": "selected Berger j=1/2 all-k physical Smith sector and its trace-healthy stationary family",
            "carrier": "one exact four-dimensional companion block, occurring twice in the physical quotient",
            "coefficient_domain": "exact rational/algebraic arithmetic",
            "claim_level": "finite structured pseudo-Hermitian feasibility preflight",
        },
        "source_refs": refs,
        "structured_metric_contract": _structured_contract(),
        "nilpotent_positive_metric_no_go": _nilpotent_theorem(),
        "selected_counterflow_negative_control": _selected_negative_control(values["selected_jhalf"]),
        "family_counterflow_negative_control": _family_negative_control(values["healthy_family"]),
        "decision": {
            "positive_eta_on_selected_quartet": "EXACTLY_INFEASIBLE",
            "positive_eta_on_trace_healthy_family": "EXACTLY_INFEASIBLE",
            "BRST_positive_metric_self_adjointness_gate": "REJECTED_AS_TRIVIALIZING_Q",
            "replacement_BRST_gate": "CHAIN_MAP_PLUS_EXPLICIT_COHOMOLOGY_DESCENT",
            "Mannheim_C_operator": "NOT_CONSTRUCTED",
            "field_theoretic_state_or_unitarity": "NOT_ESTABLISHED",
        },
        "mutation_expectations": {
            "real_spectrum_reclassification": "REJECT",
            "positive_eta_on_quartet": "REJECT",
            "norm_only_rescue": "REJECT",
            "nonzero_nilpotent_positive_self_adjoint_Q": "REJECT",
            "eta_called_C_without_involution": "REJECT",
            "finite_block_promoted_to_unitarity": "REJECT",
        },
        "claim_boundary": {
            "establishes": [
                "the exact admissibility contract for eta, C, real structure, sector compatibility and BRST cohomology descent",
                "the general positive-metric self-adjoint nilpotent no-go",
                "an exact companion realization of the frozen counterflow quartic",
                "spectral infeasibility of every positive pseudo-Hermitian eta on the selected quartet and the declared trace-healthy family",
            ],
            "does_not_establish": [
                "a Mannheim C operator on any strict-Weyl block",
                "a full-BV state, Hadamard covariance, particle interpretation, scattering theory or unitarity",
                "an anomaly or QME statement",
                "a no-go for PT/CPT quantization of pure conformal gravity",
            ],
        },
        "provenance": {
            "generator": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha(Path(__file__)),
            "independent_verifier": "quantum-weyl/pt_cpt/negative_control/verify_structured_metric_quartet_no_go.py",
            "exact_engine": "SymPy rational/algebraic matrices; no floating-point decisions",
        },
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = _dump(build())
    if args.write:
        OUTPUT.write_bytes(encoded)
    elif not OUTPUT.exists() or OUTPUT.read_bytes() != encoded:
        raise SystemExit(f"STALE: {OUTPUT.relative_to(ROOT)}")
    print("STRUCTURED_METRIC_QUARTET_NO_GO_V1: PASS")


if __name__ == "__main__":
    main()
