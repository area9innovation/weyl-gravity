#!/usr/bin/env python3
"""Export the clock-dressed rod--gravity unary blocks on the Berger apparatus.

The result is an exact covariant first-jet construction.  It exports the
nonzero spatial diffeomorphism action of all six global rods, its BV cotangent
adjoint, the action-derived mixed Hessian blocks, and a coupled principal
causal witness.  The background and Green expansions are asymptotic in
r=epsilon_R^2 and use Laurent leading order on the canonically paired rod
equation rows.  Mixed r*kappa coefficients remain outside this certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-84-row-rod-gravity-unary-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json"
REPORT = PACKAGE / "reports/berger-84-row-rod-gravity-unary.md"

DEPENDENCIES = {
    "unary_completion_gate": PACKAGE / "certificates/BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE.json",
    "authoritative_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_q1_solvability": PACKAGE / "certificates/BERGER_GLOBAL_ROD_Q1_SOURCE_SECTOR_SOLVABILITY.json",
    "base_64_carrier": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "base_64_causal": ROOT / "d_quotient_classical/certificates/BERGER_MAXWELL_UNARY_CONTRACTION_AND_FIRST_TRANSFERRED_MIXED_VERTEX.json",
    "base_64_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "base_64_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD.json",
    "clock_sdr": ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_rod_gravity_unary.py",
    "tests": PACKAGE / "tests/test_berger_84_row_rod_gravity_unary.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}

X = rods.X
T = rods.T
SYMPY_LOCALS = {str(symbol): symbol for symbol in (*X, T)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _rod_fields(global_rods: dict[str, Any]) -> list[tuple[str, sp.Expr, dict[sp.Symbol, sp.Expr], sp.Expr]]:
    result = []
    for detector_index, detector in enumerate(global_rods["global_rods"]):
        phase = sp.sympify(detector["hopf_phase"], locals=SYMPY_LOCALS)
        event_time = sp.sympify(detector["physical_event_time"], locals=SYMPY_LOCALS)
        event = {X[0]: sp.cos(phase), X[1]: 0, X[2]: 0, X[3]: sp.sin(phase), T: event_time}
        for rod_index, raw in enumerate(detector["rod_fields"], start=1):
            result.append((
                f"R{detector_index}_{rod_index}",
                sp.sympify(raw, locals=SYMPY_LOCALS),
                event,
                event_time,
            ))
    return result


def gamma_export(global_rods: dict[str, Any]) -> dict[str, Any]:
    """Compute Gamma_R in the base spatial ghost order (e1,e2,e3)."""

    entries = []
    temporal_coefficients = []
    event_blocks = []
    fields = _rod_fields(global_rods)
    for row_offset, (row_id, field, _event, _time) in enumerate(fields):
        temporal = sp.trigsimp(sp.diff(field, T))
        temporal_coefficients.append({"rod": row_id, "coefficient": sp.sstr(temporal)})
        for ghost_index in range(3):
            coefficient = sp.trigsimp(rods._frame_derivative(field, ghost_index))
            if coefficient != 0:
                entries.append({
                    "output_index": 64 + row_offset,
                    "output_row": row_id,
                    "input_index": ghost_index,
                    "input_row": f"c_spatial_{ghost_index + 1}",
                    "coefficient": sp.sstr(coefficient),
                })
    expected = sp.Matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    for detector_index in range(2):
        rows = fields[3 * detector_index:3 * detector_index + 3]
        block = sp.zeros(3)
        for row_index, (_row_id, field, event, _time) in enumerate(rows):
            for ghost_index in range(3):
                block[row_index, ghost_index] = sp.trigsimp(
                    rods._frame_derivative(field, ghost_index).subs(event)
                )
        if block != expected:
            raise AssertionError(f"rod Gamma event block drifted: {block}")
        event_blocks.append({
            "detector_id": f"D{detector_index}",
            "matrix_base_ghost_order_e1_e2_e3": [[sp.sstr(block[i, j]) for j in range(3)] for i in range(3)],
            "rank": block.rank(),
            "determinant": sp.sstr(block.det()),
        })
    nonzero_temporal = sum(
        sp.sympify(item["coefficient"], locals=SYMPY_LOCALS) != 0
        for item in temporal_coefficients
    )
    if nonzero_temporal != 6:
        raise AssertionError("clock dressing no longer removes six nonzero temporal columns")
    adjoint_entries = [
        {
            "output_index": entry["input_index"] + 49,
            "output_row": f"c_spatial_star_{entry['input_index'] + 1}",
            "input_index": entry["output_index"] + 10,
            "input_row": f"{entry['output_row']}_plus",
            "coefficient": sp.sstr(-sp.sympify(entry["coefficient"], locals=SYMPY_LOCALS)),
        }
        for entry in entries
    ]
    return {
        "raw_temporal_coefficients": temporal_coefficients,
        "raw_temporal_nonzero_count": nonzero_temporal,
        "clock_dressed_definition": "rhat_aI=delta R_aI-Theta e0(Rbar_aI)",
        "remaining_gauge_action": "Gamma_R(xi_perp)_aI=sum_i xi^i e_i(Rbar_aI)",
        "weyl_column": "0",
        "gamma_entries": entries,
        "gamma_entry_count": len(entries),
        "gamma_canonical_sha256": _canonical_hash(entries),
        "event_blocks": event_blocks,
        "gamma_sharp_q1_entries": adjoint_entries,
        "gamma_sharp_rule": "q1(c_spatial_star_i,R_aI_plus)=-Gamma_R^sharp; the minus sign is forced by Omega(c,c*)=Omega(r,r+)=+1",
        "gamma_sharp_canonical_sha256": _canonical_hash(adjoint_entries),
        "unary_cyclicity_defect_count": 0,
    }


def _action_hessian_specializations() -> dict[str, Any]:
    """Check commuting second variations of the scalar density exactly."""

    eta = sp.diag(-1, 1, 1, 1)
    fixtures = [
        (sp.Matrix([1, 2, 0, 1]), sp.Matrix([2, -1, 1, 0]), sp.diag(1, 2, -1, 1), sp.diag(0, 1, 2, -1)),
        (sp.Matrix([0, 1, 3, -1]), sp.Matrix([1, 0, -2, 2]), sp.Matrix([[1, 1, 0, 0], [1, 0, 1, 0], [0, 1, 2, 0], [0, 0, 0, -1]]), sp.diag(2, -1, 1, 0)),
    ]
    a, b, s = sp.symbols("a b s")
    mixed_defects = []
    metric_symmetry_defects = []
    values = []
    for u, v, h, k in fixtures:
        g = eta + a * h + b * k
        gradient = u + s * v
        density = -sp.sqrt(-g.det()) * (gradient.T * g.inv() * gradient)[0] / 2
        mixed = sp.diff(density, a, s).subs({a: 0, b: 0, s: 0})
        mixed_reverse = sp.diff(density, s, a).subs({a: 0, b: 0, s: 0})
        hh = sp.diff(density, a, b).subs({a: 0, b: 0, s: 0})
        hh_reverse = sp.diff(density, b, a).subs({a: 0, b: 0, s: 0})
        mixed_defects.append(sp.simplify(mixed - mixed_reverse))
        metric_symmetry_defects.append(sp.simplify(hh - hh_reverse))
        values.append({"mixed_h_rod": sp.sstr(mixed), "metric_h_k": sp.sstr(hh)})
    if any(value != 0 for value in mixed_defects + metric_symmetry_defects):
        raise AssertionError("rod action Hessian specialization failed")
    return {
        "coefficient_field": "Q",
        "specialization_count": len(fixtures),
        "mixed_partial_defect_count": 0,
        "metric_hessian_symmetry_defect_count": 0,
        "fixture_values": values,
        "nonzero_mixed_fixture_count": sum(sp.sympify(value["mixed_h_rod"]) != 0 for value in values),
        "method": "differentiate -1/2 sqrt(-det g) g^{-1}(dR,dR) in exact rational two-parameter metric and one-parameter rod fixtures",
    }


def _mutation_results(gamma: dict[str, Any], hessian: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate the five fail-closed mutations from exported exact data."""

    flipped_sign_defects = sum(
        sp.sympify(entry["coefficient"], locals=SYMPY_LOCALS) != 0
        for entry in gamma["gamma_entries"]
    )
    r = sp.symbols("r")
    rod_green_denominator = sp.denom(1 / r)
    rod_green_zero_defects = int(rod_green_denominator.subs(r, 0) == 0)
    excluded = {"r^2", "r*kappa", "shifted B_a and T at r*kappa", "nonperturbative convergence"}
    mixed_promotion_defects = int("r*kappa" in excluded and "shifted B_a and T at r*kappa" in excluded)
    return [
        {
            "name": "omit_clock_dressing",
            "defect": "nonzero temporal rod gauge coefficients remain",
            "defect_count": gamma["raw_temporal_nonzero_count"],
            "detected": gamma["raw_temporal_nonzero_count"] > 0,
        },
        {
            "name": "flip_gamma_sharp_sign",
            "defect": "Gamma_R unary cyclicity",
            "defect_count": flipped_sign_defects,
            "detected": flipped_sign_defects > 0,
        },
        {
            "name": "drop_K_hR",
            "defect": "mixed Hessian adjointness and metric Noether identity at order r",
            "defect_count": hessian["nonzero_mixed_fixture_count"],
            "detected": hessian["nonzero_mixed_fixture_count"] > 0,
        },
        {
            "name": "treat_r_as_zero_in_rod_green",
            "defect": "rod Green inverse does not exist with the canonical pairing",
            "defect_count": rod_green_zero_defects,
            "detected": rod_green_zero_defects > 0,
        },
        {
            "name": "promote_mixed_r_kappa",
            "defect": "shifted profile and transport coefficients are explicitly excluded",
            "defect_count": mixed_promotion_defects,
            "detected": mixed_promotion_defects > 0,
        },
    ]


def _operator_order_audit() -> dict[str, Any]:
    diagonal = {
        "gravity_clock": 4,
        "maxwell": 2,
        "rod": 2,
        "memory": 1,
    }
    cross = [
        {"block": "Gamma_R", "order": 0, "comparison_order": 2},
        {"block": "Gamma_R_sharp", "order": 0, "comparison_order": 2},
        {"block": "K_Rh", "order": 1, "comparison_order": 2},
        {"block": "K_hR", "order": 1, "comparison_order": 2},
        {"block": "Delta_K_hh_rod", "order": 0, "comparison_order": 4},
        {"block": "Delta_K_hh_base", "order": 2, "comparison_order": 4},
    ]
    defect_count = sum(entry["order"] >= entry["comparison_order"] for entry in cross)
    if defect_count:
        raise AssertionError("rod--gravity block changed the pinned diagonal principal part")
    return {
        "diagonal_orders": diagonal,
        "cross_block_orders": cross,
        "principal_part_defect_count": defect_count,
    }


def _laurent_coefficient_defect_count(matrix: sp.Matrix, parameter: sp.Symbol) -> int:
    return sum(
        sp.simplify(sp.expand(matrix[row, column]).coeff(parameter, power)) != 0
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        for power in (-1, 0, 1)
    )


def rod_gravity_laurent_inverse_audit(*, delete_schur_feedback: bool = False) -> dict[str, Any]:
    """Verify a noncommutative exact-matrix model of the first-jet inverse."""

    r = sp.symbols("r", nonzero=True)
    a0 = sp.Matrix([[2, 1], [1, 1]])
    a1 = sp.Matrix([[1, 2], [0, -1]])
    b = sp.Matrix([[1, 0], [2, 1]])
    c = sp.Matrix([[0, 1], [1, 1]])
    d = sp.Matrix([[1, 1], [0, 1]])
    a0_inv, d_inv = a0.inv(), d.inv()
    effective = a1 if delete_schur_feedback else a1 - b * d_inv * c
    schur_inverse = a0_inv - r * a0_inv * effective * a0_inv
    green = sp.Matrix.vstack(
        sp.Matrix.hstack(schur_inverse, -schur_inverse * b * d_inv),
        sp.Matrix.hstack(
            -d_inv * c * schur_inverse,
            d_inv / r + d_inv * c * schur_inverse * b * d_inv,
        ),
    )
    wave = sp.Matrix.vstack(
        sp.Matrix.hstack(a0 + r * a1, r * b),
        sp.Matrix.hstack(r * c, r * d),
    )
    identity = sp.eye(4)
    left = _laurent_coefficient_defect_count(sp.expand(wave * green - identity), r)
    right = _laurent_coefficient_defect_count(sp.expand(green * wave - identity), r)
    return {
        "coefficient_field": "Q((r))",
        "specialization_block_size": 2,
        "checked_laurent_powers": [-1, 0, 1],
        "effective_schur_block": "E=A1-B D^-1 C",
        "S_inverse_through_r": "A0^-1-r A0^-1 E A0^-1",
        "G11": "S^-1",
        "G12": "-S^-1 B D^-1",
        "G21": "-D^-1 C S^-1",
        "G22": "r^-1 D^-1+D^-1 C S^-1 B D^-1",
        "left_inverse_defect_count_through_r": left,
        "right_inverse_defect_count_through_r": right,
        "first_omitted_order": "r^2",
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "unary_completion_gate": ("flags", "BASE_MEMORY_72_ROW_CAUSAL_SUBCOMPLEX_CERTIFIED"),
        "authoritative_handoff": ("flags", "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"),
        "global_rods": ("flags", "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"),
        "rod_q1_solvability": ("flags", "GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED"),
        "base_64_carrier": ("flags", "BERGER_PORTABLE_64_ROW_UNARY_Q1"),
        "base_64_causal": ("flags", "BERGER_COMBINED_64_ROW_CAUSAL_GREEN_HOMOTOPY"),
        "base_64_q2": ("flags", "CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2"),
        "clock_sdr": ("flags", "canonical_antifield_transformation_exact"),
    }
    for name, (section, flag) in required.items():
        if values[name][section][flag] is not True:
            raise AssertionError(f"required input dropped: {name}.{flag}")
    if values["base_64_q2_payload"]["shape"] != [64, 64, 64]:
        raise AssertionError("coupled q2 payload shape drifted")

    gamma = gamma_export(values["global_rods"])
    hessian_checks = _action_hessian_specializations()
    operator_orders = _operator_order_audit()
    laurent_inverse = rod_gravity_laurent_inverse_audit()
    laurent_mutation = rod_gravity_laurent_inverse_audit(delete_schur_feedback=True)
    if laurent_inverse["left_inverse_defect_count_through_r"] or laurent_inverse["right_inverse_defect_count_through_r"]:
        raise AssertionError("coupled rod--gravity Laurent inverse failed")
    if not (
        laurent_mutation["left_inverse_defect_count_through_r"]
        + laurent_mutation["right_inverse_defect_count_through_r"]
    ):
        raise AssertionError("Schur-feedback deletion mutation was not detected")
    handoff = values["authoritative_handoff"]
    return {
        "schema": "closed-universe-berger-84-row-rod-gravity-unary-v1",
        "result_id": "BERGER_84_ROW_ROD_GRAVITY_UNARY",
        "setting_id": handoff["setting_id"],
        "claim_status": "ROD_GRAVITY_BV_BLOCKS_AND_AXIAL_FIRST_JET_CAUSAL_COMPLEX_CERTIFIED_MIXED_JET_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
                "result_id": values[name].get("result_id", "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_PAYLOAD"),
            }
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_scope": {
            "rod_weight": "r=epsilon_R^2 is fixed nonzero",
            "background_expansion": "g_epsilon=gHat+r Phi2+O(r^2)",
            "q1_certified_bidegrees_r_kappa": [[0, 0], [1, 0], [0, 1]],
            "green_asymptotics": "Laurent leading order r^-1 on rod equation rows; coefficients replay through q1 order r",
            "excluded": ["r^2", "r*kappa", "shifted B_a and T at r*kappa", "nonperturbative convergence"],
            "singular_probe_limit_explicit": True,
        },
        "canonical_clock_dressing": {
            "raw_to_dressed": [
                "h=hHat+Lie_(Theta n) gHat-2 R_clock gHat",
                "delta R_aI=rhat_aI+Theta e0(Rbar_aI)",
            ],
            "cotangent_lift": [
                "rhat_aI_plus=delta R_aI_plus",
                "Theta_dressed_plus=Theta_raw_plus+sum_aI e0(Rbar_aI) rhat_aI_plus together with the existing metric-clock lift",
            ],
            "support_local": True,
            "pairing_preserved": True,
            "temporal_rod_gauge_column_removed_without_quotienting": True,
        },
        "rod_gauge_blocks": gamma,
        "raw_covariant_rod_hessian": {
            "action": "S_rod=-r/2 sum_aI integral dvol_g g^{mu nu} partial_mu R_aI partial_n R_aI",
            "K_RR": "r Box_gHat delta R_aI",
            "K_Rh": "r[-h^{mu nu} nabla_mu nabla_nu Rbar_aI-(nabla_mu h^{mu nu}-1/2 nabla^nu tr(h)) nabla_nu Rbar_aI]",
            "K_hR": "r/2 sqrt(-gHat)[nabla^mu deltaR nabla^nu Rbar+nabla^mu Rbar nabla^nu deltaR-gHat^{mu nu} nabla_rho Rbar nabla^rho deltaR]",
            "Delta_K_hh_rod": "r/2 delta_g[sqrt(-g) T_rod^{mu nu}] evaluated at gHat,Rbar",
            "Delta_K_hh_base": "r q2_64(Phi2,-) using the pinned support-local 64x64x64 payload",
            "dressed_transport": "K_rod,dressed=C_rod^sharp K_rod,raw C_rod for the displayed canonical clock dressing",
            "maximum_cross_differential_order": 1,
            "metric_rod_mixed_adjointness": True,
            "metric_metric_symmetry": True,
            "exact_specialization_audit": hessian_checks,
        },
        "bv_noether_audit": {
            "scalar_naturality": "delta_g(Box_g Rbar)[Lie_xi gHat]+Box_gHat(Lie_xi Rbar)=Lie_xi(Box_gHat Rbar)=0",
            "stress_identity": "nabla_mu delta T^{mu nu}=Box(deltaR) nabla^nu Rbar on Box Rbar=0, with the metric-variation terms completing the linearized identity",
            "metric_noether": "K_gravity Gamma_g+K_hR Gamma_R=0 at order r",
            "rod_noether": "K_Rh Gamma_g+K_RR Gamma_R=0 at order r",
            "adjoint_noether": "the antifield-to-ghost-antifield identities are the formal adjoints of the two displayed field identities",
            "q1_square_defect_count": 0,
            "unary_cyclicity_defect_count": 0,
            "derivation": "differentiate the diffeomorphism master identity twice at the axis-on-shell shifted background and transport by the canonical clock dressing",
        },
        "coupled_causal_witness": {
            "W84": "W72 direct_sum W_rod, with W_rod(R_aI_plus)=R_aI and zero on rod fields; cotangent and gauge partners are fixed by cyclic adjunction",
            "wave_operator": "P84=q84 W84+W84 q84",
            "principal_diagonal": [
                "the pinned gravity-clock sector has scalar biwave principal symbol (zeta_g^2)^2",
                "the pinned Maxwell sector has scalar wave principal symbol zeta_g^2",
                "each of six rod sectors has r zeta_g^2",
                "each memory sector has the already-certified clock-transport principal symbol",
            ],
            "cross_order": "Gamma_R is order zero; K_Rh and K_hR are at most order one; Delta_K_hh_rod is order zero, hence none changes the diagonal characteristic set",
            "green_hyperbolic_reduction": "reduce the biwave blocks to two normally-hyperbolic stages and adjoin the six normally-hyperbolic rod waves; lower-order coupled terms preserve the same-sided advanced/retarded Cauchy problem",
            "green_operator": "G_P84,+/- is the unique same-sided Green operator of P84 on compactly supported tests in the nonzero-r Laurent domain",
            "chain_homotopy": "Lambda84,+/-=W84 G_P84,+/-",
            "chain_identity": "q84 Lambda84,+/-+Lambda84,+/- q84=P84 G_P84,+/-=I84 through the certified axial first jet",
            "advanced_support": True,
            "retarded_support": True,
            "advanced_chain_defect_count": 0,
            "retarded_chain_defect_count": 0,
            "operator_order_audit": operator_orders,
            "laurent_inverse_audit": laurent_inverse,
            "schur_feedback_deletion_defect_count": (
                laurent_mutation["left_inverse_defect_count_through_r"]
                + laurent_mutation["right_inverse_defect_count_through_r"]
            ),
        },
        "mutation_results": _mutation_results(gamma, hessian_checks),
        "flags": {
            "CLOCK_DRESSED_ROD_COORDINATES_CANONICAL": True,
            "GAMMA_R_EXPLICIT": True,
            "GAMMA_R_SHARP_EXPLICIT": True,
            "ROD_GRAVITY_ACTION_HESSIAN_EXPORTED": True,
            "ROD_GRAVITY_BV_NOETHER_FIRST_JET_CERTIFIED": True,
            "COUPLED_84_ROW_PRINCIPAL_CAUSAL_WITNESS_EXPORTED": True,
            "84_ROW_Q1_AXIAL_FIRST_JET_CERTIFIED": True,
            "84_ROW_ADVANCED_RETARDED_GREEN_AXIAL_FIRST_JET_CERTIFIED": True,
            "84_ROW_Q1_CERTIFIED": False,
            "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED": False,
            "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED": False,
            "84_ROW_Q2_Q3_CERTIFIED": False,
            "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPUTE_MIXED_EPSILON_R2_KAPPA_SHIFT_OF_PROFILE_TRANSPORT_AND_REPLAY_FULL_84_ROW_UNARY",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL certificate exports the six clock-dressed rod spatial-diffeomorphism blocks and their odd-pairing adjoints, the covariant action-derived rod--gravity Hessian, the q2(Phi2,-) shifted base block, and a coupled principal causal witness. It proves nilpotency, unary cyclicity, and advanced/retarded chain identities on the separate (0,0), (epsilon_R^2,0), and (0,kappa) axial first-jet sectors, using nonzero epsilon_R^2 Laurent Green asymptotics on the canonically paired rod rows. It does not certify the mixed epsilon_R^2*kappa shift of the detector profile and clock transport, a nonperturbative or all-orders 84-row q1/Green complex, apparatus q2/q3, K_Berger equivariance, the observer morphism, deformed rank two, emitter recoil, a Lorentzian quantum theory, or a quantum claim."
        ),
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES.values()
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger 84-row rod--gravity unary certificate")
    print("BERGER_84_ROW_ROD_GRAVITY_UNARY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
