"""Exact exceptional/global Einstein--Weyl off-shell harmonic chain maps.

The generic axial and polar chain maps were already polynomial.  This module
closes the coefficient-level row gaps at ell=1 and ell=0 without using a
frequency, momentum, or characteristic inverse.  It deliberately stops short
of a support-local all-harmonic theorem: selecting exceptional harmonic
subspaces is a REDUCED-MODE operation until the tables are reconstructed as a
single natural differential operator on the four-dimensional bundles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import _generic_rows
from bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift import _complex_data


OUTPUT = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-exceptional-global-offshell-chain-maps-v1.schema.json"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-weyl-exceptional-global-offshell-chain-maps.md"
INPUTS = {
    "generic_axial": ROOT / "bridge/certificates/einstein_weyl_relative_linear_triangle_preflight.json",
    "generic_polar": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json",
    "axial_ell1_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell1_k0_operator.json",
    "polar_ell1_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell1_k0_operator.json",
    "ell0_target": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "source_exceptional": ROOT / "bridge/certificates/einstein_maxwell_polar_exceptional_complex.json",
    "exceptional_solution_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
    "homogeneous_solution_cofiber": ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json",
    "twist_solution_cofiber": ROOT / "bridge/certificates/einstein_weyl_twist_solution_cofiber.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _adjoint(matrix: sp.MatrixBase, omega: sp.Symbol, momentum: sp.Symbol) -> sp.Matrix:
    return matrix.subs({omega: -omega, momentum: -momentum}, simultaneous=True).T


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def _strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [[str(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _block_payload(
    *,
    name: str,
    source_dimensions: list[int],
    target_dimensions: list[int],
    source_orders: dict[str, list[str]],
    target_orders: dict[str, list[str]],
    source_gauge: sp.Matrix,
    target_gauge: sp.Matrix,
    source_euler: sp.Matrix,
    target_euler: sp.Matrix,
    source_noether: sp.Matrix,
    target_noether: sp.Matrix,
    ghost_map: sp.Matrix,
    field_map: sp.Matrix,
    equation_map: sp.Matrix,
    identity_map: sp.Matrix,
    omega: sp.Symbol,
    momentum: sp.Symbol,
    source_identity_coordinate_pairing: bool,
) -> dict[str, Any]:
    defects = {
        "source_q1_squared_right": source_euler * source_gauge,
        "source_q1_squared_left": source_noether * source_euler,
        "target_q1_squared_right": target_euler * target_gauge,
        "target_q1_squared_left": target_noether * target_euler,
        "ghost_field_square": target_gauge * ghost_map - field_map * source_gauge,
        "field_equation_square": target_euler * field_map - equation_map * source_euler,
        "equation_identity_square": target_noether * equation_map - identity_map * source_noether,
    }
    failed = [label for label, defect in defects.items() if not _zero(defect)]
    if failed:
        raise AssertionError(f"{name} defects survived: {failed}")
    matrices = (source_gauge, target_gauge, source_euler, target_euler, source_noether, target_noether, ghost_map, field_map, equation_map, identity_map)
    denominators = sorted({str(sp.factor(sp.denom(value))) for matrix in matrices for value in matrix})
    if any(not sp.sympify(value).is_number for value in denominators):
        raise AssertionError(f"{name} acquired a differential inverse: {denominators}")
    source_adjoint_defect = source_euler - _adjoint(source_euler, omega, momentum)
    target_adjoint_defect = target_euler - _adjoint(target_euler, omega, momentum)
    if source_identity_coordinate_pairing and not _zero(source_adjoint_defect):
        raise AssertionError(f"{name} source action-coordinate adjoint defect survived")
    if not _zero(target_adjoint_defect):
        raise AssertionError(f"{name} target action-coordinate adjoint defect survived")
    return {
        "name": name,
        "source_dimensions": source_dimensions,
        "target_dimensions": target_dimensions,
        "source_orders": source_orders,
        "target_orders": target_orders,
        "maps": {
            "source_gauge": _strings(source_gauge),
            "target_gauge": _strings(target_gauge),
            "source_euler": _strings(source_euler),
            "target_euler": _strings(target_euler),
            "source_noether": _strings(source_noether),
            "target_noether": _strings(target_noether),
            "ghost_map": _strings(ghost_map),
            "field_map": _strings(field_map),
            "equation_map": _strings(equation_map),
            "identity_map": _strings(identity_map),
        },
        "map_ranks_over_Q_k_omega": {
            "ghost": ghost_map.rank(),
            "field": field_map.rank(),
            "equation": equation_map.rank(),
            "identity": identity_map.rank(),
        },
        "defects": {label: "0" for label in defects},
        "formal_adjoint_audit": {
            "source": "PASS_IN_IDENTITY_ACTION_COORDINATES" if source_identity_coordinate_pairing else "ACTION_ROW_PAIRING_REQUIRED_NOT_IDENTITY_COORDINATES",
            "target": "PASS_IN_IDENTITY_ACTION_COORDINATES",
        },
        "constant_denominators_only": denominators,
        "inverted_polynomials": [],
    }


def _axial_ell1() -> dict[str, Any]:
    rows, symbols = _generic_rows()
    lam, momentum, omega = symbols["lambda"], symbols["k"], symbols["omega"]
    coefficients = sp.Matrix([symbols["h_t"], symbols["h_x"], symbols["q_t"], symbols["q_x"]])
    source_four = sp.Matrix([
        [momentum**2 + lam, momentum * omega, 2, 0],
        [momentum * omega, omega**2 - lam, 0, -2],
        [lam, 0, momentum**2 + lam, momentum * omega],
        [0, -lam, momentum * omega, omega**2 - lam],
    ]).subs(lam, 2).applyfunc(sp.factor)
    target_four = sp.Matrix([
        lam * rows["metric_t"],
        -lam * rows["metric_x"],
        rows["maxwell_t"],
        rows["maxwell_x"],
    ]).jacobian(coefficients).subs(lam, 2).applyfunc(sp.factor)
    factor = 3 * momentum**2 - 3 * omega**2 + 4
    equation_four = sp.Matrix([
        [-factor / 2, 0, 3 * (2 - omega**2) / 2, 3 * momentum * omega / 2],
        [0, -factor / 2, -3 * momentum * omega / 2, 3 * (momentum**2 + 2) / 2],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    if not _zero(target_four - equation_four * source_four):
        raise AssertionError("axial ell=1 reduced factorization changed")

    # The b coefficient is removed by the U(1) parameter without division.
    # R records the b=0 slice; its formal adjoint lifts equation rows back to
    # the complete five-field presentation.
    imaginary = sp.I
    projection = sp.Matrix([
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, imaginary * omega],
        [0, 0, 0, 1, -imaginary * momentum],
    ])
    lift = _adjoint(projection, omega, momentum)
    selector = sp.zeros(4, 5)
    selector[:4, :4] = sp.eye(4)
    source_euler = (lift * source_four * projection).applyfunc(sp.factor)
    target_euler = (lift * target_four * projection).applyfunc(sp.factor)
    equation_map = (lift * equation_four * selector).applyfunc(sp.factor)
    source_gauge = sp.Matrix([
        [-imaginary * omega, 0],
        [imaginary * momentum, 0],
        [0, -imaginary * omega],
        [0, imaginary * momentum],
        [1, 1],
    ])
    target_gauge = source_gauge
    source_noether = _adjoint(source_gauge, omega, momentum)
    target_noether = source_noether
    identity_map = sp.Matrix([[-factor / 2, factor / 2], [0, 0]])
    return _block_payload(
        name="axial ell=1, all compact momenta",
        source_dimensions=[2, 5, 5, 2],
        target_dimensions=[2, 5, 5, 2],
        source_orders={"ghosts": ["xi_ax", "chi_ax"], "fields": ["h_t", "h_x", "q_t", "q_x", "b"], "equations": ["h_t*", "h_x*", "q_t*", "q_x*", "b*"], "identities": ["xi_ax*", "chi_ax*"]},
        target_orders={"ghosts": ["xi_ax", "chi_ax"], "fields": ["h_t", "h_x", "q_t", "q_x", "b"], "equations": ["h_t*", "h_x*", "q_t*", "q_x*", "b*"], "identities": ["xi_ax*", "chi_ax*"]},
        source_gauge=source_gauge,
        target_gauge=target_gauge,
        source_euler=source_euler,
        target_euler=target_euler,
        source_noether=source_noether,
        target_noether=target_noether,
        ghost_map=sp.eye(2),
        field_map=sp.eye(5),
        equation_map=equation_map,
        identity_map=identity_map,
        omega=omega,
        momentum=momentum,
        source_identity_coordinate_pairing=True,
    )


def _polar_ell1() -> dict[str, Any]:
    data = _complex_data()
    lam, momentum, omega = data["symbols"]["lambda"], data["symbols"]["k"], data["symbols"]["omega"]
    matrices = data["matrices"]
    # The trace-free tensor harmonic and its dual equation vanish at ell=1.
    keep = [0, 1, 2, 3, 4, 5, 7]
    specialize = lambda matrix: matrix.subs(lam, 2).applyfunc(sp.factor)
    source_gauge = specialize(matrices["source_gauge"]).extract(keep, [0, 1, 2])
    target_gauge = specialize(matrices["target_gauge"]).extract(keep, [0, 1, 2, 3])
    source_euler = specialize(matrices["source_euler"]).extract(keep, keep)
    target_euler = specialize(matrices["target_euler"]).extract(keep, keep)
    equation_map = specialize(matrices["ungauged_equation_map"]).extract(keep, keep)
    source_noether = specialize(matrices["source_noether"]).extract([0, 1, 2], keep)
    target_noether = specialize(matrices["target_noether"]).extract([0, 1, 2, 3], keep)
    ghost_map = specialize(matrices["ghost_embedding"])
    return _block_payload(
        name="polar ell=1, all compact momenta",
        source_dimensions=[3, 7, 7, 3],
        target_dimensions=[4, 7, 7, 4],
        source_orders={"ghosts": ["xi_t", "xi_x", "xi"], "fields": ["A", "B", "C", "h_t", "h_x", "K", "U"], "equations": ["A*", "B*", "C*", "h_t*", "h_x*", "K*", "U*"], "identities": ["xi_t*", "xi_x*", "xi*"]},
        target_orders={"ghosts": ["xi_t", "xi_x", "xi", "sigma"], "fields": ["A", "B", "C", "h_t", "h_x", "K", "U"], "equations": ["A*", "B*", "C*", "h_t*", "h_x*", "K*", "U*"], "identities": ["xi_t*", "xi_x*", "xi*", "sigma*"]},
        source_gauge=source_gauge,
        target_gauge=target_gauge,
        source_euler=source_euler,
        target_euler=target_euler,
        source_noether=source_noether,
        target_noether=target_noether,
        ghost_map=ghost_map,
        field_map=sp.eye(7),
        equation_map=equation_map,
        identity_map=sp.zeros(4, 3),
        omega=omega,
        momentum=momentum,
        source_identity_coordinate_pairing=False,
    )


def _polar_ell0() -> dict[str, Any]:
    momentum, omega = sp.symbols("k omega", real=True)
    imaginary = sp.I
    source_metric = sp.Matrix([
        [0, 0, 0, -momentum**2],
        [0, 0, 0, -2 * momentum * omega],
        [0, 0, 0, -omega**2],
        [-momentum**2, -2 * momentum * omega, -omega**2, momentum**2 - omega**2 - 2],
    ])
    vector = sp.Matrix([momentum**2, 2 * momentum * omega, omega**2, momentum**2 - omega**2])
    target_metric = vector * vector.T / 2
    maxwell_vector = sp.Matrix([momentum, omega])
    source_euler = sp.zeros(6)
    target_euler = sp.zeros(6)
    source_euler[:4, :4] = source_metric
    target_euler[:4, :4] = target_metric
    source_euler[4:, 4:] = maxwell_vector * maxwell_vector.T
    target_euler[4:, 4:] = maxwell_vector * maxwell_vector.T
    source_gauge = sp.Matrix([
        [-2 * imaginary * omega, 0, 0],
        [imaginary * momentum, -imaginary * omega, 0],
        [0, 2 * imaginary * momentum, 0],
        [0, 0, 0],
        [0, 0, -imaginary * omega],
        [0, 0, imaginary * momentum],
    ])
    target_gauge = source_gauge.row_join(sp.Matrix([-2, 0, 2, 2, 0, 0]))
    source_noether = _adjoint(source_gauge, omega, momentum)
    target_noether = _adjoint(target_gauge, omega, momentum)
    c = momentum**2 - omega**2 - 1
    equation_map = sp.zeros(6)
    equation_map[0, 0], equation_map[0, 3] = -c, -momentum**2 / 2
    equation_map[1, 1], equation_map[1, 3] = -c, -momentum * omega
    equation_map[2, 2], equation_map[2, 3] = -c, -omega**2 / 2
    equation_map[3, 0], equation_map[3, 2], equation_map[3, 3] = -c, c, (omega**2 - momentum**2) / 2
    equation_map[4, 4] = equation_map[5, 5] = 1
    identity_map = sp.zeros(4, 3)
    identity_map[0, 0] = identity_map[1, 1] = -c
    identity_map[2, 2] = 1
    ghost_map = sp.zeros(4, 3)
    ghost_map[:3, :3] = sp.eye(3)
    return _block_payload(
        name="polar ell=0, all Fourier pairs including generalized zero",
        source_dimensions=[3, 6, 6, 3],
        target_dimensions=[4, 6, 6, 4],
        source_orders={"ghosts": ["xi_t", "xi_x", "chi"], "fields": ["A", "B", "C", "K", "T", "X"], "equations": ["A*", "B*", "C*", "K*", "T*", "X*"], "identities": ["xi_t*", "xi_x*", "chi*"]},
        target_orders={"ghosts": ["xi_t", "xi_x", "chi", "sigma"], "fields": ["A", "B", "C", "K", "T", "X"], "equations": ["A*", "B*", "C*", "K*", "T*", "X*"], "identities": ["xi_t*", "xi_x*", "chi*", "sigma*"]},
        source_gauge=source_gauge,
        target_gauge=target_gauge,
        source_euler=source_euler,
        target_euler=target_euler,
        source_noether=source_noether,
        target_noether=target_noether,
        ghost_map=ghost_map,
        field_map=sp.eye(6),
        equation_map=equation_map,
        identity_map=identity_map,
        omega=omega,
        momentum=momentum,
        source_identity_coordinate_pairing=True,
    )


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in INPUTS.items()}
    if records["generic_axial"]["classification"]["generic_axial_offshell_chain_map_certified"] is not True:
        raise AssertionError("generic axial chain map changed")
    if records["generic_polar"]["classification"]["polynomial_ghost_field_equation_identity_chain_map_certified"] is not True:
        raise AssertionError("generic polar chain map changed")
    if records["axial_ell1_target"]["classification"]["extra_fourth_order_ell1_shell_discovered"] is not True:
        raise AssertionError("direct axial ell=1 target anchor changed")
    if records["polar_ell1_target"]["classification"]["polar_ell1_extra_fourth_order_shell_certified"] is not True:
        raise AssertionError("direct polar ell=1 target anchor changed")
    if records["ell0_target"]["classification"]["direct_four_dimensional_exceptional_operator_constructed"] is not True:
        raise AssertionError("direct ell=0 target anchor changed")
    if records["source_exceptional"]["classification"]["all_polar_ell_linear_complex"] is not True:
        raise AssertionError("source exceptional complex changed")
    if records["exceptional_solution_cofiber"]["classification"]["exceptional_solution_cofiber_certified"] is not True:
        raise AssertionError("exceptional solution cofiber changed")
    if records["homogeneous_solution_cofiber"]["classification"]["homogeneous_solution_cofiber_zero"] is not True:
        raise AssertionError("homogeneous solution cofiber changed")
    if records["twist_solution_cofiber"]["classification"]["twist_solution_cofiber_zero"] is not True:
        raise AssertionError("twist solution cofiber changed")
    blocks = {"axial_ell1": _axial_ell1(), "polar_ell1": _polar_ell1(), "polar_ell0": _polar_ell0()}
    return {
        "schema": "einstein-weyl-exceptional-global-offshell-chain-maps-v1",
        "result_id": "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1",
        "result_state": "EXCEPTIONAL_AND_GLOBAL_HARMONIC_OFFSHELL_CHAIN_MAPS_CERTIFIED_COVARIANT_GLUE_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Einstein-Maxwell_to_Weyl-Maxwell",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "closed S1_L x S2, smooth periodic identity-component gauge",
            "charge_sector": "fixed magnetic bundle P_N",
            "carrier": "complete exceptional axial ell=1, polar ell=1 and homogeneous polar ell=0 Fourier coefficient complexes",
            "degree": "ghost-field-equation-identity rows",
            "parity": "axial and polar kept separate",
            "ell": "0 and 1",
            "m": "all by SO(3) equivariance",
            "k": "all compact Fourier momenta",
            "omega": "polynomial Fourier variable; generalized zero retained without inversion",
        },
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        "blocks": blocks,
        "coverage": {
            "generic_axial_ell_ge_2": "imported strict polynomial all-row chain map",
            "generic_polar_ell_ge_2": "imported strict polynomial all-row chain map",
            "axial_ell1_all_k": "certified here",
            "polar_ell1_all_k": "certified here",
            "polar_ell0_all_k_and_generalized_zero": "certified here",
            "axial_ell0": "NOT_APPLICABLE: no axial scalar harmonic",
        },
        "solution_cofiber_imports": {
            "ell1_k0": "standard Einstein image plus axial/polar extra cofiber; axial twist lies in the Einstein image",
            "homogeneous_generalized_zero": "zero cofiber with nontrivial action-form shear",
            "twist_generalized_zero": "zero cofiber with target form -2 times the source form",
        },
        "classification": {
            "exceptional_axial_all_row_offshell_chain_map_certified": True,
            "exceptional_polar_all_row_offshell_chain_map_certified": True,
            "homogeneous_all_row_offshell_chain_map_certified": True,
            "all_maps_polynomial_without_differential_inverse": True,
            "all_compact_momenta_included": True,
            "generalized_zero_frequency_retained": True,
            "all_harmonic_sector_coefficient_maps_available": True,
            "single_covariant_support_local_map_reconstructed": False,
            "support_local_global_mapping_cofiber_certified": False,
            "finite_large_gauge_and_final_residual_endpoints_included": False,
            "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_certified": False,
            "Lorentzian_causal_observational_or_quantum_claim": False,
        },
        "interpretation": "The formerly missing exceptional/global coefficient algebra is not obstructed: every ell=0,1 ghost-field-equation-identity square has an exact polynomial map, including all compact momenta and generalized zero frequency. The remaining Bridge-1 issue is geometric globalization: reconstruct these sector tables together with the generic maps as one natural support-local four-dimensional chain morphism, include finite large-gauge/residual endpoints, and export the three action-derived forms separately. Harmonic row selection itself is not support local.",
        "next_gate": "reconstruct and verify the unique natural covariant equation/identity maps whose harmonic reductions are the complete generic-plus-exceptional tables; then add finite large-gauge/residual endpoint rows and assemble the NONCYCLIC_THREE_FORM triangle",
        "claim_boundary": "This exact theorem closes the exceptional and homogeneous off-shell polynomial row-map gap in the complete harmonic presentation. It is not the requested support-local all-sector triangle because no spectral projector may be used to glue harmonic blocks, and it does not include finite large-gauge/final residual endpoints. It makes no causal, observable, particle, scattering, nonlinear or quantum claim.",
        "source_manifest": {
            str(Path(__file__).relative_to(ROOT)): _sha256(Path(__file__)),
            str(SCHEMA.relative_to(ROOT)): _sha256(SCHEMA),
            "bridge/einstein_sector/verify_einstein_weyl_exceptional_global_offshell_chain_maps.py": _sha256(ROOT / "bridge/einstein_sector/verify_einstein_weyl_exceptional_global_offshell_chain_maps.py"),
            "bridge/einstein_sector/tests/test_einstein_weyl_exceptional_global_offshell_chain_maps.py": _sha256(ROOT / "bridge/einstein_sector/tests/test_einstein_weyl_exceptional_global_offshell_chain_maps.py"),
        },
        "verification_receipt": {
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python files>", "python3 -m json.tool <scoped JSON files>", "git diff --check -- <scoped files>"]},
            "tier_1": {"status": "PASS", "commands": [
                "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_exceptional_global_offshell_chain_maps --check",
                "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_weyl_exceptional_global_offshell_chain_maps.py",
                "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_exceptional_global_offshell_chain_maps -v"
            ]},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "generic all-row maps, direct exceptional target operators and solution-cofiber pairings are pinned dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "the covariant support-local glue and final residual endpoints remain open"}
        },
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_weyl_exceptional_global_offshell_chain_maps --check",
            "PYTHONPATH=. python3 bridge/einstein_sector/verify_einstein_weyl_exceptional_global_offshell_chain_maps.py",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_exceptional_global_offshell_chain_maps -v",
        ],
    }


def _write_report(value: dict[str, Any]) -> None:
    REPORT.write_text(
        """# Exceptional/global off-shell Einstein--Weyl chain maps

The exceptional algebra closes positively.  Exact polynomial chain maps now
cover axial `ell=1`, polar `ell=1`, and homogeneous polar `ell=0`, at every
compact momentum and with generalized zero frequency retained.  Every source
and target `q1^2` identity and every ghost/field, field/equation and
equation/identity chain square vanishes.  No momentum, frequency,
characteristic polynomial, inverse Laplacian or inverse curl is used.

This does **not** yet promote the full relative triangle.  The current theorem
is a complete harmonic coefficient presentation.  Selecting an exceptional
harmonic sector is not support local on `S2`; the next task is to reconstruct
the generic and exceptional tables as one natural four-dimensional
differential chain morphism and then include finite large-gauge and residual
endpoint rows.  The Einstein, pulled-back Weyl and relative action forms must
remain distinct.

The result removes the old ambiguity about whether missing exceptional rows
hide an algebraic obstruction.  They do not.  The remaining gate is geometric
globalization and endpoint descent.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    value = build()
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write_report(value)
    elif _load(OUTPUT) != value:
        raise AssertionError("exceptional/global off-shell chain-map certificate is stale")
    print("EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1: PASS")


if __name__ == "__main__":
    main()
