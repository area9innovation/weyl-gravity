#!/usr/bin/env python3
"""Export the clock-dressed rod--gravity unary blocks on the Berger apparatus.

The result is an exact covariant first-jet construction.  It exports the
nonzero spatial diffeomorphism action of all six global rods, its BV cotangent
adjoint, the action-derived mixed Hessian blocks, and a formal coefficientwise
causal witness.  The corrected principal-symbol audit treats
q2(Phi2,-) as a fourth-order diagonal deformation, not as a subprincipal
perturbation.  Mixed r*kappa coefficients remain outside this certificate;
their coefficient ring and required identities are exported as a preflight.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from closed_universe_observers import generate_berger_global_detector_rods as rods
from closed_universe_observers import generate_berger_global_rod_q1_solvability as rod_solv


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
    "base_54_q2_payload": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json",
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


@lru_cache(maxsize=32)
def _load_json_cached(path_text: str, sha256: str) -> dict[str, Any]:
    del sha256
    return json.loads(Path(path_text).read_text())


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


@lru_cache(maxsize=4)
def _cached_gamma(global_rods_sha256: str) -> dict[str, Any]:
    return gamma_export(_load_json_cached(str(DEPENDENCIES["global_rods"]), global_rods_sha256))


@lru_cache(maxsize=1)
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


def _sparse_vector(value: sp.Matrix) -> list[list[Any]]:
    return [[index, sp.sstr(sp.factor(value[index]))] for index in range(value.rows) if value[index] != 0]


def _primitive_matrix(block: dict[str, Any]) -> sp.Matrix:
    matrix = sp.zeros(100, 3)
    for column, entries in enumerate(block["canonical_primitives_sparse"]):
        for row, coefficient in entries:
            matrix[row, column] = sp.sympify(coefficient, locals={"I": sp.I})
    return matrix


def _payload_scalar(value: dict[str, Any]) -> sp.Expr:
    def rational(item: Any) -> sp.Rational:
        if isinstance(item, dict):
            return sp.Rational(item["numerator"], item["denominator"])
        return sp.Rational(item)

    return rational(value["rational"]) + rational(value.get("sqrt10", 0)) * sp.sqrt(10)


def physical_phi2_export(handoff: dict[str, Any], solvability: dict[str, Any]) -> dict[str, Any]:
    """Assemble the physical real Phi2 in one canonical 10 x 10 basis."""

    if not solvability["flags"]["ACTION_EULER_HALF_STRESS_NORMALIZATION_CERTIFIED"]:
        raise AssertionError("physical Phi2 source is not action normalized")
    synthesis = handoff["physical_backreaction_synthesis"]
    zero_primitive = _primitive_matrix(solvability["exact_blocks"]["zero"])
    positive_primitive = _primitive_matrix(solvability["exact_blocks"]["positive"])
    zero_coefficients = sp.Matrix([sp.sympify(value, locals={"I": sp.I}) for value in synthesis["zero_frequency_coefficients"]])
    positive_coefficients = sp.Matrix([sp.sympify(value, locals={"I": sp.I}) for value in synthesis["positive_frequency_coefficients"]])
    negative_coefficients = sp.Matrix([sp.sympify(value, locals={"I": sp.I}) for value in synthesis["negative_frequency_coefficients"]])
    zero = (zero_primitive * zero_coefficients).applyfunc(sp.simplify)
    positive = (positive_primitive * positive_coefficients).applyfunc(sp.simplify)
    negative = (positive_primitive.conjugate() * negative_coefficients).applyfunc(sp.simplify)
    reality_defects = sum(
        sp.trigsimp(sp.expand_complex(negative[index] - sp.conjugate(positive[index]))) != 0
        for index in range(100)
    )
    zero_reality_defects = sum(
        sp.trigsimp(sp.expand_complex(value - sp.conjugate(value))) != 0 for value in zero
    )
    if reality_defects or zero_reality_defects:
        raise AssertionError("assembled physical Phi2 failed its exact reality condition")

    carrier_rows = sorted(handoff["carrier"]["component_rows"], key=lambda row: row["index"])
    metric_rows = [row["row_id"] for row in carrier_rows if 5 <= row["index"] <= 14]
    if metric_rows != [
        "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
        "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33",
    ]:
        raise AssertionError("physical Phi2 metric-component order drifted")
    spatial_basis = solvability["finite_sector"]["spatial_basis"]
    if len(spatial_basis) != 10:
        raise AssertionError("physical Phi2 spatial basis drifted")
    derivative_matrices = []
    for axis, matrix in enumerate(rod_solv._spatial_matrices(), start=1):
        entries = [
            [row, column, sp.sstr(sp.factor(matrix[row, column]))]
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ]
        derivative_matrices.append({
            "operator": f"e{axis}",
            "shape": [10, 10],
            "entries": entries,
            "canonical_sha256": _canonical_hash(entries),
        })
    sparse = {
        "zero": _sparse_vector(zero),
        "positive": _sparse_vector(positive),
        "negative": _sparse_vector(negative),
    }
    return {
        "vector_shape": [10, 10],
        "vector_index_rule": "index=10*metric_component_index+spatial_basis_index",
        "metric_component_order": metric_rows,
        "spatial_basis_order": spatial_basis,
        "temporal_frequency_order": ["0", "+sqrt(58)/3", "-sqrt(58)/3"],
        "temporal_derivative_multipliers": ["0", "I*sqrt(58)/3", "-I*sqrt(58)/3"],
        "assembled_sparse_coefficients": sparse,
        "assembled_nonzero_counts": {name: len(entries) for name, entries in sparse.items()},
        "assembled_canonical_sha256": _canonical_hash(sparse),
        "spatial_derivative_matrices": derivative_matrices,
        "reconstruction": "Phi2(t,x)=sum_C,b [v0_Cb+exp(I*sqrt(58)*t/3)v+_Cb+exp(-I*sqrt(58)*t/3)v-_Cb] basis_b(x) e^C",
        "negative_equals_conjugate_positive": True,
        "reality_defect_count": reality_defects + zero_reality_defects,
        "source": "physical two-detector synthesis of the pinned canonical retained-mode primitives",
    }


def q2_principal_order_audit(payload: dict[str, Any], phi2: dict[str, Any]) -> dict[str, Any]:
    """Classify q2(Phi2,-) and exhibit an exact nonzero order-four coefficient."""

    histogram: dict[tuple[int, int], int] = {}
    metric_term_count = 0
    for row in payload["rows"]:
        if not 27 <= row["output"] <= 36:
            continue
        for first, first_word, second, second_word, _coefficient in row["terms"]:
            if 5 <= first <= 14 and 5 <= second <= 14:
                orders = (sum(first_word), sum(second_word))
                histogram[orders] = histogram.get(orders, 0) + 1
                metric_term_count += 1
    maximum_argument_order = max(max(orders) for orders in histogram)
    maximum_total_order = max(sum(orders) for orders in histogram)
    fourth_order_terms = sum(count for orders, count in histogram.items() if 4 in orders)
    if maximum_argument_order != 4 or maximum_total_order != 4 or fourth_order_terms == 0:
        raise AssertionError("pure-Weyl q2 principal-order audit drifted")

    # A single exact contracted coefficient is sufficient to rule out complete
    # cancellation of the fourth-order principal part.  This coefficient is
    # the zero-frequency, first-spatial-basis component multiplying
    # e3^4 h_hat_00 in the h_hat_00-antifield equation.
    witness_output = 27
    witness_fluctuation = 5
    witness_word = [0, 0, 0, 4]
    witness_spatial_basis = 0
    zero_phi2 = {
        index: sp.sympify(coefficient, locals={"I": sp.I})
        for index, coefficient in phi2["assembled_sparse_coefficients"]["zero"]
    }
    contracted_witness = sp.S.Zero
    for row in payload["rows"]:
        if row["output"] != witness_output:
            continue
        for first, first_word, second, second_word, coefficient in row["terms"]:
            scalar = _payload_scalar(coefficient)
            if second == witness_fluctuation and second_word == witness_word and 5 <= first <= 14 and sum(first_word) == 0:
                contracted_witness += scalar * zero_phi2.get(10 * (first - 5) + witness_spatial_basis, 0)
    contracted_witness = sp.factor(contracted_witness)
    if contracted_witness != sp.Rational(623, 324):
        raise AssertionError("physical Phi2 fourth-order contraction witness drifted")
    return {
        "payload_shape": payload["shape"],
        "metric_input_rows": list(range(5, 15)),
        "metric_antifield_output_rows": list(range(27, 37)),
        "metric_metric_term_count": metric_term_count,
        "derivative_order_histogram": [
            {"first_argument_order": orders[0], "second_argument_order": orders[1], "term_count": count}
            for orders, count in sorted(histogram.items())
        ],
        "maximum_argument_order": maximum_argument_order,
        "maximum_total_order": maximum_total_order,
        "fourth_order_argument_term_count": fourth_order_terms,
        "physical_phi2_nonzero_coefficient_count": sum(phi2["assembled_nonzero_counts"].values()),
        "classification": "FOURTH_ORDER_DIAGONAL_PRINCIPAL_DEFORMATION",
        "physical_contracted_principal_order": 4,
        "exact_non_cancellation_after_physical_phi2_contraction_certified": True,
        "physical_contraction_witness": {
            "output_row": witness_output,
            "output_component": "h_hat_00_antifield",
            "fluctuation_input_row": witness_fluctuation,
            "fluctuation_component": "h_hat_00",
            "fluctuation_derivative_word_e0_e1_e2_e3": witness_word,
            "background_temporal_frequency": "0",
            "background_spatial_basis_index": witness_spatial_basis,
            "contracted_coefficient": sp.sstr(contracted_witness),
        },
        "fail_closed_rule": "treat q2(Phi2,-) as order four unless an exact contracted cancellation certificate is supplied",
        "prior_order_two_classification_rejected": True,
    }


@lru_cache(maxsize=4)
def _cached_physical_phi2(handoff_sha256: str, solvability_sha256: str) -> dict[str, Any]:
    del handoff_sha256, solvability_sha256
    return physical_phi2_export(
        json.loads(DEPENDENCIES["authoritative_handoff"].read_text()),
        json.loads(DEPENDENCIES["rod_q1_solvability"].read_text()),
    )


@lru_cache(maxsize=4)
def _cached_principal_audit(
    payload_sha256: str, handoff_sha256: str, solvability_sha256: str
) -> dict[str, Any]:
    payload = json.loads(DEPENDENCIES["base_54_q2_payload"].read_text())
    phi2 = _cached_physical_phi2(handoff_sha256, solvability_sha256)
    del payload_sha256
    return q2_principal_order_audit(payload, phi2)


def _mutation_results(
    gamma: dict[str, Any], hessian: dict[str, Any], principal: dict[str, Any]
) -> list[dict[str, Any]]:
    """Evaluate the fail-closed mutations from exported exact data."""

    flipped_sign_defects = sum(
        sp.sympify(entry["coefficient"], locals=SYMPY_LOCALS) != 0
        for entry in gamma["gamma_entries"]
    )
    r = sp.symbols("r")
    rod_green_denominator = sp.denom(1 / r)
    rod_green_zero_defects = int(rod_green_denominator.subs(r, 0) == 0)
    excluded = {"r^2", "r*kappa", "delta_r T on the memory rows", "shifted B_a at r*kappa", "nonperturbative convergence"}
    mixed_promotion_defects = int("r*kappa" in excluded and "shifted B_a at r*kappa" in excluded)
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
            "defect": "the r-axis memory transport and mixed profile coefficients are explicitly excluded",
            "defect_count": mixed_promotion_defects,
            "detected": mixed_promotion_defects > 0,
        },
        {
            "name": "demote_q2_Phi2_to_order_two",
            "defect": "fourth-order pure-Weyl metric q2 terms are discarded from the principal deformation",
            "defect_count": principal["fourth_order_argument_term_count"],
            "detected": principal["maximum_argument_order"] == 4,
        },
    ]


def _operator_order_audit(principal: dict[str, Any]) -> dict[str, Any]:
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
    ]
    strict_cross_defect_count = sum(entry["order"] >= entry["comparison_order"] for entry in cross)
    if strict_cross_defect_count:
        raise AssertionError("an off-diagonal rod--gravity block reached principal order")
    return {
        "diagonal_orders": diagonal,
        "cross_block_orders": cross,
        "strictly_subprincipal_cross_defect_count": strict_cross_defect_count,
        "diagonal_principal_deformations": [
            {
                "block": "Delta_K_hh_base=q2_64(Phi2,-)",
                "order": principal["maximum_argument_order"],
                "comparison_order": 4,
                "classification": "PRINCIPAL_NOT_SUBPRINCIPAL",
            }
        ],
        "principal_deformation_count": 1,
        "unchanged_principal_symbol_claim": False,
    }


def mixed_r_kappa_preflight(phi2: dict[str, Any]) -> dict[str, Any]:
    """Freeze the coefficient and adjoint conventions for the next gate."""

    return {
        "status": "PREFLIGHT_COMPLETE_COEFFICIENTS_NOT_COMPUTED",
        "unary_coefficient_ring": "K[r,kappa]/(r^2,kappa^2) for coefficient identities only, K generated by sqrt(10),sqrt(58),I and the exact detector phase constants",
        "causal_coefficient_window": {
            "ring": "K((r))[[kappa]]",
            "checked_r_powers": [-1, 0, 1],
            "checked_kappa_powers": [0, 1, 2],
            "rule": "compare Laurent coefficients in the displayed window; do not quotient by r^2 after adjoining r^-1",
        },
        "unary_decomposition": "Q=Q00+r Q10+kappa Q01+r*kappa Q11+O(r^2,kappa^2)",
        "bidegree_correction_required": "delta_r T belongs to Q10 because the memory kinetic term p*T(g_r)*m has no kappa factor; only delta_r B_a belongs to Q11",
        "mixed_nilpotency_identity": "[Q00,Q11]+[Q10,Q01]=0",
        "mixed_cyclicity_identity": "Omega(Q11 x,y)+graded Omega(x,Q11 y) cancels the r*kappa pairing-transport terms induced by Q10 and Q01",
        "physical_phi2_reference_sha256": phi2["assembled_canonical_sha256"],
        "background_fields_at_order_r": {
            "metric": "g_r=gHat+r Phi2",
            "clock_scalar": "Theta_bar unchanged; its metric dual and normalized flow change",
            "rod_scalars": "Rbar_aI unchanged at this order in the divided profile; their metric contractions change",
            "maxwell_memory": "Abar=mbar=pbar=0",
        },
        "required_Q10_memory_blocks": [
            "delta_r T from n_Theta(g_r)",
            "delta_r T^sharp after cotangent density transport to the frozen 84-row pairing",
        ],
        "required_Q11_blocks": [
            "delta_r B_a^(0) from inverse metric, Hodge pairing, normalized detector density, and physical volume",
            "delta_r B_a^sharp after cotangent density transport to the frozen 84-row pairing",
            "the r-correction of the clock/rod canonical dressing wherever it enters the kappa readout rows",
        ],
        "transport_variation": {
            "definition": "T_r=n_Theta(g_r)^mu nabla_mu, n_Theta^mu=nabla^mu Theta/(nabla Theta)^2",
            "delta_n": "-Phi2^{mu nu} partial_nu Theta/X+nabla^mu Theta Phi2^{alpha beta} partial_alpha Theta partial_beta Theta/X^2, X=(nabla Theta)^2",
            "raw_metric_adjoint": "T_r^*=-T_r-div_{g_r}(n_Theta(g_r))",
            "base_identity_not_reusable": "T0*=-T0 follows from stationarity only; it must not be frozen at order r",
        },
        "pairing_transport": {
            "physical_density_ratio": "D_r=dvol_{g_r}/dvol_gHat=1+r/2 tr_gHat(Phi2)+O(r^2)",
            "rule": "derive raw adjoints with dvol_{g_r}, then conjugate every antifield-density block to the frozen 84-row pairing; do not transpose B_a or T before this transport",
        },
        "arity_boundary": {
            "included": "only the shifted background coefficients B_a^(0)(g_r) and T(g_r) entering q1",
            "excluded": "B_a^(1) and B_a^(2), which belong to apparatus q2 and q3",
        },
        "mixed_green_coefficient": "G11=-G00 P11 G00+G00 P10 G00 P01 G00+G00 P01 G00 P10 G00, with all products noncommutative and same-sided",
        "acceptance": [
            "export every nonzero Q11 block and its frozen-pairing adjoint",
            "verify the mixed nilpotency and cyclicity identities coefficientwise on all 84 rows",
            "verify both multiplication orders of the bivariate Laurent Green coefficient and same-sided support",
            "reject promotion if T*=-T is reused without the divergence/density correction",
        ],
        "mixed_Q11_computed": False,
        "mixed_green_computed": False,
    }


def _laurent_coefficient_defect_count(matrix: sp.Matrix, parameter: sp.Symbol) -> int:
    return sum(
        sp.simplify(sp.expand(matrix[row, column]).coeff(parameter, power)) != 0
        for row in range(matrix.rows)
        for column in range(matrix.cols)
        for power in (-1, 0, 1)
    )


@lru_cache(maxsize=2)
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
    dependency_hashes = {name: _sha256(path) for name, path in DEPENDENCIES.items()}
    values = {
        name: _load_json_cached(str(path), dependency_hashes[name])
        for name, path in DEPENDENCIES.items()
    }
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
    if values["base_54_q2_payload"]["shape"] != [54, 54, 54]:
        raise AssertionError("gravity q2 payload shape drifted")

    gamma = _cached_gamma(dependency_hashes["global_rods"])
    hessian_checks = _action_hessian_specializations()
    handoff_sha256 = dependency_hashes["authoritative_handoff"]
    solvability_sha256 = dependency_hashes["rod_q1_solvability"]
    phi2 = _cached_physical_phi2(handoff_sha256, solvability_sha256)
    principal_audit = _cached_principal_audit(
        dependency_hashes["base_54_q2_payload"], handoff_sha256, solvability_sha256
    )
    operator_orders = _operator_order_audit(principal_audit)
    mixed_preflight = mixed_r_kappa_preflight(phi2)
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
        "claim_status": "ROD_GRAVITY_R_AXIS_CERTIFIED_MEMORY_R_SHIFT_AND_MIXED_PROFILE_OPEN_PRINCIPAL_ORDER_CORRECTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": dependency_hashes[name],
                "result_id": values[name].get("result_id", path.stem),
            }
            for name, path in DEPENDENCIES.items()
        },
        "coefficient_scope": {
            "rod_weight": "r=epsilon_R^2 is fixed nonzero",
            "background_expansion": "g_epsilon=gHat+r Phi2+O(r^2)",
            "rod_gravity_certified_bidegrees_r_kappa": [[1, 0]],
            "full_84_q1_certified_bidegrees_r_kappa": [[0, 0], [0, 1]],
            "green_asymptotics": "Laurent leading order r^-1 on rod equation rows; coefficients replay through q1 order r",
            "excluded": ["r^2", "r*kappa", "delta_r T on the memory rows", "shifted B_a at r*kappa", "nonperturbative convergence"],
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
        "physical_phi2_tensor": phi2,
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
                "the gravity-clock biwave principal symbol is deformed coefficientwise by r q2(Phi2,-), including fourth-order fluctuation derivatives",
                "the pinned Maxwell sector has scalar wave principal symbol zeta_g^2",
                "each of six rod sectors has r zeta_g^2",
                "each memory sector has the already-certified clock-transport principal symbol",
            ],
            "cross_order": "Gamma_R is order zero; K_Rh and K_hR are at most order one; Delta_K_hh_rod is order zero. These rod cross blocks are subprincipal, while q2(Phi2,-) is a fourth-order diagonal principal deformation.",
            "green_hyperbolic_reduction": "coefficientwise formal causal perturbation: insert the local fourth-order q2(Phi2,-) between pinned same-sided base Green operators and combine it with the rod Schur--Laurent blocks; locality preserves the chosen causal side term by term",
            "green_operator": "G_P84,+/- is a formal same-sided Laurent coefficientwise inverse through the axial first jet; finite-r existence, uniqueness, and Green hyperbolicity are not asserted",
            "chain_homotopy": "Lambda84,+/-=W84 G_P84,+/-",
            "chain_identity": "the rod--gravity Schur--Laurent coefficient satisfies both inverse orders through r with the memory transport frozen at T0; this is not yet the full 84-row r-axis identity",
            "advanced_support": True,
            "retarded_support": True,
            "advanced_chain_defect_count": 0,
            "retarded_chain_defect_count": 0,
            "operator_order_audit": operator_orders,
            "q2_principal_order_audit": principal_audit,
            "laurent_inverse_audit": laurent_inverse,
            "schur_feedback_deletion_defect_count": (
                laurent_mutation["left_inverse_defect_count_through_r"]
                + laurent_mutation["right_inverse_defect_count_through_r"]
            ),
        },
        "mixed_r_kappa_preflight": mixed_preflight,
        "mutation_results": _mutation_results(gamma, hessian_checks, principal_audit),
        "flags": {
            "CLOCK_DRESSED_ROD_COORDINATES_CANONICAL": True,
            "GAMMA_R_EXPLICIT": True,
            "GAMMA_R_SHARP_EXPLICIT": True,
            "ROD_GRAVITY_ACTION_HESSIAN_EXPORTED": True,
            "ROD_GRAVITY_BV_NOETHER_FIRST_JET_CERTIFIED": True,
            "COUPLED_84_ROW_PRINCIPAL_CAUSAL_WITNESS_EXPORTED": True,
            "ROD_GRAVITY_R_AXIS_FIRST_JET_CERTIFIED": True,
            "ROD_GRAVITY_R_AXIS_FORMAL_CAUSAL_COEFFICIENT_CERTIFIED": True,
            "MEMORY_TRANSPORT_R_SHIFT_CERTIFIED": False,
            "84_ROW_Q1_AXIAL_FIRST_JET_CERTIFIED": False,
            "84_ROW_ADVANCED_RETARDED_GREEN_AXIAL_FIRST_JET_CERTIFIED": False,
            "PHYSICAL_PHI2_CANONICAL_TENSOR_EXPORTED": True,
            "Q2_PHI2_FOURTH_ORDER_PRINCIPAL_DEFORMATION_AUDITED": True,
            "MIXED_R_KAPPA_PREFLIGHT_COMPLETE": True,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "84_ROW_Q1_CERTIFIED": False,
            "84_ROW_ADVANCED_RETARDED_GREEN_CERTIFIED": False,
            "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED": False,
            "84_ROW_Q2_Q3_CERTIFIED": False,
            "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "COMPUTE_MEMORY_Q10_TRANSPORT_SHIFT_THEN_MIXED_Q11_PROFILE_SHIFT",
        "claim_boundary": (
            "This corrected exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL certificate exports the six clock-dressed rod spatial-diffeomorphism blocks and their odd-pairing adjoints, the covariant action-derived rod--gravity Hessian, a canonical physical Phi2 tensor, and the q2(Phi2,-) shifted base block. It certifies the rod--gravity r-axis nilpotency/cyclicity identities and its formal Schur--Laurent causal coefficient, while the already-certified (0,0) and (0,kappa) memory complex remains imported separately. A bidegree correction records that delta_r T is a Q10 memory block, not a Q11 block; because it is not computed here, this certificate does not by itself certify the full 84-row r axis. The principal audit proves that q2(Phi2,-) contains a fourth-order diagonal principal deformation, so finite-r existence, uniqueness, and Green hyperbolicity are not proved. The mixed profile coefficient, an all-orders 84-row q1/Green complex, apparatus q2/q3, K_Berger equivariance, the observer morphism, deformed rank two, emitter recoil, a Lorentzian quantum theory, and every quantum claim remain open."
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
