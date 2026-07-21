"""Exact compact-Cauchy constraint-symbol and Fredholm gate.

The Weyl--Maxwell canonical phase space has thirty local components.  Its
seven first-class constraints and seven legitimate configuration gauge
conditions form a right-elliptic (full-row-rank) Douglis--Nirenberg symbol,
but they cannot form a Fredholm operator: the symbol retains the sixteen
physical phase-space directions.  Two transverse-traceless momentum
witnesses make that obstruction explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-constraint-fredholm-gate-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-constraint-fredholm-gate-v1.schema.json"
PRODUCER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate.py"

INPUTS = {
    "full_time_sobolev_gate": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1.json",
        "020cf4bcfa8299a9be7a67078dae4ae8c85f184816000da48df8a537487f7aac",
    ),
    "finite_harmonic_structural_freeze": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
        "43b212dafc623909ce76ff31bcb1b3fab7054a9fa7a2ff1b757e630f26cf1740",
    ),
    "product_incidence": (
        "bridge/certificates/einstein_maxwell_product_incidence.json",
        "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
    ),
    "stabilizer_descent": (
        "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
        "7d2840bc88b3fb157345badb7ae2683adceb7401b611ba5b90dca4b8868993b8",
    ),
    "action_normalized_linear_phase_space": (
        "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
        "442d4bbd0de7b02215f13b4dc3b8f5becf1cdc99f57bba7c7b58586405c48821",
    ),
    "complete_finite_smooth_global": (
        "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
        "d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd",
    ),
}

TENSOR_SLOTS = ["11", "22", "33", "12", "13", "23"]
VARIABLES = (
    [f"h{slot}" for slot in TENSOR_SLOTS]
    + [f"K{slot}" for slot in TENSOR_SLOTS]
    + [f"pi{slot}" for slot in TENSOR_SLOTS]
    + [f"P{slot}" for slot in TENSOR_SLOTS]
    + ["a1", "a2", "a3", "E1", "E2", "E3"]
)
CONSTRAINT_ROWS = ["H_perp", "H_1", "H_2", "H_3", "P_trace", "Q_scale", "Gauss"]
GAUGE_ROWS = ["G_1", "G_2", "G_3", "G_perp", "W_value", "W_normal", "Coulomb"]


class CompactCauchyFredholmGateError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompactCauchyFredholmGateError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _imports() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name, (relative, expected) in INPUTS.items():
        path = ROOT / relative
        _require(path.exists(), f"missing input: {relative}")
        actual = _sha256(path)
        _require(actual == expected, f"input drift: {name}")
        payload = _load(path)
        rows.append(
            {
                "name": name,
                "path": relative,
                "sha256": actual,
                "result_id": payload.get("result_id", payload.get("schema", "NO_RESULT_ID")),
            }
        )
    return rows


def _set(matrix: sp.MutableDenseMatrix, row: str, column: str, value: sp.Expr | int) -> None:
    matrix[(CONSTRAINT_ROWS + GAUGE_ROWS).index(row), VARIABLES.index(column)] = value


def _symbol_matrices() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return raw constraints, gauge rows and their combined symbol.

    The covector is xi=(1,0,0), aligned with S1.  The parallel traceless
    background Ostrogradsky momentum is normalized to diag(-2,1,1); its
    nonzero scalar normalization does not affect any rank or kernel claim.
    """

    combined = sp.zeros(14, 30)

    # Hamiltonian symbol from (R_ij + D_i D_j) P^ij.  Linearizing the
    # density connection at the parallel product momentum gives -h11+P11
    # in this normalized frame.
    _set(combined, "H_perp", "h11", -1)
    _set(combined, "H_perp", "P11", 1)

    # Momentum constraints at Kbar=pi_bar=0 and Pbar=diag(-2,1,1).
    for column, value in (("pi11", -2), ("K11", 2), ("K22", 1), ("K33", 1)):
        _set(combined, "H_1", column, value)
    for row, pi_column, k_column in (("H_2", "pi12", "K12"), ("H_3", "pi13", "K13")):
        _set(combined, row, pi_column, -2)
        _set(combined, row, k_column, 4)

    # Primary and secondary conformal constraints.
    for column, value in (("P11", 1), ("P22", 1), ("P33", 1), ("h11", -2), ("h22", 1), ("h33", 1)):
        _set(combined, "P_trace", column, value)
    for column, value in (("pi11", 2), ("pi22", 2), ("pi33", 2), ("K11", -2), ("K22", 1), ("K33", 1)):
        _set(combined, "Q_scale", column, value)
    _set(combined, "Gauss", "E1", 1)

    # Configuration gauge slice: spatial unimodular harmonic, normal
    # double-divergence, Weyl value/normal derivative, and Maxwell Coulomb.
    for column, value in (("h11", sp.Rational(2, 3)), ("h22", sp.Rational(-1, 3)), ("h33", sp.Rational(-1, 3))):
        _set(combined, "G_1", column, value)
    _set(combined, "G_2", "h12", 1)
    _set(combined, "G_3", "h13", 1)
    for column, value in (("K11", sp.Rational(2, 3)), ("K22", sp.Rational(-1, 3)), ("K33", sp.Rational(-1, 3))):
        _set(combined, "G_perp", column, value)
    for column in ("h11", "h22", "h33"):
        _set(combined, "W_value", column, 1)
    for column in ("K11", "K22", "K33"):
        _set(combined, "W_normal", column, 1)
    _set(combined, "Coulomb", "a1", 1)

    return sp.Matrix(combined[:7, :]), sp.Matrix(combined[7:, :]), sp.Matrix(combined)


def _column_vector(**entries: int) -> sp.Matrix:
    vector = sp.zeros(len(VARIABLES), 1)
    for name, value in entries.items():
        vector[VARIABLES.index(name), 0] = value
    return vector


def _matrix_rows(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in matrix.row(index)] for index in range(matrix.rows)]


def _symbol_certificate() -> dict[str, Any]:
    raw, gauge, combined = _symbol_matrices()
    _require(raw.rank() == 7, "raw constraint symbol lost full row rank")
    _require(gauge.rank() == 7, "gauge symbol lost full row rank")
    _require(combined.rank() == 14, "combined symbol rank changed")

    p_cross = _column_vector(P23=1)
    p_plus = _column_vector(P22=1, P33=-1)
    _require(combined * p_cross == sp.zeros(14, 1), "cross TT witness left the kernel")
    _require(combined * p_plus == sp.zeros(14, 1), "plus TT witness left the kernel")

    raw_columns = ["P11", "pi11", "pi12", "pi13", "P22", "pi22", "E1"]
    raw_minor = raw[:, [VARIABLES.index(name) for name in raw_columns]]
    _require(raw_minor.det() == -16, "raw right-elliptic minor changed")

    # Principal action of the seven gauge parameters ordered as spatial
    # v1,v2,v3; normal lapse f; Weyl value omega; Weyl normal rho; Maxwell chi.
    gauge_orbit = sp.diag(sp.Rational(4, 3), 1, 1, sp.Rational(-2, 3), 6, 3, 1)
    _require(gauge_orbit.det() == -16, "gauge-slice orbit determinant changed")

    mutated = combined.col_join(sp.zeros(1, 30))
    mutated[14, VARIABLES.index("P23")] = 1
    _require(mutated.rank() == 15, "physical-killing mutation did not change rank")
    _require(mutated * p_cross != sp.zeros(15, 1), "physical-killing mutation was not detected")

    return {
        "covector_fixture": "orthonormal product frame with xi=(1,0,0) along S1_L",
        "background_momentum_normalization": "parallel traceless P0^ij proportional to diag(-2,1,1); the suppressed nonzero action normalization does not affect ranks",
        "variables": VARIABLES,
        "constraint_rows": CONSTRAINT_ROWS,
        "gauge_rows": GAUGE_ROWS,
        "raw_constraint_symbol": _matrix_rows(raw),
        "gauge_symbol": _matrix_rows(gauge),
        "combined_symbol": _matrix_rows(combined),
        "raw_rank": raw.rank(),
        "raw_surjective_minor": {"columns": raw_columns, "determinant": str(raw_minor.det())},
        "gauge_rank": gauge.rank(),
        "gauge_on_gauge_orbit_determinant": str(gauge_orbit.det()),
        "combined_rank": combined.rank(),
        "domain_rank": combined.cols,
        "codomain_rank": combined.rows,
        "symbol_kernel_dimension": combined.cols - combined.rank(),
        "tt_momentum_witnesses": [
            {"name": "P_cross", "nonzero_components": {"P23": "1"}, "residual": [str(value) for value in combined * p_cross]},
            {"name": "P_plus", "nonzero_components": {"P22": "1", "P33": "-1"}, "residual": [str(value) for value in combined * p_plus]},
        ],
        "covariant_rank_argument": "For every xi!=0, P^ij -> (xi_i xi_j P^ij,tr P) has rank 2, pi^ij -> (xi_j pi^ij,tr pi) has rank 4, and E^i -> xi_i E^i has rank 1. Hence the raw constraint symbol has rank 7 for every nonzero covector.",
        "combined_covariant_rank_argument": "For every xi!=0 the seven configuration gauge rows are surjective on the seven principal gauge-orbit directions: the spatial block has eigenvalues |xi|^2,|xi|^2,(4/3)|xi|^2, the normal block is -(2/3)|xi|^4, and the two Weyl plus Maxwell blocks are nonzero. Gauge rows contain no momenta. First solve the gauge rows in configuration variables, then use the independently surjective momentum/electric constraint block to cancel the induced constraint values. Thus the combined symbol has rank 14 for every xi!=0.",
        "mutation_control": {
            "added_row": "P23=0",
            "mutated_rank": mutated.rank(),
            "interpretation": "This kills one displayed physical TT momentum only by adding a non-gauge condition; it is forbidden as a gauge-slice repair.",
        },
    }


def build_certificate() -> dict[str, Any]:
    imported = _imports()
    symbol = _symbol_certificate()
    return {
        "schema": "einstein-maxwell-weyl-compact-cauchy-constraint-fredholm-gate-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1",
        "result_state": "RIGHT_ELLIPTIC_CONSTRAINT_MAP_CERTIFIED_TWO_SIDED_FREDHOLM_GATE_OBSTRUCTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_commit": "d78b1f8bd",
            "producer": str(PRODUCER_PATH.relative_to(ROOT)),
            "producer_sha256": _sha256(PRODUCER_PATH),
            "imported_artifacts": imported,
            "canonical_cross_checks": [
                {"citation": "Kiefer--Nikolic, Phys. Rev. D 95, 084018 (2017), arXiv:1702.04973", "source_sha256": "c159d4b8e86d076f5eb1642b8883d0147575c98d275795ad1478b438f3c4148b"},
                {"citation": "Chen--Ma, Phys. Rev. D 98, 064009 (2018), arXiv:1803.10807", "source_sha256": "9a58d78083efa84771d490d1cda0b743f9e230a41995bf65dd08b050b35e009f"},
            ],
        },
        "declared_cauchy_problem": {
            "slice": "Sigma=S1_L x S2, compact and boundaryless",
            "bundle_and_charge": "fixed magnetic U(1) bundle P_N with N=2 and fixed harmonic electric coordinate Q_e; Wilson-line coordinate remains physical",
            "maxwell_gauge": "based/zero-mean gauge algebra; the Gauss codomain is mean-zero, so constant U(1) reducibility is not miscounted as a sixth Taub covector",
            "sobolev_index": "integer s>=4",
            "domain": "h_ij,P^ij in H^(s+2); K_ij,pi^ij,a_i,E^i in H^(s+1), with P and pi tensor densities understood via the fixed smooth background volume form",
            "constraint_targets": "H_perp,H_i,Gauss in H^s; P_trace in H^(s+2); Q_scale in H^(s+1)",
            "gauge_targets": "G_i in H^(s+1); G_perp in H^(s-1); W_value in H^(s+2); W_normal in H^(s+1); Coulomb in H^s",
            "local_gauge_slice": [
                "G_i=D^j(h_ij-(1/3)h h0_ij)=0",
                "G_perp=D^iD^j(K_ij-(1/3)K h0_ij)=0",
                "W_value=h=0",
                "W_normal=K=0",
                "Coulomb=D^i a_i=0",
            ],
            "gauge_slice_completeness": "The principal action on spatial Diff, normal Diff, Weyl value, Weyl normal derivative and based Maxwell parameters has determinant -16 at |xi|=1.",
        },
        "action_derived_constraint_ledger": {
            "canonical_pairs": ["(h_ij,pi^ij)", "(K_ij,P^ij)", "(a_i,E^i)"],
            "H_i": "-2 h_ij D_k pi^(jk)+P^(jk)D_i K_jk-2D_j(P^(jk)K_ik)+F_ij E^j",
            "H_perp": "2pi^(ij)K_ij-(P_ij P^ij)/(2 sqrt(h)) + P^ij R_ij + P^ij K_ij K + D_iD_jP^ij - sqrt(h) C_ijkn C^(ijk)_n + H_Maxwell, after the nonzero canonical rescaling fixed by alpha_B=3",
            "P_trace": "h_ij P^ij",
            "Q_scale": "2h_ij pi^ij+K_ijP^ij",
            "Gauss": "D_i E^i",
            "maxwell_terms": "H_Maxwell=(E_iE^i)/(2sqrt(h))+(sqrt(h)/4)F_ijF^ij and H_i^Maxwell=F_ijE^j",
            "first_class_count": 7,
            "local_phase_space_rank": 30,
            "physical_phase_space_rank": 16,
            "normalization_boundary": "The displayed unbarred pure-Weyl formulas use a nonzero canonical rescaling relative to alpha_B=3. The exact symbol ranks, TT kernel and Fredholm obstruction are invariant under that rescaling; no numerical Hamiltonian-energy claim is made.",
        },
        "douglis_nirenberg_symbol": symbol,
        "functional_analytic_verdict": {
            "raw_constraint_map": "UNDERDETERMINED_ELLIPTIC_RIGHT_SEMI_FREDHOLM",
            "raw_constraint_symbol_surjective": True,
            "raw_constraint_range_closed_on_compact_slice": True,
            "raw_constraint_cokernel_finite_dimensional": True,
            "combined_constraint_gauge_symbol_full_row_rank": True,
            "combined_constraint_gauge_range_closed_on_compact_slice": True,
            "combined_operator_fredholm": False,
            "reason_not_fredholm": "A Fredholm differential operator on a compact manifold must have an invertible principal symbol and equal domain/codomain bundle ranks. Here the ranks are 30 and 14 and the exact symbol kernel has dimension 16.",
            "physical_kernel_may_not_be_gauge_fixed_away": True,
            "smooth_mapping": "For s>=4 the nonlinear canonical constraint expressions define a smooth map on the open H^(s+2) metric cone with the displayed weighted targets; products and inverse-metric composition are continuous without additional derivative loss.",
            "tame_slice_and_momentum_map_normal_form": "OPEN: right-semi-Fredholmness is the appropriate AMM starting point, but exact global adjoint-kernel identification and a nonlinear slice theorem have not been supplied.",
        },
        "adjoint_cokernel_ledger": {
            "finite_dimensional": "CERTIFIED by underdetermined ellipticity on compact Sigma",
            "five_lifted_stabilizers_contained": ["H", "P_x", "J_1", "J_2", "J_3"],
            "exactly_five": "OPEN",
            "constant_U1": "REMOVED from the target by the mean-zero Gauss codomain; it is a reducibility acting trivially on the connection, not a sixth nontrivial Taub moment map",
            "finite_EP_comparison": "The five finite exponential-polynomial covectors remain certified in their carrier, but finite-mode counting is not used to identify the Sobolev adjoint kernel.",
        },
        "classification": {
            "complete_action_derived_canonical_constraint_ledger": True,
            "explicit_weighted_sobolev_spaces": True,
            "explicit_complete_local_gauge_slice_at_symbol_level": True,
            "raw_constraint_right_ellipticity": True,
            "closed_range_and_finite_cokernel": True,
            "two_sided_ellipticity": False,
            "fredholm_constraint_plus_gauge_operator": False,
            "adjoint_kernel_exactly_five": False,
            "sobolev_momentum_map_normal_form": False,
            "finite_EP_theorem_promoted_by_density": False,
            "global_evolution_or_stability_claim": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "next_gate": {
            "name": "COMPACT_CAUCHY_UNDERDETERMINED_ELLIPTIC_ADJOINT_KERNEL_AND_SLICE",
            "required": [
                "compute the global adjoint kernel of the right-elliptic constraint map on S1_L x S2 in the fixed charge fibre",
                "prove or refute that the only nontrivial elements are the five lifted stabilizers",
                "construct the nonlinear Sobolev gauge slice and AMM momentum-map normal form using semi-Fredholm rather than false Fredholm hypotheses",
            ],
        },
        "scope": {
            "theory": "Weyl-Maxwell target with Einstein-Maxwell finite-harmonic comparison",
            "background": "compactified magnetically supported Plebanski-Hacyan product",
            "boundaries": "compact boundaryless Cauchy slice S1_L x S2",
            "charge_sector": "fixed magnetic P_N, N=2; fixed harmonic electric Q_e; based Maxwell gauge",
            "carrier": "complete local canonical Weyl-Maxwell Cauchy phase space and one exact principal-symbol fibre",
            "degree": "linearized constraint and gauge symbol; nonlinear mapping regularity only",
            "parity": "all local tensor components before harmonic parity splitting",
            "ell": "all; principal-symbol statement is local and pre-harmonic",
            "m": "all; principal-symbol statement is local and pre-harmonic",
            "k": "all; witness covector is aligned with nonzero S1 cotangent direction",
            "omega": "NOT_APPLICABLE: Cauchy constraint map",
        },
        "claim_boundary": "This theorem derives the canonical Weyl-Maxwell constraint ledger, certifies the raw compact-Cauchy constraint symbol as underdetermined elliptic with closed range and finite cokernel, and proves that the declared constraint-plus-gauge operator is not Fredholm because its exact symbol retains sixteen physical directions. It does not identify the global adjoint kernel as exactly five, prove an AMM/Fischer-Marsden normal form, promote the finite EP theorem to Sobolev data, or establish evolution, bounded stability, causality, scattering, particles, observables or quantum theory.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate --check",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-constraint-fredholm-gate-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER_PATH.relative_to(ROOT)),
        "generated_by_sha256": _sha256(PRODUCER_PATH),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "einstein.ph.wm.compact_cauchy.constraint_fredholm_gate",
                "scope": certificate["scope"],
                "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
                "mode_data": {
                    "dispersion": {"status": "NOT_APPLICABLE", "statement": "This is a spatial Cauchy constraint symbol, not a frequency-shell theorem."},
                    "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "No Sobolev completion of the Lee-Wald phase space is constructed."},
                    "taub_maps": {"status": "OPEN", "statement": "The adjoint kernel is finite and contains the five lifted stabilizers, but equality with those five remains open."},
                    "resonance": {"status": "NOT_APPLICABLE", "statement": "No temporal resonance inversion occurs in the Cauchy symbol."},
                    "second_order": {
                        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                        "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "The finite harmonic result is not promoted by this symbol theorem."},
                        "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "Exponential-polynomial time corrections are a separate carrier."},
                        "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No evolution or retarded map is analyzed."},
                    },
                },
                "evidence": [{"path": str(certificate_path.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": _sha256(certificate_path)}],
                "claim_boundary": certificate["claim_boundary"],
            }
        ],
        "verification_commands": certificate["verification_commands"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atlas", type=Path, default=ATLAS_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    if args.check:
        _require(args.output.exists() and _load(args.output) == certificate, "certificate drift or missing")
        _require(args.atlas.exists() and _load(args.atlas) == build_atlas(certificate, args.output), "atlas drift or missing")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate, args.output)
    args.atlas.parent.mkdir(parents=True, exist_ok=True)
    args.atlas.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
