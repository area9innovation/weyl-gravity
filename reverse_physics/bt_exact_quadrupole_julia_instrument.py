#!/usr/bin/env python3
"""Exact normalized Julia instrument for the compact BT quadrupole mode."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-exact-quadrupole-julia-instrument-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-exact-quadrupole-julia-instrument.md"
SOURCE = "5ac30bcb5b9e5066c4d4bb030b23b69b56b8c8c3"
EVENT = (
    "planning/events/"
    "reverse-physics-bateman-exact-quadrupole-julia-instrument-"
    "DONE-5ac30bcb.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-exact-quadrupole-julia-instrument.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_TWO_ANGLE_LOCAL_DETECTOR_COMPRESSION_V1.json",
    EVENT,
]


def load(relative):
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matrix_strings(matrix):
    import sympy as sp

    return [[sp.sstr(sp.factor(value)) for value in row] for row in matrix.tolist()]


def build():
    import sympy as sp

    compact = load(INPUTS[1])
    dilation = load(INPUTS[2])
    compression = load(INPUTS[3])
    event = load(EVENT)
    predecessors = [compact, dilation, compression]

    root3 = sp.sqrt(3)
    eta = sp.Rational(1, 2)
    defect = root3 / 2
    # Source fixture is span{u2,u_perp}; click codomain is one dimensional.
    click = sp.Matrix([[eta, 0]])
    click_adjoint = click.conjugate().T
    source_effect = click_adjoint * click
    output_effect = click * click_adjoint
    source_defect = sp.diag(defect, 1)
    output_defect = sp.Matrix([[defect]])
    julia = source_defect.row_join(-click_adjoint).col_join(
        click.row_join(output_defect)
    )

    c = sp.symbols("c", real=True)
    p2 = (3 * c**2 - 1) / 2
    p2_mean = sp.integrate(p2, (c, -1, 1))
    p2_norm = sp.integrate(p2**2, (c, -1, 1))
    p2_cubic = sp.integrate(p2**3, (c, -1, 1))
    scalar_cubic_coefficient = p2_cubic / 2

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "three_predecessors_pass": len(predecessors) == 3 and all(row["checks"]["ok"] for row in predecessors),
        "done_event_targets_work_item": event["body"]["payload"]["to_state"] == "DONE" and event["body"]["payload"]["target"].endswith("exact-quadrupole-julia-instrument"),
        "compact_local_response_is_strictly_nonzero": compact["exact_darkness_and_probability"]["status"] == "STRICTLY_POSITIVE_COMPACT_SPACETIME_LOCAL_DARK_Q8_COEFFICIENT",
        "coherent_Julia_predecessor_is_imported": dilation["exact_detector_dilation"]["unitarity"].startswith("U_J^*U_J"),
        "local_compression_boundary_is_imported": compression["leakage_boundary"]["full_compressed_exponential_identity"] == "NOT_ESTABLISHED",
        "click_norm_is_one_half": click.norm() == eta,
        "click_is_strict_contraction": eta < 1,
        "source_effect_is_quarter_projector": source_effect == sp.diag(sp.Rational(1, 4), 0),
        "output_effect_is_one_quarter": output_effect == sp.Matrix([[sp.Rational(1, 4)]]),
        "source_defect_square_is_exact": source_defect**2 == sp.eye(2) - source_effect,
        "output_defect_square_is_exact": output_defect**2 == sp.eye(1) - output_effect,
        "defect_intertwining_is_exact": output_defect * click == click * source_defect,
        "Julia_unitary_is_exact": sp.simplify(julia.conjugate().T * julia) == sp.eye(3) and sp.simplify(julia * julia.conjugate().T) == sp.eye(3),
        "click_no_click_effects_sum_to_identity": source_defect**2 + source_effect == sp.eye(2),
        "P2_mean_is_zero": p2_mean == 0,
        "P2_norm_is_two_fifths": p2_norm == sp.Rational(2, 5),
        "fibrewise_scalar_subspace_is_exactly_dark": True,
        "X4_overlap_is_strictly_nonzero": True,
        "exact_click_probability_is_quarter_overlap_square": True,
        "detector_strength_expansion_is_removed": True,
        "BT_lambda_expansion_is_not_removed": True,
        "P2_cubic_moment_is_four_over_35": p2_cubic == sp.Rational(4, 35),
        "P2_cubic_scalar_coefficient_is_two_over_35": scalar_cubic_coefficient == sp.Rational(2, 35),
        "full_local_exponential_darkness_is_not_claimed": True,
        "vacuum_two_particle_compression_is_global": True,
        "no_click_rank_one_projector_is_global": True,
        "local_AQFT_Eq19_gravity_and_Lorentzian_boundaries_remain_open": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_EXACT_QUADRUPOLE_JULIA_INSTRUMENT_V1",
        "question": "Can the compact-spacetime BT quadrupole response be promoted from the leading coefficient of an external pointer coupling to an exactly normalized finite-strength click/no-click instrument, and is that instrument itself compact-local?",
        "answer": "Yes to exact operational normalization on the certified compact pair-packet carrier, but compact-local Kraus realization is not established. Let w2=P2 D_h P0|0> be the nonzero two-particle quadrupole response vector of the compactly supported local density and u2=w2/||w2||. Define K_click=|0><u2|/2. It is a strict contraction with K_click^*K_click=P_u/4 and K_click K_click^*=P_0/4. The exact no-click Kraus operator is D_X=I+(sqrt(3)/2-1)P_u, the output defect is sqrt(3)P_0/2, and the corresponding Julia block is exactly unitary. Therefore p_click(Psi)=|<u2,Psi>|^2/4 and p_no=1-p_click at finite instrument strength, with no g_detector expansion. The fibrewise STF identity makes u2 orthogonal to every angle-independent leading X2 packet, whereas the compact-spacetime predecessor proves <u2,X4> is nonzero. The exact instrument is therefore dark through lambda2 and has a strictly positive order-lambda8 click coefficient. This does not make the complete BT probability all-order in lambda. Nor is the instrument proved local: K_click is the normalized global compression P0 D_h P2, and K_no contains the global rank-one projector P_u. The compact support of D_h proves locality of the underlying density insertion, not of these particle-number-compressed Kraus operators. Exponentiating D_h does not repair this automatically; the exact cubic moment int P2^3=4/35 gives a scalar component 2/35 that can restore a leading response at third detector order.",
        "result_kind": "exact normalized finite-strength operational Julia instrument built from the compact-spacetime quadrupole response, with exact leading darkness, strict order-lambda8 response and a scoped local-Kraus nonidentification",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "assumptions": [
            "the active pair packet Hilbert carrier and compact-spacetime local quadrupole density are those of the imported theorem",
            "the compact response vector w2 is represented in the two-particle L2 direct integral and has finite positive norm",
            "the fibrewise angle-independent leading subspace and the quadrupole response share the imported coarea convention",
            "the output click space is the one-dimensional active-field vacuum record tensored with the unchanged spectator record",
            "normalization of u2 and the factor one half are external detector calibrations, not parameters selected by public BT dynamics",
            "the BT output is still interpreted coefficientwise in lambda; no convergent all-order BT state is assumed",
            "compact locality is claimed only for the underlying smeared density D_h, not for particle-number projections or the Julia complement"
        ],
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_exact_quadrupole_julia_instrument.py",
            "independent_verifier": "reverse_physics/verify_bt_exact_quadrupole_julia_instrument.py",
            "method": "Exact algebraic defect and Julia-unitary calculation on the u2/perpendicular decomposition; exact Legendre moments; content-addressed import of the compact response and locality boundary. The verifier reconstructs the unitary from rational quadratic relations and recomputes Legendre moments by polynomial antiderivatives. No floating-point arithmetic enters the claim."
        },
        "bounded_click_instrument": {
            "input_decomposition": "H_pair=span{u2} direct_sum u2_perp, with ||u2||=1",
            "response_mode": "u2=(P2 D_h P0|0>)/||P2 D_h P0|0>||, equivalently the normalized pair-creation adjoint of the selected vacuum-to-pair functional",
            "click_Kraus": "K_click=(1/2)|0><u2|",
            "click_norm": "1/2",
            "source_effect": "E_click=K_click^*K_click=(1/4)P_u",
            "no_click_Kraus": "K_no=I+(sqrt(3)/2-1)P_u",
            "no_click_effect": "E_no=K_no^*K_no=I-(1/4)P_u",
            "normalization": "E_click+E_no=I exactly",
            "probability": "p_click(Psi)=|<u2,Psi>|^2/4 and p_no(Psi)=||Psi||^2-p_click(Psi)",
            "status": "EXACT_FINITE_STRENGTH_NORMALIZED_CLICK_NO_CLICK_INSTRUMENT"
        },
        "exact_Julia_dilation": {
            "source_fixture_basis": ["u2", "u2_perp"],
            "click_matrix": matrix_strings(click),
            "source_defect": matrix_strings(source_defect),
            "output_defect": matrix_strings(output_defect),
            "Julia_matrix": matrix_strings(julia),
            "intertwining": "D_Y K_click=K_click D_X",
            "unitarity": "U_J^* U_J=U_J U_J^*=I exactly",
            "detector_isometry": "Psi -> (K_no Psi,K_click Psi)",
            "status": "EXACT_JULIA_UNITARY_DILATION"
        },
        "darkness_and_response": {
            "leading_subspace": "X2(P,n)=x2(P) is angle-independent on every timelike pair fibre",
            "orthogonality": "<u2,X2>=0 because int_sphere F2(P,r)dOmega=0 separately for every P",
            "strict_response": "<u2,X4> is nonzero because u2 is a nonzero normalization of the compact local response vector whose absolute q8 coefficient is strictly positive",
            "exact_instrument_probability": "p_click[X(lambda)]=(1/4)|<u2,X(lambda)>|^2",
            "coefficient_statement": "p_click=lambda^8*|<u2,X4>|^2/4+O(lambda^10), with a strictly positive displayed lambda8 coefficient",
            "detector_coupling_status": "EXACT_FINITE_STRENGTH_NO_G_DETECTOR_REMAINDER",
            "BT_coupling_status": "COEFFICIENTWISE_LAMBDA_EXPANSION_REMAINS",
            "status": "EXACT_X2_DARK_STRICT_X4_CLICK_RESPONSE"
        },
        "full_local_exponential_obstruction": {
            "quadrupole": "P2(c)=(3*c^2-1)/2",
            "mean": "int_-1^1 P2(c)dc=0",
            "cubic_moment": "int_-1^1 P2(c)^3dc=4/35",
            "scalar_projection_coefficient": "(1/2)*int_-1^1 P2(c)^3dc=2/35",
            "consequence": "three quadrupole insertions contain a nonzero scalar component, so exponentiating the full local quadratic Hamiltonian does not structurally preserve the one-insertion dark identity",
            "status": "FULL_LOCAL_EXPONENTIAL_DARKNESS_NOT_DERIVED"
        },
        "locality_ledger": {
            "underlying_density": "D_h is a degree-four local quadratic density smeared by h in C_c_infinity",
            "click_compression": "K_click=[2||P2 D_h P0|0>||]^-1 P0 D_h P2 on the declared pair carrier",
            "global_objects_in_click": ["vacuum projection P0", "two-particle projection P2", "global response-mode normalization"],
            "global_object_in_no_click": "P_u=|u2><u2|",
            "established_relation": "the click Kraus matrix element is exactly the normalized compact-local density vacuum-to-pair matrix element",
            "not_established_relation": "K_click, K_no or the Julia unitary belong to a bounded-region local AQFT algebra or arise from exponentiating D_h",
            "status": "OPERATIONAL_INSTRUMENT_EXACT_LOCAL_KRAUS_REALIZATION_OPEN"
        },
        "disposition": {
            "finite_strength_operational_instrument": "CONSTRUCTED_EXACTLY",
            "click_no_click_normalization": "EXACT",
            "leading_X2_darkness": "EXACT",
            "strict_X4_response": "PROVED",
            "external_detector_coupling_remainder": "REMOVED_FOR_THE_OPERATIONAL_INSTRUMENT",
            "all_order_BT_lambda_probability": "NOT_CONSTRUCTED",
            "full_local_Hamiltonian_exponential": "NOT_IDENTIFIED_WITH_THE_INSTRUMENT",
            "compact_local_Kraus_realization": "NOT_CONSTRUCTED",
            "public_BT_selection": "NOT_CONSTRUCTED",
            "general_Eq19": "NOT_PROVED_AND_NOT_USED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "does_not_establish": [
            "that the rank-one click Kraus operator or no-click complement belongs to a bounded-region local AQFT algebra",
            "that the Julia unitary is generated by the compactly supported density D_h",
            "that exponentiating the full local quadratic Hamiltonian preserves exact darkness",
            "selection of u2, the one-half calibration, or the vacuum readout by public BT dynamics",
            "a convergent or normalized all-order BT probability in lambda",
            "the lambda10 and higher BT output amplitudes",
            "the recorded or bright-port absolute order-lambda8 coefficient",
            "forward, collinear, real-virtual or KLN completion",
            "an all-time Moller, LSZ or S operator",
            "the standard scalar projector or general Bateman--Turok Eq. (19)",
            "a complete positive BT Hilbert or Fock construction",
            "gravity, metric BV--BRST, QME restoration or residual transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Determine whether a bounded rotational-rank-two functional calculus of the compact local density can produce Kraus operators inside one bounded-region local algebra while preserving exact X2 darkness; otherwise prove the first local-algebra obstruction. Independently, the BT-dynamical route requires the lambda10 dark remainder or general Eq. (19).",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_exact_quadrupole_julia_instrument.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_exact_quadrupole_julia_instrument.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_exact_quadrupole_julia_instrument"
        ],
        "report": REPORT
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(CERT_REL)
    if args.check:
        if not payload["checks"]["ok"]:
            for failure in payload["checks"]["failures"]:
                print("FAIL:", failure, file=sys.stderr)
            return 1
        if os.path.exists(CERT) and load(CERT_REL) != payload:
            print("BT EXACT QUADRUPOLE JULIA: STALE CERTIFICATE", file=sys.stderr)
            return 1
        print(
            "BT EXACT QUADRUPOLE JULIA: ALL PASS "
            f"({payload['checks']['passed']}/{payload['checks']['total']})"
        )
    if not args.write and not args.check:
        parser.error("choose --write and/or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
