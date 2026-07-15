"""Exact local minimal BV complex for the flat compensated Einstein--Weyl phase.

On the ``v != 0`` compensator chart, use

    rho = varphi/v,        h_hat = h + 2 rho eta.

The quadratic action depends only on ``h_hat``.  In these variables the
minimal complex splits into the Einstein--Weyl diffeomorphism complex and a
contractible Weyl Stueckelberg doublet, together with its antifield dual.

This is a LOCAL-ALGEBRAIC compact-support/formal-symbol certificate.  It is
not yet the complete classical import freeze: no residual cohomology,
gauge-fixed nonminimal domain, Green complex, matter BV complex, or quantum
claim is included.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "bridge" / "certificates" / "compensated_quadratic_minimal_bv.json"
)
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "compensated_quadratic_minimal_bv.schema.json"
)
INPUTS = {
    "compensator_phase": ROOT
    / "bridge"
    / "certificates"
    / "compensator_einstein_phase.json",
    "sourced_defect_preflight": ROOT
    / "bridge"
    / "certificates"
    / "compensated_einstein_sourced_defect_preflight.json",
    "pure_weyl_free_bv_reference": ROOT
    / "bridge"
    / "certificates"
    / "free_bv_complex.json",
    "positive_berger_clock": ROOT
    / "d_quotient_classical"
    / "certificates"
    / "POSITIVE_BERGER_CLOCK_BACKGROUND.json",
    "berger_charge_seed": ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_CLOCK_REDUCED_CHARGE_SEED.json",
}


class CompensatedQuadraticMinimalBVError(RuntimeError):
    """Raised when an exact BV identity or lifecycle guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompensatedQuadraticMinimalBVError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_digest(matrix: sp.MatrixBase) -> str:
    payload = {
        "shape": list(matrix.shape),
        "entries": [
            [row, column, str(sp.factor(value))]
            for (row, column), value in sorted(sp.SparseMatrix(matrix).todok().items())
        ],
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _trace(tensor: sp.Matrix, eta: sp.Matrix) -> sp.Expr:
    return sp.simplify(
        sum(eta[mu, nu] * tensor[mu, nu] for mu in range(4) for nu in range(4))
    )


@functools.lru_cache(maxsize=1)
def _build_exact_data() -> dict[str, Any]:
    eta = sp.diag(1, -1, -1, -1)
    pairs = tuple((mu, nu) for mu in range(4) for nu in range(mu, 4))
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    p = sp.Matrix(sp.symbols("p0:4"))
    p_up = eta * p
    p_squared = sp.expand((p.T * p_up)[0])
    c1, alpha, v = sp.symbols("c1 alpha v", nonzero=True)

    h_symbols = sp.symbols("h0:10")
    h = sp.Matrix(
        4,
        4,
        lambda mu, nu: h_symbols[pair_index[(min(mu, nu), max(mu, nu))]],
    )
    h_trace = _trace(h, eta)
    divergence = [
        sp.expand(sum(p_up[rho] * h[rho, nu] for rho in range(4)))
        for nu in range(4)
    ]
    ricci = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.expand(
            sp.Rational(1, 2)
            * (
                p[mu] * divergence[nu]
                + p[nu] * divergence[mu]
                - p_squared * h[mu, nu]
                - p[mu] * p[nu] * h_trace
            )
        ),
    )
    scalar = _trace(ricci, eta)
    einstein = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.expand(
            ricci[mu, nu] - sp.Rational(1, 2) * eta[mu, nu] * scalar
        ),
    )
    einstein_trace = _trace(einstein, eta)
    bach = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.expand(
            sp.Rational(1, 2) * p_squared * einstein[mu, nu]
            - sp.Rational(1, 6)
            * (eta[mu, nu] * p_squared - p[mu] * p[nu])
            * einstein_trace
        ),
    )
    euler = sp.Matrix(
        [sp.expand(c1 * einstein[mu, nu] + 2 * alpha * bach[mu, nu]) for mu, nu in pairs]
    )
    metric_operator = euler.jacobian(sp.Matrix(h_symbols))

    metric_weights = []
    for mu, nu in pairs:
        multiplicity = 1 if mu == nu else 2
        metric_weights.append(multiplicity * eta[mu, mu] * eta[nu, nu])
    metric_gram = sp.diag(*metric_weights)
    _require(metric_gram.det() != 0, "symmetric-tensor pairing is degenerate")
    _require(
        sp.simplify(metric_gram * metric_operator - metric_operator.T * metric_gram)
        == sp.zeros(10),
        "Einstein--Weyl Hessian is not formally self-adjoint",
    )

    diff_gauge = sp.zeros(10, 4)
    for row, (mu, nu) in enumerate(pairs):
        for column in range(4):
            diff_gauge[row, column] = (
                p[mu] * (1 if nu == column else 0)
                + p[nu] * (1 if mu == column else 0)
            )
    _require(
        sp.simplify(metric_operator * diff_gauge) == sp.zeros(10, 4),
        "metric Hessian does not annihilate linearized diffeomorphisms",
    )
    _require(
        sp.simplify(diff_gauge.T * metric_gram * metric_operator)
        == sp.zeros(4, 10),
        "metric Noether identity failed",
    )

    eta_vector = sp.Matrix([eta[mu, nu] for mu, nu in pairs])
    field_map = sp.zeros(11, 11)
    field_map[:10, :10] = sp.eye(10)
    field_map[:10, 10] = 2 * eta_vector / v
    field_map[10, 10] = 1 / v
    _require(sp.factor(field_map.det()) == 1 / v, "invariant field map determinant changed")
    original_weyl = sp.Matrix.vstack(2 * eta_vector, sp.Matrix([-v]))
    invariant_weyl = sp.simplify(field_map * original_weyl)
    _require(
        invariant_weyl == sp.Matrix([0] * 10 + [-1]),
        "original Weyl gauge vector did not become the rho doublet",
    )
    original_diff = sp.Matrix.vstack(diff_gauge, sp.zeros(1, 4))
    invariant_diff = sp.simplify(field_map * original_diff)
    _require(
        invariant_diff == sp.Matrix.vstack(diff_gauge, sp.zeros(1, 4)),
        "diffeomorphism gauge map changed under the compensator field map",
    )

    field_gram = sp.diag(*metric_weights, 1)
    ghost_gram = sp.diag(1, -1, -1, -1, 1)
    hessian = sp.diag(metric_operator, sp.zeros(1, 1))
    gauge = sp.zeros(11, 5)
    gauge[:10, :4] = diff_gauge
    gauge[10, 4] = -1
    _require(sp.simplify(hessian * gauge) == sp.zeros(11, 5), "H R != 0")
    _require(
        sp.simplify(gauge.T * field_gram * hessian) == sp.zeros(5, 11),
        "R^T G H != 0",
    )
    _require(
        sp.simplify(field_gram * hessian - hessian.T * field_gram) == sp.zeros(11),
        "compensated Hessian is not self-adjoint",
    )

    p_flip = {symbol: -symbol for symbol in p}
    gauge_minus = gauge.subs(p_flip, simultaneous=True)
    noether = sp.simplify(-ghost_gram.inv() * gauge_minus.T * field_gram)
    total_dimension = 32
    q = sp.zeros(total_dimension)
    ghost_slice = slice(0, 5)
    field_slice = slice(5, 16)
    antifield_slice = slice(16, 27)
    ghost_antifield_slice = slice(27, 32)
    q[field_slice, ghost_slice] = gauge
    q[antifield_slice, field_slice] = hessian
    q[ghost_antifield_slice, antifield_slice] = noether
    _require(sp.simplify(q * q) == sp.zeros(total_dimension), "minimal BV q^2 != 0")

    pairing = sp.zeros(total_dimension)
    pairing[ghost_slice, ghost_antifield_slice] = ghost_gram
    pairing[ghost_antifield_slice, ghost_slice] = -ghost_gram
    pairing[field_slice, antifield_slice] = field_gram
    pairing[antifield_slice, field_slice] = -field_gram
    _require(pairing.det() != 0, "minimal BV pairing is degenerate")
    q_minus = q.subs(p_flip, simultaneous=True)
    _require(
        sp.simplify(q_minus.T * pairing + pairing * q) == sp.zeros(total_dimension),
        "minimal BV differential is not formally cyclic",
    )

    weyl_indices = (4, 15, 26, 31)
    retained_indices = tuple(index for index in range(total_dimension) if index not in weyl_indices)
    inclusion = sp.zeros(total_dimension, len(retained_indices))
    projection = sp.zeros(len(retained_indices), total_dimension)
    for reduced_index, full_index in enumerate(retained_indices):
        inclusion[full_index, reduced_index] = 1
        projection[reduced_index, full_index] = 1
    homotopy = sp.zeros(total_dimension)
    homotopy[4, 15] = -1
    homotopy[26, 31] = 1
    identity = sp.eye(total_dimension)
    _require(projection * inclusion == sp.eye(len(retained_indices)), "pi i != 1")
    _require(
        sp.simplify(
            inclusion * projection - (identity - q * homotopy - homotopy * q)
        )
        == sp.zeros(total_dimension),
        "Weyl doublet contraction identity failed",
    )
    _require(homotopy * homotopy == sp.zeros(total_dimension), "s^2 != 0")
    _require(homotopy * inclusion == sp.zeros(total_dimension, 28), "s i != 0")
    _require(projection * homotopy == sp.zeros(28, total_dimension), "pi s != 0")
    _require(q * inclusion == inclusion * (projection * q * inclusion), "inclusion is not a chain map")
    _require(projection * q == (projection * q * inclusion) * projection, "projection is not a chain map")
    reduced_pairing = sp.simplify(inclusion.T * pairing * inclusion)
    _require(reduced_pairing.det() != 0, "reduced metric-diffeomorphism pairing is degenerate")

    fixture = {
        p[0]: 2,
        p[1]: 1,
        p[2]: 0,
        p[3]: 0,
        c1: -1,
        alpha: -1,
    }
    _require(gauge.subs(fixture).rank() == 5, "generic gauge rank fixture changed")
    _require(hessian.subs(fixture).rank() == 6, "generic Hessian rank fixture changed")
    _require(q.subs(fixture).rank() == 16, "generic BV rank fixture changed")

    original_action_hessian = sp.simplify(
        field_map[:10, :].T * metric_gram * metric_operator * field_map[:10, :]
    )
    invariant_action_hessian = sp.diag(metric_gram * metric_operator, sp.zeros(1, 1))
    inverse_map = sp.simplify(field_map.inv())
    _require(
        sp.simplify(
            inverse_map.T * original_action_hessian * inverse_map
            - invariant_action_hessian
        )
        == sp.zeros(11),
        "original-field action Hessian did not split in invariant variables",
    )

    digests = {
        "metric_operator": _matrix_digest(metric_operator),
        "original_action_hessian": _matrix_digest(original_action_hessian),
        "field_map": _matrix_digest(field_map),
        "gauge": _matrix_digest(gauge),
        "hessian": _matrix_digest(hessian),
        "noether": _matrix_digest(noether),
        "q": _matrix_digest(q),
        "pairing": _matrix_digest(pairing),
        "inclusion": _matrix_digest(inclusion),
        "pi_cl": _matrix_digest(projection),
        "homotopy": _matrix_digest(homotopy),
        "reduced_q": _matrix_digest(projection * q * inclusion),
        "reduced_pairing": _matrix_digest(reduced_pairing),
    }

    return {
        "symbols": {"p": p, "p_squared": p_squared, "c1": c1, "alpha": alpha, "v": v},
        "pairs": pairs,
        "metric_gram": metric_gram,
        "metric_operator": metric_operator,
        "field_map": field_map,
        "field_gram": field_gram,
        "ghost_gram": ghost_gram,
        "gauge": gauge,
        "hessian": hessian,
        "noether": noether,
        "q": q,
        "pairing": pairing,
        "inclusion": inclusion,
        "projection": projection,
        "homotopy": homotopy,
        "reduced_q": projection * q * inclusion,
        "reduced_pairing": reduced_pairing,
        "original_action_hessian": original_action_hessian,
        "digests": digests,
    }


def _action_and_field_theorem(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_representative": (
            "S=S_W+int sqrt(-g) zeta(phi^2 R-6 phi Box phi), with lambda=0 on the flat v!=0 phase"
        ),
        "bulk_integration_by_parts": (
            "zeta(phi^2 R+6 partial_phi.partial^phi) differs by -6 zeta nabla_m(phi nabla^m phi)"
        ),
        "boundary_rule": (
            "compact-support formal adjoints may discard the divergence; any BFV lift must restore and track it"
        ),
        "background_stationarity": (
            "phi=v!=0, g=eta, lambda=0 has zero tadpole by the imported phase certificate"
        ),
        "original_fields": ["symmetric h_mn", "varphi"],
        "invariant_fields": ["h_hat_mn=h_mn+2(varphi/v)eta_mn", "rho=varphi/v"],
        "field_map_determinant": "det F=1/v",
        "chart_boundary": "the field map and Weyl contraction are singular at v=0",
        "quadratic_split": (
            "S2=(1/2)<h_hat,K_EW h_hat>; rho is absent from the Hessian and is pure Weyl gauge"
        ),
        "metric_euler_operator": "K_EW h=c1 G1(h)+2 alpha B1(h)",
        "operator_fingerprints": {
            "metric_operator": data["digests"]["metric_operator"],
            "original_action_hessian": data["digests"]["original_action_hessian"],
            "field_map": data["digests"]["field_map"],
        },
        "status": "PASS",
    }


def _minimal_bv_theorem(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "grading_convention": "chain degree equals repository ghost number: ghosts -1, fields 0, antifields 1, ghost antifields 2",
        "field_slices": [
            {"name": "diff_ghost", "dimension": 4, "degree": -1},
            {"name": "weyl_ghost", "dimension": 1, "degree": -1},
            {"name": "h_hat", "dimension": 10, "degree": 0},
            {"name": "rho", "dimension": 1, "degree": 0},
            {"name": "h_hat_antifield", "dimension": 10, "degree": 1},
            {"name": "rho_antifield", "dimension": 1, "degree": 1},
            {"name": "diff_ghost_antifield", "dimension": 4, "degree": 2},
            {"name": "weyl_ghost_antifield", "dimension": 1, "degree": 2},
        ],
        "total_dimension": 32,
        "differential_blocks": [
            "R:(xi,sigma)->(2 partial_(m xi_n),-sigma)",
            "H:(h_hat,rho)->(K_EW h_hat,0)",
            "N=-R^dagger from field antifields to ghost antifields in the declared cyclic sign convention",
        ],
        "exact_identities": [
            "H R=0",
            "R^T G_field H=0",
            "q^2=0",
            "q(-p)^T Omega+Omega q(p)=0",
        ],
        "pairing": {
            "symmetric_tensor": "<h,k>=h_mn k^mn with off-diagonal multiplicity two",
            "diff_ghost": "eta_mn",
            "rho_and_weyl_ghost": "unit scalar pairing",
            "full_rank": 32,
        },
        "generic_off_shell_fixture": {
            "parameters": "p=(2,1,0,0), c1=-1, alpha=-1",
            "gauge_rank": 5,
            "hessian_rank": 6,
            "q_rank": 16,
            "interpretation": "rank fixture only; not an on-shell physical cohomology calculation",
        },
        "operator_fingerprints": {
            "gauge": data["digests"]["gauge"],
            "hessian": data["digests"]["hessian"],
            "noether": data["digests"]["noether"],
            "q": data["digests"]["q"],
            "pairing": data["digests"]["pairing"],
        },
        "status": "PASS",
    }


def _contraction_theorem(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "contractible_coordinates": [
            "weyl_ghost",
            "rho",
            "rho_antifield",
            "weyl_ghost_antifield",
        ],
        "doublet_maps": ["q(weyl_ghost)=-rho", "q(rho_antifield)=weyl_ghost_antifield"],
        "homotopy_maps": ["s(rho)=-weyl_ghost", "s(weyl_ghost_antifield)=rho_antifield"],
        "reduced_complex": "28-dimensional Einstein-Weyl metric-diffeomorphism minimal BV complex",
        "identities": [
            "pi_cl i=1",
            "i pi_cl=1-q s-s q",
            "s^2=0",
            "s i=0",
            "pi_cl s=0",
            "q i=i q_red",
            "pi_cl q=q_red pi_cl",
        ],
        "pairing_restriction": "i^T Omega i is nondegenerate on the reduced complex",
        "operator_fingerprints": {
            "inclusion": data["digests"]["inclusion"],
            "pi_cl": data["digests"]["pi_cl"],
            "homotopy": data["digests"]["homotopy"],
            "reduced_q": data["digests"]["reduced_q"],
            "reduced_pairing": data["digests"]["reduced_pairing"],
        },
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "compensated-flat-quadratic-minimal-bv-v1",
        "wrong compensated minimal BV schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"compensated minimal BV certificate is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(payload.get("dependency_tags") == ["LOCAL-ALGEBRAIC"], "wrong dependency tags")
    _require(
        payload.get("provenance", {}).get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(
        payload.get("verdict")
        == "COMPENSATED_FLAT_MINIMAL_BV_SPLITS_EW_DIFF_PLUS_WEYL_DOUBLET",
        "compensated minimal BV verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "action_representative_and_boundary_divergence_declared",
        "flat_background_stationarity_imported",
        "invariant_field_map_exact_and_invertible_for_v_nonzero",
        "weyl_invariant_metric_hessian_constructed",
        "symmetric_tensor_pairing_exact",
        "diff_and_weyl_gauge_maps_constructed",
        "hessian_gauge_annihilation_exact",
        "noether_identity_exact",
        "minimal_bv_nilpotency_exact",
        "formal_cyclicity_exact",
        "weyl_stueckelberg_doublet_contracted",
        "reduced_metric_diff_chain_equivalence_exact",
        "reduced_pairing_nondegenerate",
        "berger_background_status_imported",
        "berger_charge_seed_status_imported",
        "compensator_and_berger_clock_roles_separated",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    phase = _load(INPUTS["compensator_phase"])
    defect = _load(INPUTS["sourced_defect_preflight"])
    pure_bv = _load(INPUTS["pure_weyl_free_bv_reference"])
    berger = _load(INPUTS["positive_berger_clock"])
    berger_charge = _load(INPUTS["berger_charge_seed"])
    _require(
        phase.get("result_id") == "COMPENSATOR_EINSTEIN_PHASE"
        and phase.get("weyl_frame_theorem", {}).get("invariant_linear_metric")
        == "h_hat_mn=h_mn+2(varphi/v)eta_mn",
        "compensator phase input changed",
    )
    _require(
        defect.get("verdict")
        == "ARBITRARY_SAME_SOURCE_EINSTEIN_TRUNCATION_REFUTED_LINEAR_FLAT",
        "sourced-defect input changed",
    )
    _require(pure_bv.get("schema") == "pure-weyl-free-bv-block-v1", "pure-Weyl BV reference changed")
    _require(
        berger.get("result_id") == "POSITIVE_BERGER_CLOCK_BACKGROUND"
        and berger.get("claim_status") == "CERTIFIED_EXACT_BACKGROUND"
        and berger.get("flags", {}).get("exact_backreacted_background_exists") is True
        and berger.get("flags", {}).get("support_local_all_row_bv_retract_constructed")
        is False,
        "Berger background gate changed",
    )
    _require(
        berger_charge.get("result_id") == "BERGER_CLOCK_REDUCED_CHARGE_SEED"
        and berger_charge.get("claim_status") == "CERTIFIED_REDUCED_CHARGE_SEED"
        and berger_charge.get("flags", {}).get("global_internal_charge_computed") is True
        and berger_charge.get("flags", {}).get("total_covariant_D_charge_computed") is False,
        "Berger charge gate changed",
    )

    data = _build_exact_data()
    certificate = {
        "schema": "compensated-flat-quadratic-minimal-bv-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/compensated_quadratic_minimal_bv.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_FLAT_QUADRATIC_MINIMAL_BV_COMPLEX",
        "result_state": "LOCAL_MINIMAL_BV_CERTIFIED_CLASSICAL_IMPORT_FREEZE_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "input_base_commit": "c4a1d28bab4d716a281db1c5428a83e515f6a822",
            "generator_path": (
                "bridge/einstein_sector/compensated_quadratic_minimal_bv.py"
            ),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "domain": {
            "spacetime": "four-dimensional Minkowski space",
            "test_sections": "compactly supported smooth formal fields, or polynomial Fourier symbols with p->-p formal adjoint",
            "phase": "phi=v!=0, lambda=0, c1=zeta v^2 nonzero, alpha nonzero",
            "curvature_convention": "metric Euler row K_EW=c1 G1+2 alpha B1",
            "zero_mode_rule": "generic-symbol ranks do not classify p=0 Killing or global cylinder residual modes",
        },
        "action_and_field_theorem": _action_and_field_theorem(data),
        "minimal_bv_theorem": _minimal_bv_theorem(data),
        "weyl_doublet_contraction": _contraction_theorem(data),
        "berger_clock_coordination": {
            "background_result": "CERTIFIED_EXACT_BACKGROUND",
            "background_verdict": "positive-energy rotating scalar clock on a compact squashed Berger background exists",
            "charge_result": "CERTIFIED_REDUCED_CHARGE_SEED",
            "charge_verdict": "nonzero internal O(2) clock momentum; total covariant D charge remains open",
            "next_gate": "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT",
            "convention_guard": (
                "the Berger certificates use signature (-,+,+,+), while this flat compensated complex uses (+,-,-,-); no Berger sign formula is imported into K_EW"
            ),
            "separation_rule": (
                "the Berger phase clock is a dynamical relational matter clock on a non-flat compact background; rho here is a flat-phase Weyl Stueckelberg coordinate and supplies no relational time"
            ),
            "effect_on_this_theorem": (
                "contextual import only; Berger operators are not inserted into the flat compensated BV differential"
            ),
        },
        "lifecycle_boundary": {
            "certified_now": "local minimal vacuum BV complex and exact Weyl-doublet contraction",
            "next_gate": "COMPENSATED_CLASSICAL_IMPORT_FREEZE",
            "freeze_requirements": [
                "declare the target residual or local cohomology result kind",
                "compute exact cohomology representatives and pairing",
                "certify all required chain maps and contractions",
                "add a complete provenance and missing-object ledger",
                "keep gauge-fixed nonminimal and causal Green data in separate promotions",
            ],
        },
        "verdict": "COMPENSATED_FLAT_MINIMAL_BV_SPLITS_EW_DIFF_PLUS_WEYL_DOUBLET",
        "claim_flags": {
            "action_representative_and_boundary_divergence_declared": True,
            "flat_background_stationarity_imported": True,
            "invariant_field_map_exact_and_invertible_for_v_nonzero": True,
            "weyl_invariant_metric_hessian_constructed": True,
            "symmetric_tensor_pairing_exact": True,
            "diff_and_weyl_gauge_maps_constructed": True,
            "hessian_gauge_annihilation_exact": True,
            "noether_identity_exact": True,
            "minimal_bv_nilpotency_exact": True,
            "formal_cyclicity_exact": True,
            "weyl_stueckelberg_doublet_contracted": True,
            "reduced_metric_diff_chain_equivalence_exact": True,
            "reduced_pairing_nondegenerate": True,
            "berger_background_status_imported": True,
            "berger_charge_seed_status_imported": True,
            "compensator_and_berger_clock_roles_separated": True,
            "classical_import_freeze_complete": False,
            "physical_residual_cohomology_computed": False,
            "on_shell_one_particle_cohomology_computed": False,
            "p_zero_global_modes_classified": False,
            "gauge_fixed_nonminimal_complex_constructed": False,
            "green_hyperbolic_complex_constructed": False,
            "matter_inclusive_bv_complex_constructed": False,
            "sourced_defect_chain_map_constructed": False,
            "berger_support_local_bv_retract_constructed": False,
            "berger_total_covariant_D_charge_computed": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "scope_guards": [
            "all proved identities are LOCAL-ALGEBRAIC and exact over Q(c1,alpha,v,v^-1)[p0,p1,p2,p3]",
            "compact support justifies formal integration by parts; the discarded divergence is retained in the boundary ledger",
            "the v!=0 invariant chart and Weyl contraction are not extended through v=0",
            "generic off-shell rank is not physical or residual cohomology",
            "the pure-Weyl D-finite BV fixture is architectural context, not the compensated local field complex",
            "the Berger clock imports do not identify its relational phase with the Stueckelberg compensator",
            "no gauge-fixed, causal, nonlinear, boundary, scattering, quantum, or complete classical-freeze claim is made",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.compensated_quadratic_minimal_bv "
            "--verify bridge/certificates/compensated_quadratic_minimal_bv.json"
        ),
    }
    _validate_contract(certificate)
    return certificate


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"certificate is stale or altered: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(
            json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
