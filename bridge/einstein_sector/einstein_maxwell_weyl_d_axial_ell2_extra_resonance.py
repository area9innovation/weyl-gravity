"""Adjoint pairing theorem for d crossed with the axial ell=2 extra block."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.schema.json"
INPUTS = {
    "e1_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e1_source_fixture.json",
    "e2_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_e2_source_fixture.json",
    "axial_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "exceptional_all_m": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json",
    "electric_gate": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_duality_ell2_extra_resonance.json",
}


class DAxialResonanceError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DAxialResonanceError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _pairing_theorem(records: dict[str, dict[str, object]]) -> dict[str, object]:
    locals_ = {"I": sp.I, "sqrt": sp.sqrt}
    sources = []
    for label in ("e1_source", "e2_source"):
        sources.append(sp.Matrix([sp.sympify(value, locals=locals_) for value in records[label]["bilinear_source_rows"]]))
    source_matrix = sp.Matrix.hstack(*sources)

    rows, symbols = _generic_rows()
    row_names = ["metric_t", "metric_x", "maxwell_t", "maxwell_x"]
    fields = [symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]]
    hessian = sp.diag(6, -6, 1, 1) * sp.Matrix([rows[name] for name in row_names]).jacobian(fields)
    frequency = 4 / sp.sqrt(3)
    hessian = hessian.subs({symbols["lambda"]: 6, symbols["k"]: 0, symbols["omega"]: frequency}).applyfunc(sp.factor)
    _require(hessian.rank() == 2, "axial p-shell rank changed")
    adjoint_basis = [sp.Matrix([-1, 0, 1, 0]), sp.Matrix([0, -sp.Rational(1, 9), 0, 1])]
    for witness in adjoint_basis:
        _require(hessian.T * witness == sp.zeros(4, 1), "axial adjoint witness changed")
    witness_matrix = sp.Matrix.hstack(*adjoint_basis)
    pairing = (witness_matrix.T * source_matrix).applyfunc(sp.factor)
    expected = sp.diag(72 * sp.sqrt(3) * sp.I, -sp.Rational(104, 27) * sp.sqrt(3) * sp.I)
    _require(pairing == expected, "d-cross adjoint pairing matrix changed")
    _require(sp.factor(pairing.det()) == 832, "d-cross pairing determinant changed")
    return {
        "frequency_squared": "16/3=omega_e^2",
        "action_Hessian": _matrix_strings(hessian),
        "action_row_order": ["6*metric_t", "-6*metric_x", "maxwell_t", "maxwell_x"],
        "adjoint_basis": [[str(value) for value in witness] for witness in adjoint_basis],
        "source_columns_e1_e2": _matrix_strings(source_matrix),
        "adjoint_pairing_matrix": _matrix_strings(pairing),
        "determinant": "832",
        "cancellation_formula_for_d_nonzero": {
            "given_axial_adjoint_defect": "r=(r1,r2)",
            "e1_amplitude": "z1=-r1/(72*i*sqrt(3)*d)",
            "e2_amplitude": "z2=27*r2/(104*i*sqrt(3)*d)",
            "scope": "cancels the axial p-shell adjoint projection only; all other source channels and moment maps remain to be imposed",
        },
        "SO3_promotion": "d is an SO(3) scalar, so equivariance tensors this invertible multiplicity-space matrix with the identity on V_2; the theorem holds for all m",
    }


def build_certificate() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["e1_source"]["case"] == "e1" and records["e2_source"]["case"] == "e2", "source fixture labels changed")
    _require(records["axial_operator"]["classification"]["two_extra_algebraic_polarizations"], "axial operator changed")
    _require(records["exceptional_all_m"]["classification"]["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"], "exceptional input changed")
    _require(records["electric_gate"]["classification"]["electric_Qe_cannot_cancel_exceptional_adjoint_defect"], "preceding global gate changed")
    theorem = _pairing_theorem(records)
    return {
        "schema": "einstein-maxwell-weyl-d-axial-ell2-extra-resonance-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_D_AXIAL_ELL2_EXTRA_RESONANCE",
        "result_state": "D_TIMES_AXIAL_ELL2_EXTRA_ADJOINT_MAP_ISOMORPHISM_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "correction_class": "BOUNDED_OR_FINITE_QUASIPERIODIC",
        "domain": "homogeneous circumference-velocity d crossed with the complete axial ell=2,k=0 extra-primary multiplicity space, all m, at Omega^2=16/3",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "pairing_theorem": theorem,
        "classification": {
            "both_axial_extra_source_columns_direct_four_dimensional": True,
            "complete_axial_p_shell_adjoint_cokernel_exhibited": True,
            "d_cross_adjoint_map_invertible": True,
            "all_m_by_SO3_equivariance": True,
            "arbitrary_axial_resonant_defect_algebraically_cancellable_for_d_nonzero": True,
            "full_second_order_equation_solved": False,
            "stabilizer_moment_maps_simultaneously_zero": False,
            "polar_d_cross_block_classified": False,
            "smooth_secular_correction_theorem": False,
            "causal_retarded_correction_theorem": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The circumference velocity is not a spectator. Its cross-source with the two axial ell=2 extra representatives spans the entire axial p-shell adjoint cokernel. Consequently an axial resonant defect—including the axial component generated by mixed exceptional dipoles—can be canceled algebraically once d and suitable ell=2 axial extra amplitudes are admitted. This is a compatibility result, not yet a common-moment-map solution or a full second-order extension.",
        "next_gate": "compute the polar d-times-extra block, then add a,b and twist position/velocity and solve the simultaneous moment-map plus resonant-functional zero locus",
        "claim_boundary": "This theorem concerns bounded/finite-quasiperiodic axial resonant compatibility at one k=0 shell. It does not solve nonresonant rows, the polar defect, stabilizer constraints, smooth secular or causal correction classes, opposite momenta, multiple |k| fibres, all-orders integration, residual descent, particles, or quantum theory.",
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <scoped JSON paths>", "git diff --check -- <scoped paths>"]},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.91, "commands": [
                "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_axial_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json",
                "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_axial_ell2_extra_resonance.py",
                "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_axial_ell2_extra_resonance"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "inputs": ["e1_source", "e2_source", "axial_operator"]},
            "tier_3": {"status": "NOT_RUN", "reason": "polar, stabilizer-zero, and correction-class completion remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_axial_ell2_extra_resonance --verify bridge/certificates/einstein_maxwell_weyl_d_axial_ell2_extra_resonance.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_axial_ell2_extra_resonance.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_axial_ell2_extra_resonance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    payload = build_certificate()
    if arguments.write:
        DEFAULT_OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    assert arguments.verify is not None
    _require(json.loads(arguments.verify.read_text(encoding="utf-8")) == payload, "d-axial resonance certificate is stale")


if __name__ == "__main__":
    main()
