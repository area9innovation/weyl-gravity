"""Exact external-source Ward chain map for the compensated Einstein defect.

This theorem is deliberately universal and kinematic.  It constructs the
Diff x Weyl Ward complex of an external source multiplet (T_mn,J_phi), the
Bach-obstruction chain map Q(T), and the affine Einstein-defect map.  It does
not pretend that external sources are dynamical BV fields: a matter-inclusive
BV lift still requires a selected matter action and its Euler/ghost/antifield
rows.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.verify_compensated_minimal_bv_operator_export import (
    load_verified_export,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/compensated_sourced_defect_chain_map.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/compensated_sourced_defect_chain_map.schema.json"
OPERATOR_EXPORT = ROOT / "bridge/certificates/compensated_minimal_bv_operator_export.json"
PREFLIGHT = ROOT / "bridge/certificates/compensated_einstein_sourced_defect_preflight.json"
CHARACTERISTIC_SNAPSHOT = ROOT / "bridge/certificates/compensated_nonzero_characteristic_snapshot.json"
BERGER_MINIMAL_BV_SDR = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json"


class SourcedDefectChainMapError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SourcedDefectChainMapError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _zero(matrix: sp.MatrixBase) -> bool:
    return sp.SparseMatrix(matrix.applyfunc(sp.simplify)).nnz() == 0


def _record(matrix: sp.MatrixBase) -> dict[str, Any]:
    entries = [
        [row, column, str(sp.factor(value))]
        for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
    ]
    body = {"shape": list(matrix.shape), "entries": entries}
    digest = hashlib.sha256(json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
    return {**body, "sha256": digest}


def _tensor_matrix(vector: sp.Matrix, pairs: tuple[tuple[int, int], ...]) -> sp.Matrix:
    index = {pair: position for position, pair in enumerate(pairs)}
    return sp.Matrix(4, 4, lambda mu, nu: vector[index[(min(mu, nu), max(mu, nu))]])


def _tensor_vector(tensor: sp.Matrix, pairs: tuple[tuple[int, int], ...]) -> sp.Matrix:
    return sp.Matrix([tensor[mu, nu] for mu, nu in pairs])


@functools.lru_cache(maxsize=1)
def _build_exact_data() -> dict[str, Any]:
    _, exported, symbols = load_verified_export(OPERATOR_EXPORT)
    p = sp.Matrix([symbols[f"p{i}"] for i in range(4)])
    c1, alpha, v = symbols["c1"], symbols["alpha"], symbols["v"]
    eta = sp.diag(1, -1, -1, -1)
    p_up = eta * p
    p_squared = sp.expand((p.T * p_up)[0])
    pairs = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))

    tensor_symbols = sp.Matrix(sp.symbols("x0:10"))
    tensor = _tensor_matrix(tensor_symbols, pairs)
    trace = sp.expand(sum(eta[mu, nu] * tensor[mu, nu] for mu in range(4) for nu in range(4)))
    divergence = sp.Matrix([
        sp.expand(sum(p_up[mu] * tensor[mu, nu] for mu in range(4)))
        for nu in range(4)
    ])
    divergence_matrix = divergence.jacobian(tensor_symbols)
    trace_matrix = sp.Matrix([trace]).jacobian(tensor_symbols)

    h_trace = trace
    h_divergence = divergence
    ricci = sp.Matrix(4, 4, lambda mu, nu: sp.expand(sp.Rational(1, 2) * (
        p[mu] * h_divergence[nu] + p[nu] * h_divergence[mu]
        - p_squared * tensor[mu, nu] - p[mu] * p[nu] * h_trace
    )))
    scalar = sp.expand(sum(eta[mu, nu] * ricci[mu, nu] for mu in range(4) for nu in range(4)))
    einstein_tensor = sp.Matrix(4, 4, lambda mu, nu: sp.expand(
        ricci[mu, nu] - sp.Rational(1, 2) * eta[mu, nu] * scalar
    ))
    einstein = _tensor_vector(einstein_tensor, pairs).jacobian(tensor_symbols)

    q_tensor = sp.Matrix(4, 4, lambda mu, nu: sp.expand(
        sp.Rational(1, 2) * p_squared * tensor[mu, nu]
        - sp.Rational(1, 6) * (eta[mu, nu] * p_squared - p[mu] * p[nu]) * trace
    ))
    obstruction = _tensor_vector(q_tensor, pairs).jacobian(tensor_symbols)

    _require(_zero(divergence_matrix * einstein), "linearized Bianchi identity failed")
    _require(_zero(trace_matrix * obstruction), "Q(T) is not traceless")
    _require(
        _zero(divergence_matrix * obstruction - sp.Rational(1, 2) * p_squared * divergence_matrix),
        "Q does not intertwine the divergence Ward row",
    )

    metric_operator = exported["metric_operator"]
    _require(
        _zero(metric_operator - (c1 * einstein + 2 * alpha * obstruction * einstein)),
        "independently exported Einstein--Weyl operator does not factor through QG",
    )
    diff_gauge = exported["gauge"][:10, :4]
    _require(_zero(einstein * diff_gauge), "G R_diff != 0")

    source_ward = sp.zeros(5, 11)
    source_ward[:4, :10] = divergence_matrix
    source_ward[4, :10] = trace_matrix
    source_ward[4, 10] = -v

    obstruction_map = sp.zeros(10, 11)
    obstruction_map[:, :10] = obstruction
    obstruction_ward = divergence_matrix.col_join(trace_matrix)
    obstruction_on_ward = sp.zeros(5)
    obstruction_on_ward[:4, :4] = sp.Rational(1, 2) * p_squared * sp.eye(4)
    _require(
        _zero(obstruction_ward * obstruction_map - obstruction_on_ward * source_ward),
        "source-to-obstruction Ward square does not commute",
    )

    augmented_ward = sp.zeros(5, 21)
    augmented_ward[:, 10:21] = source_ward
    defect_map = sp.zeros(10, 21)
    defect_map[:, :10] = einstein
    defect_map[:, 10:20] = -sp.eye(10) / c1
    defect_on_ward = sp.zeros(4, 5)
    defect_on_ward[:, :4] = -sp.eye(4) / c1
    _require(
        _zero(divergence_matrix * defect_map - defect_on_ward * augmented_ward),
        "Einstein-defect divergence Ward square does not commute",
    )

    augmented_gauge = sp.zeros(21, 4)
    augmented_gauge[:10, :] = diff_gauge
    _require(_zero(defect_map * augmented_gauge), "Einstein defect is not Diff gauge invariant")
    _require(_zero(augmented_ward * augmented_gauge), "source Ward map does not annihilate gauge image")

    defect_operator = c1 * sp.eye(10) + 2 * alpha * obstruction
    obstruction_extended = sp.zeros(10, 21)
    obstruction_extended[:, 10:21] = obstruction_map
    ew_residual = sp.zeros(10, 21)
    ew_residual[:, :10] = metric_operator
    ew_residual[:, 10:20] = -sp.eye(10)
    _require(
        _zero(ew_residual - defect_operator * defect_map - 2 * alpha * obstruction_extended / c1),
        "sourced defect equation does not reconstruct the Einstein--Weyl residual",
    )

    dressed_source = sp.eye(11)
    dressed_source[:10, :10] += 2 * alpha * obstruction / c1
    dressed_ward = sp.eye(5)
    dressed_ward[:4, :4] *= 1 + alpha * p_squared / c1
    _require(_zero(source_ward * dressed_source - dressed_ward * source_ward), "dressed source is not a Ward-complex endomorphism")

    matrices = {
        "divergence": divergence_matrix,
        "trace": trace_matrix,
        "linearized_einstein": einstein,
        "source_obstruction_Q": obstruction,
        "source_ward": source_ward,
        "obstruction_map": obstruction_map,
        "obstruction_ward": obstruction_ward,
        "obstruction_on_ward": obstruction_on_ward,
        "augmented_ward": augmented_ward,
        "einstein_defect": defect_map,
        "defect_on_ward": defect_on_ward,
        "augmented_diff_gauge": augmented_gauge,
        "defect_operator": defect_operator,
        "einstein_weyl_residual": ew_residual,
        "dressed_source": dressed_source,
        "dressed_ward": dressed_ward,
    }
    return {"symbols": symbols, "pairs": pairs, "matrices": matrices}


def _compatible_source_fiber(data: dict[str, Any], name: str, momentum: tuple[int, int, int, int]) -> dict[str, Any]:
    symbols = data["symbols"]
    substitution = {
        symbols["p0"]: momentum[0], symbols["p1"]: momentum[1],
        symbols["p2"]: momentum[2], symbols["p3"]: momentum[3],
        symbols["c1"]: -1, symbols["alpha"]: -1, symbols["v"]: 1,
    }
    ward = sp.Matrix(data["matrices"]["source_ward"].subs(substitution))
    obstruction = sp.Matrix(data["matrices"]["obstruction_map"].subs(substitution))
    combined = ward.col_join(obstruction)
    columns = combined.nullspace()
    inclusion = sp.Matrix.hstack(*columns) if columns else sp.zeros(11, 0)
    _require(_zero(ward * inclusion), f"Ward violation in {name} compatible-source basis")
    _require(_zero(obstruction * inclusion), f"Q(T) violation in {name} compatible-source basis")
    return {
        "name": name,
        "parameters": {"p": list(momentum), "p_squared": momentum[0] ** 2 - sum(x * x for x in momentum[1:]), "v": 1},
        "ward_rank": ward.rank(),
        "ward_cycle_dimension": 11 - ward.rank(),
        "combined_constraint_rank": combined.rank(),
        "compatible_source_dimension": inclusion.cols,
        "compatible_source_inclusion": _record(inclusion),
        "status": "PASS",
    }


def build_certificate() -> dict[str, Any]:
    preflight = _load(PREFLIGHT)
    snapshot = _load(CHARACTERISTIC_SNAPSHOT)
    berger = _load(BERGER_MINIMAL_BV_SDR)
    _require(preflight.get("verdict") == "ARBITRARY_SAME_SOURCE_EINSTEIN_TRUNCATION_REFUTED_LINEAR_FLAT", "preflight verdict changed")
    _require(snapshot.get("result_state") == "SCOPED_EXACT_SNAPSHOT_CERTIFIED_GLOBAL_CLASSICAL_FREEZE_OPEN", "characteristic scope changed")
    _require(
        berger.get("result_id") == "BERGER_MINIMAL_BV_CLOCK_SDR"
        and berger.get("claim_status") == "CERTIFIED_MINIMAL_CLOCK_SECTOR_SDR"
        and berger.get("flags", {}).get("support_local_clock_SDR_exact") is True
        and berger.get("flags", {}).get("retained_dressed_metric_q1_coefficients_complete") is False
        and berger.get("flags", {}).get("gauge_fixed_nonminimal_rows_complete") is False,
        "Berger minimal-BV contextual gate changed",
    )
    data = _build_exact_data()
    generic = _compatible_source_fiber(data, "generic_noncharacteristic", (2, 1, 0, 0))
    null = _compatible_source_fiber(data, "nonzero_null", (1, 0, 0, 1))
    zero = _compatible_source_fiber(data, "zero_symbol_ledger", (0, 0, 0, 0))
    _require(generic["compatible_source_dimension"] == 1, "generic compatible-source dimension changed")
    _require(null["compatible_source_dimension"] == 5, "null compatible-source dimension changed")
    _require(zero["compatible_source_dimension"] == 10, "zero compatible-source ledger changed")

    records = {name: _record(matrix) for name, matrix in data["matrices"].items()}
    payload = {
        "schema": "compensated-sourced-defect-chain-map-v1",
        "schema_path": "bridge/einstein_sector/schema/compensated_sourced_defect_chain_map.schema.json",
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_EXTERNAL_SOURCE_DEFECT_CHAIN_MAP",
        "result_state": "UNIVERSAL_SOURCE_WARD_CHAIN_MAP_CERTIFIED_MATTER_BV_LIFT_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "0cf75919f37b03328720fa86653ce245f2cfe365",
            "generator_path": "bridge/einstein_sector/compensated_sourced_defect_chain_map.py",
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            "operator_export": {"path": str(OPERATOR_EXPORT.relative_to(ROOT)), "sha256": _sha256(OPERATOR_EXPORT)},
            "sourced_defect_preflight": {"path": str(PREFLIGHT.relative_to(ROOT)), "sha256": _sha256(PREFLIGHT)},
            "characteristic_snapshot": {"path": str(CHARACTERISTIC_SNAPSHOT.relative_to(ROOT)), "sha256": _sha256(CHARACTERISTIC_SNAPSHOT)},
            "berger_minimal_bv_clock_sdr": {"path": str(BERGER_MINIMAL_BV_SDR.relative_to(ROOT)), "sha256": _sha256(BERGER_MINIMAL_BV_SDR)},
        },
        "domain": {
            "spacetime": "four-dimensional Minkowski space",
            "phase": "constant compensator phi=v!=0",
            "source_space": "external spurion multiplets (T_mn,J_phi), not dynamical matter fields",
            "source_ward_map": "(T,J)->(partial^m T_mn, tr(T)-v J)",
            "defect": "Delta=G1(h_hat)-T/c1",
            "coefficient_ring": "Q(c1,alpha,v,v^-1)[p0,p1,p2,p3]",
        },
        "chain_map_theorem": {
            "obstruction_square": "W_B Q_ext = diag((p_squared/2)I4,0) W_source",
            "defect_square": "div Delta = -(1/c1) projection_div W_source",
            "gauge_identity": "Delta(R_diff xi,0,0)=0",
            "residual_identity": "E_EW=(c1 I+2 alpha Q)Delta+(2 alpha/c1)Q(T)",
            "on_shell_defect_equation": "(c1 I+2 alpha Q)Delta=-(2 alpha/c1)Q(T)",
            "same_source_closure": "Delta=0 is Einstein--Weyl on shell if and only if Q(T)=0",
            "dressed_source_endomorphism": "T_EW=T+(2 alpha/c1)Q(T), J_EW=J is a Ward-complex chain map but changes the coupling",
            "status": "PASS",
        },
        "matrix_export": records,
        "compatible_source_fibers": {"generic": generic, "null": null, "zero": zero},
        "classification": {
            "universal_result": "external-source Ward and defect chain maps",
            "external_source_geometry": "for fixed nonzero source, the field solution locus remains affine",
            "not_a_bv_complex_reason": "T and J have no declared kinetic equations, matter gauge symmetries, ghosts, or antifields",
            "model_dependent_next_lift": "choose a matter action (the Berger conformal-scalar model is one candidate), construct its full BV rows, and prove that its stress/source map intertwines the matter BV differential with this universal Ward complex",
            "berger_context": "the Berger team has certified an eight-row support-local minimal clock SDR, but the retained 26-row q1 coefficients and nonminimal rows required for a full matter-BV lift remain open",
        },
        "verdict": "SOURCE_WARD_TO_EINSTEIN_DEFECT_CHAIN_MAP_EXACT_GENERIC_MATTER_BV_NOT_UNIVERSAL",
        "claim_flags": {
            "canonical_compensated_operator_export_imported": True,
            "source_ward_complex_constructed": True,
            "bach_obstruction_chain_map_exact": True,
            "einstein_defect_chain_map_exact": True,
            "sourced_defect_residual_identity_exact": True,
            "compatible_source_kernel_representatives_exact": True,
            "dressed_source_ward_endomorphism_exact": True,
            "berger_minimal_clock_sdr_imported": True,
            "arbitrary_ward_cycle_is_einstein_compatible": False,
            "fixed_external_source_locus_is_bv_subcomplex": False,
            "matter_inclusive_bv_complex_constructed": False,
            "berger_matter_bv_lift_constructed": False,
            "retarded_advanced_defect_propagation_proved": False,
            "nonlinear_closure_proved": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "missing_object_ledger": [
            "select and import a dynamical matter action with exact provenance",
            "construct matter Euler, gauge, ghost, antifield, Noether, pairing, and cyclicity rows",
            "prove the stress/source realization is a chain map into the universal source Ward complex",
            "test whether the matter equations preserve Q(T)=0 rather than merely the Ward identities",
            "construct retarded/advanced defect propagation only after the matter and nonminimal domains are fixed",
        ],
        "scope_guards": [
            "external spurions make a Ward complex but not a dynamical BV complex",
            "the compatible-source kernels are exact representative symbol fibers, not global matter solution spaces",
            "Q(T)=0 is stronger than Diff x Weyl Ward compatibility",
            "the dressed source is a changed higher-derivative coupling, not same-source Einstein equivalence",
            "no LORENTZIAN-CAUSAL, nonlinear, scattering, or quantum claim is made",
        ],
        "verification_command": "python3 -m bridge.einstein_sector.compensated_sourced_defect_chain_map --verify bridge/certificates/compensated_sourced_defect_chain_map.json",
    }
    return payload


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"sourced-defect chain-map certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
