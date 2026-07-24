#!/usr/bin/env python3
"""Produce the exact partial-jet crosswalk certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
INPUTS = {
    "complete_reconstruction": ROOT / (
        "black_hole_programme/phase3/"
        "axial_complete_reconstruction_repair/certificate.json"
    ),
    "triangular_factorization": ROOT / (
        "black_hole_programme/phase3/"
        "axial_rw_lx_triangular_preflight/certificate.json"
    ),
    "spin_two_extension": ROOT / (
        "black_hole_programme/phase3/"
        "axial_spin_two_scattering_extension_preflight/certificate.json"
    ),
    "global_connection_v5": ROOT / (
        "black_hole_programme/phase3/"
        "axial_global_connection_matrix_v5/certificate.json"
    ),
    "h4_exterior_norm": ROOT / (
        "black_hole_programme/phase3/"
        "axial_horizon_h4_plucker_exterior_norm_v1/certificate.json"
    ),
    "h4_radial_refinement": ROOT / (
        "black_hole_programme/phase3/"
        "axial_horizon_h4_plucker_radial_refinement_v1/certificate.json"
    ),
}

R = sp.Symbol("r", positive=True)
W = sp.Symbol("omega")
I = sp.I


def parse(value: str | int) -> sp.Expr:
    return sp.sympify(value, locals={"r": R, "omega": W, "I": I})


def matrix(rows: list[list[str | int]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def reduce_expr(value: sp.Expr) -> sp.Expr:
    return sp.cancel(sp.together(value))


def encode(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(reduce_expr(value)))


def encode_matrix(value: sp.Matrix) -> list[list[str]]:
    return [
        [encode(value[row, col]) for col in range(value.cols)]
        for row in range(value.rows)
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_expected(
    a: sp.Matrix,
    e: sp.Matrix,
    c: sp.Matrix,
    d: sp.Matrix,
    ax: sp.Matrix,
) -> sp.Matrix:
    result = sp.zeros(6)
    result[:2, :2] = a
    result[:2, 2:4] = e
    result[:2, 4:6] = c
    result[2:4, 2:4] = a
    result[2:4, 4:6] = d
    result[4:6, 4:6] = ax
    return result


def derive(documents: dict[str, dict]) -> dict[str, sp.Matrix]:
    complete = documents["complete_reconstruction"]
    triangular = documents["triangular_factorization"]

    flow6 = matrix(complete["complete_reconstruction"]["flow6"])
    a4 = flow6[:4, :4]
    source = flow6[4:6, :4]
    kernel2 = flow6[4:6, 4:6]
    embedding = matrix(
        triangular["carrier_exact_sequence"]["RW_embedding_J"]
    )
    right_inverse = matrix(
        triangular["carrier_exact_sequence"]["right_inverse_N"]
    )
    carrier_gauge = embedding.row_join(right_inverse)
    metric_master = matrix(
        triangular["Einstein_kernel_RW_equivalence"][
            "U_H1F_to_PsiPsiPrime"
        ]
    )

    carrier_flow = (
        carrier_gauge.inv()
        * (a4 * carrier_gauge - carrier_gauge.diff(R))
    ).applyfunc(reduce_expr)
    a = carrier_flow[:2, :2]
    d = carrier_flow[:2, 2:4]
    ax = carrier_flow[2:4, 2:4]
    e = (metric_master * source * embedding).applyfunc(reduce_expr)
    c = (metric_master * source * right_inverse).applyfunc(reduce_expr)
    common_source = (metric_master * source).applyfunc(reduce_expr)
    joint_extension = e.row_join(c)
    forcing_column = sp.Matrix([-R, 1])
    forcing_row = common_source[1:2, :]

    # Old order is (carrier_4, metric_2); new order is
    # (metric_RW, carrier_RW, Lx).
    old_to_new = (
        sp.zeros(2, 4).row_join(metric_master)
        .col_join(carrier_gauge.inv().row_join(sp.zeros(4, 2)))
    )
    transformed = (
        old_to_new.diff(R) * old_to_new.inv()
        + old_to_new * flow6 * old_to_new.inv()
    ).applyfunc(reduce_expr)
    expected = block_expected(a, e, c, d, ax)

    base = sp.zeros(4)
    base[:2, :2] = a
    base[:2, 2:4] = d
    base[2:4, 2:4] = ax
    tangent = sp.zeros(4)
    tangent[:2, :2] = e
    tangent[:2, 2:4] = c

    return {
        "flow6": flow6,
        "kernel2": kernel2,
        "embedding": embedding,
        "right_inverse": right_inverse,
        "carrier_gauge": carrier_gauge,
        "metric_master": metric_master,
        "carrier_flow": carrier_flow,
        "A": a,
        "D": d,
        "Ax": ax,
        "E": e,
        "C": c,
        "common_source": common_source,
        "joint_extension": joint_extension,
        "forcing_column": forcing_column,
        "forcing_row": forcing_row,
        "old_to_new": old_to_new,
        "transformed": transformed,
        "expected": expected,
        "base": base,
        "tangent": tangent,
    }


def assert_zero_matrix(value: sp.Matrix, label: str) -> None:
    if any(reduce_expr(entry) != 0 for entry in value):
        raise RuntimeError(f"{label} failed")


def produce() -> dict:
    documents = {
        name: json.loads(path.read_text())
        for name, path in INPUTS.items()
    }
    result = derive(documents)

    assert_zero_matrix(
        result["transformed"] - result["expected"],
        "full transformed six-state identity",
    )
    assert_zero_matrix(
        result["kernel2"] - (
            result["metric_master"].inv()
            * result["A"]
            * result["metric_master"]
            - result["metric_master"].inv()
            * result["metric_master"].diff(R)
        ),
        "metric master chain identity",
    )
    imported_e = matrix(
        documents["spin_two_extension"]["exact_local_extension"]["matrix"]
    )
    assert_zero_matrix(result["E"] - imported_e, "imported E identity")
    witness = parse(
        documents["triangular_factorization"][
            "complete_six_state_filtration"
        ]["natural_gauge_Lx_to_metric_extension_witness"]
    )
    if reduce_expr(result["C"][0, 0] - witness) != 0:
        raise RuntimeError("C witness mismatch")
    if result["E"].rank() != 1 or result["C"].rank() != 1:
        raise RuntimeError("rank-one extension identity failed")
    if result["joint_extension"].rank() != 1:
        raise RuntimeError("joint extension rank-one identity failed")
    assert_zero_matrix(
        result["common_source"]
        - result["forcing_column"] * result["forcing_row"],
        "common-source outer factorization",
    )
    assert_zero_matrix(
        result["joint_extension"]
        - result["common_source"] * result["carrier_gauge"],
        "joint common-source identity",
    )

    # Generic fundamental-map partial jet. P and R are 2x2 base diagonal
    # blocks, Q is the base Lx-to-RW transfer, and dotted blocks are the
    # intrinsic first variations. The determinant must be independent of
    # Q and all tangent blocks.
    symbols = sp.symbols(
        "p00 p01 p10 p11 q00 q01 q10 q11 "
        "r00 r01 r10 r11 pd00 pd01 pd10 pd11 "
        "qd00 qd01 qd10 qd11"
    )
    p = sp.Matrix(2, 2, symbols[0:4])
    q = sp.Matrix(2, 2, symbols[4:8])
    rmap = sp.Matrix(2, 2, symbols[8:12])
    pdot = sp.Matrix(2, 2, symbols[12:16])
    qdot = sp.Matrix(2, 2, symbols[16:20])
    phi6 = sp.zeros(6)
    phi6[:2, :2] = p
    phi6[:2, 2:4] = pdot
    phi6[:2, 4:6] = qdot
    phi6[2:4, 2:4] = p
    phi6[2:4, 4:6] = q
    phi6[4:6, 4:6] = rmap
    determinant = sp.factor(phi6.det())
    expected_determinant = sp.factor(p.det() ** 2 * rmap.det())
    if sp.expand(determinant - expected_determinant) != 0:
        raise RuntimeError("fundamental-map determinant identity failed")

    imports = {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
        for name, path in INPUTS.items()
    }
    document = {
        "schema": "phase3-axial-partial-jet-transport-crosswalk-v1",
        "schema_path": str((HERE / "schema.json").relative_to(ROOT)),
        "result_id": "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_TRANSPORT_CROSSWALK",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "EXACT_LOCAL_PARTIAL_JET_CROSSWALK_ENDPOINT_OPEN",
        "declaration": {
            "theory": "strict linearized four-dimensional pure Weyl C^2 gravity",
            "background": "Schwarzschild exterior M=1",
            "sector": "axial ell=2",
            "coefficient_field": "Q(I,omega,r)",
            "derivative": "d/dr",
            "old_state_order": ["carrier_4", "metric_2"],
            "new_state_order": [
                "metric_RW_tangent",
                "carrier_RW_base",
                "Lx_spin_one",
            ],
        },
        "imports": imports,
        "exact_blocks": {
            "A_RW": encode_matrix(result["A"]),
            "A_x": encode_matrix(result["Ax"]),
            "D_Lx_to_carrier_RW": encode_matrix(result["D"]),
            "E_RW_self_extension": encode_matrix(result["E"]),
            "C_Lx_to_metric_RW": encode_matrix(result["C"]),
            "E_rank": int(result["E"].rank()),
            "C_rank": int(result["C"].rank()),
            "joint_E_C_rank": int(result["joint_extension"].rank()),
            "C_00_witness": encode(result["C"][0, 0]),
        },
        "common_scalar_forcing": {
            "identity": "[E C]=U*S*[J N]",
            "U_times_S": encode_matrix(result["common_source"]),
            "joint_E_C": encode_matrix(result["joint_extension"]),
            "outer_column_ell": encode_matrix(result["forcing_column"]),
            "outer_row_rho": encode_matrix(result["forcing_row"]),
            "outer_factorization": "U*S=ell*rho",
            "scalar": "sigma=rho*(J*Y+N*Z)",
            "forcing": "(U*u)*sigma=ell*sigma",
            "rank": int(result["joint_extension"].rank()),
        },
        "full_transform_crosswalk": {
            "coordinate_map_old_to_new": encode_matrix(result["old_to_new"]),
            "transformation_law": "G_prime*G_inverse+G*flow6*G_inverse",
            "transformed_full_6x6": encode_matrix(result["transformed"]),
            "expected_block_matrix": encode_matrix(result["expected"]),
            "exact_identity_verified": True,
        },
        "partial_jet": {
            "type": "spin-two-row partial first jet; not the full jet of a four-state module",
            "state_module": "(epsilon*M_RW direct_sum M_RW) direct_sum M_x",
            "dual_number_ring": "Q(I,omega,r)[epsilon]/(epsilon**2)",
            "base_four_state_connection_B0": encode_matrix(result["base"]),
            "tangent_four_state_connection_B1": encode_matrix(result["tangent"]),
            "family": "B(tau)=B0+tau*B1",
            "held_tau_independent": "spin-one state Z and A_x",
            "differentiated_equations": (
                "X0'=A*X0+E*X1+C*Z; "
                "X1'=A*X1+D*Z; Z'=A_x*Z"
            ),
            "expanded_six_state_connection": encode_matrix(result["expected"]),
            "exact_identity_verified": True,
        },
        "fundamental_map_partial_jet": {
            "base_map": "Phi4(tau)=[[P(tau),Q(tau)],[0,R]]",
            "expanded_map": (
                "Phi6=[[P,Pdot,Qdot],[0,P,Q],[0,0,R]]"
            ),
            "matrix_template": encode_matrix(phi6),
            "determinant": encode(determinant),
            "determinant_identity": "det(Phi6)=det(P)**2*det(R)",
            "exact_determinant_verified": True,
            "proof_scope": (
                "Exact partial-jet functor plus product rule and common "
                "identity initial data; no endpoint frame is asserted."
            ),
        },
        "conditional_endpoint_derivative": {
            "hypothesis": (
                "C_plus(tau) and C_minus(tau) are induced by compatible "
                "tau-analytic endpoint frames from the same family"
            ),
            "connection_formula": "T_pm=J_partial(C_pm)",
            "scattering_formula": (
                "T_plus*T_minus_inverse="
                "J_partial(C_plus*C_minus_inverse)"
            ),
            "derivative_formula": (
                "d_tau(C_plus*C_minus_inverse)="
                "C_plus_dot*C_minus_inverse-"
                "C_plus*C_minus_inverse*C_minus_dot*C_minus_inverse"
            ),
            "hypothesis_verified_here": False,
        },
        "transport_method_boundary": {
            "tau_dual_alone_cures_H4": False,
            "reason": (
                "The H4 exterior-norm rail already retained a shared omega "
                "generator across all real coordinates; its refusal was a "
                "Taylor-product/exterior-norm conditioning failure, not "
                "independent-column tau decorrelation."
            ),
            "required_successor_algebra": (
                "IvTaylor4_omega tensor Q(I,omega,r)[epsilon]/(epsilon**2)"
            ),
            "global_v5_relevance": (
                "The partial jet targets the structured lower-lift "
                "decorrelation diagnosed in global connection v5, but no "
                "validated transport has been run here."
            ),
            "bounded_transport_attempted": False,
        },
        "endpoint_hypotheses": {
            "required_for_Tpm_equals_partial_jet": [
                "endpoint frames induced by one common tau-analytic family",
                "the same common horizon frame on base and tangent rows",
                "tau-analytic preservation of declared boundary classes",
                "tau-independent spin-one block in the selected normalization",
                "explicit permutation from endpoint factor order to jet order",
            ],
            "constructed_here": False,
        },
        "claim_flags": {
            "exact_full_six_state_factor_gauge_crosswalk": True,
            "missing_C_derived": True,
            "E_rank_one": True,
            "C_rank_one": True,
            "joint_E_C_rank_one": True,
            "common_scalar_forcing_certified": True,
            "partial_spin_two_row_jet_exact": True,
            "fundamental_map_partial_jet_formula_exact": True,
            "fundamental_map_determinant_exact": True,
            "tau_only_H4_repair_certified": False,
            "endpoint_partial_jet_frames_constructed": False,
            "T_plus_recovered": False,
            "scattering_identity_certified": False,
            "bounded_transport_certified": False,
            "H4_pass_certified": False,
        },
        "does_not_establish": [
            "compatible endpoint partial-jet frames",
            "the outgoing trace map T_plus",
            "a global scattering identity",
            "bounded interval or direct-integral transport",
            "an H4 exterior-norm pass",
            "time-domain stability or a Lorentzian causal theorem",
        ],
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    return document


if __name__ == "__main__":
    cert = produce()
    print(
        "status=" + cert["status"]
        + " full_six_state_identity=true partial_jet=true endpoint_open=true"
    )
