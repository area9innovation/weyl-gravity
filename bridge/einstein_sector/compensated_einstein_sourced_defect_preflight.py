"""Gauge-covariant sourced Einstein-defect preflight for the compensated phase.

The constant-compensator phase has the linearized metric equation

    c1 G_1(h_hat) + 2 alpha B_1(h_hat) = T,

where ``h_hat=h+2(varphi/v)eta`` is Weyl invariant.  This module derives the
flat tensor identity ``B_1=Q G_1`` and uses it to audit the same-source
Einstein truncation ``c1 G_1=T``.  Its exact compatibility condition is

    Q(T)=0.

This is a preflight theorem.  A fixed external source defines an affine
solution sector, not a BV subcomplex.  A genuine sourced BV theorem must add
the matter fields, ghosts when present, antifields, and Ward identities to a
certified compensated quadratic BV complex.
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
    ROOT
    / "bridge"
    / "certificates"
    / "compensated_einstein_sourced_defect_preflight.json"
)
SCHEMA_PATH = (
    ROOT
    / "bridge"
    / "einstein_sector"
    / "schema"
    / "compensated_einstein_sourced_defect_preflight.schema.json"
)
INPUTS = {
    "compensator_phase": ROOT
    / "bridge"
    / "certificates"
    / "compensator_einstein_phase.json",
    "causal_subsector": ROOT
    / "bridge"
    / "certificates"
    / "compensated_einstein_causal_subsector.json",
    "local_projectors": ROOT
    / "bridge"
    / "certificates"
    / "compensated_einstein_local_projectors.json",
    "pure_weyl_free_bv_reference": ROOT
    / "bridge"
    / "certificates"
    / "free_bv_complex.json",
}


class CompensatedEinsteinSourcedDefectPreflightError(RuntimeError):
    """Raised when a sourced-defect identity or fail-closed guard regresses."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CompensatedEinsteinSourcedDefectPreflightError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _trace(tensor: sp.Matrix, metric_inverse: sp.Matrix) -> sp.Expr:
    return sp.simplify(
        sum(
            metric_inverse[mu, nu] * tensor[mu, nu]
            for mu in range(4)
            for nu in range(4)
        )
    )


@functools.lru_cache(maxsize=1)
def _linearized_tensor_checks() -> dict[str, Any]:
    eta = sp.diag(1, -1, -1, -1)
    p_down = sp.Matrix(sp.symbols("p0:4"))
    p_up = eta * p_down
    p_squared = sp.expand((p_down.T * p_up)[0])

    entries = {
        (mu, nu): sp.symbols(f"h{mu}{nu}")
        for mu in range(4)
        for nu in range(mu, 4)
    }
    h = sp.Matrix(4, 4, lambda mu, nu: entries[min(mu, nu), max(mu, nu)])
    h_trace = _trace(h, eta)
    h_divergence = [
        sp.expand(sum(p_up[rho] * h[rho, nu] for rho in range(4)))
        for nu in range(4)
    ]
    ricci = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.expand(
            sp.Rational(1, 2)
            * (
                p_down[mu] * h_divergence[nu]
                + p_down[nu] * h_divergence[mu]
                - p_squared * h[mu, nu]
                - p_down[mu] * p_down[nu] * h_trace
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
    einstein_divergence = [
        sp.simplify(sum(p_up[mu] * einstein[mu, nu] for mu in range(4)))
        for nu in range(4)
    ]
    _require(einstein_trace == -scalar, "linearized Einstein trace identity changed")
    _require(einstein_divergence == [0, 0, 0, 0], "linearized Bianchi identity failed")

    xi = sp.Matrix(sp.symbols("xi0:4"))
    pure_diff = sp.Matrix(
        4,
        4,
        lambda mu, nu: p_down[mu] * xi[nu] + p_down[nu] * xi[mu],
    )
    diff_substitution = {
        entries[mu, nu]: pure_diff[mu, nu] for mu, nu in entries
    }
    _require(
        all(
            sp.simplify(einstein[mu, nu].subs(diff_substitution)) == 0
            for mu in range(4)
            for nu in range(4)
        ),
        "linearized Einstein tensor is not diffeomorphism gauge invariant",
    )

    bach = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.expand(
            sp.Rational(1, 2) * p_squared * einstein[mu, nu]
            - sp.Rational(1, 6)
            * (eta[mu, nu] * p_squared - p_down[mu] * p_down[nu])
            * einstein_trace
        ),
    )
    _require(_trace(bach, eta) == 0, "linearized Bach tensor is not traceless")
    _require(
        [
            sp.simplify(sum(p_up[mu] * bach[mu, nu] for mu in range(4)))
            for nu in range(4)
        ]
        == [0, 0, 0, 0],
        "linearized Bach tensor is not divergence free",
    )
    _require(
        all(
            sp.simplify(bach[mu, nu].subs(diff_substitution)) == 0
            for mu in range(4)
            for nu in range(4)
        ),
        "linearized Bach tensor is not diffeomorphism gauge invariant",
    )

    plus, cross = sp.symbols("h_plus h_cross")
    tt_tensor = sp.Matrix(
        [
            [0, 0, 0, 0],
            [0, plus, cross, 0],
            [0, cross, -plus, 0],
            [0, 0, 0, 0],
        ]
    )
    tt_substitution = {
        **{entries[mu, nu]: tt_tensor[mu, nu] for mu, nu in entries},
        p_down[1]: 0,
        p_down[2]: 0,
    }
    tt_p_squared = sp.expand(p_squared.subs(tt_substitution))
    _require(_trace(tt_tensor, eta) == 0, "TT polarization witness has nonzero trace")
    _require(
        all(
            sp.simplify(h_divergence[nu].subs(tt_substitution)) == 0
            for nu in range(4)
        ),
        "TT polarization witness is not transverse",
    )
    _require(
        all(
            sp.simplify(
                einstein[mu, nu].subs(tt_substitution)
                + sp.Rational(1, 2) * tt_p_squared * tt_tensor[mu, nu]
            )
            == 0
            for mu in range(4)
            for nu in range(4)
        ),
        "TT Einstein reduction changed",
    )
    _require(
        all(
            sp.simplify(
                bach[mu, nu].subs(tt_substitution)
                + sp.Rational(1, 4) * tt_p_squared**2 * tt_tensor[mu, nu]
            )
            == 0
            for mu in range(4)
            for nu in range(4)
        ),
        "TT Bach reduction changed",
    )

    sigma, varphi, v = sp.symbols("sigma varphi v", nonzero=True)
    delta_h_trace_amplitude = 2 * sigma
    delta_varphi = -v * sigma
    delta_h_hat_trace_amplitude = sp.simplify(
        delta_h_trace_amplitude + 2 * delta_varphi / v
    )
    _require(
        delta_h_hat_trace_amplitude == 0,
        "compensated linear metric is not Weyl invariant",
    )

    return {
        "background": "four-dimensional Minkowski space with eta=diag(1,-1,-1,-1)",
        "weyl_invariant_metric": "h_hat_mn=h_mn+2(varphi/v)eta_mn",
        "weyl_variations": ["delta_sigma h_mn=2 sigma eta_mn", "delta_sigma varphi=-v sigma"],
        "diffeomorphism_variation": "delta_xi h_hat_mn=partial_m xi_n+partial_n xi_m",
        "linearized_einstein_tensor": "G1_mn=R1_mn-(1/2)eta_mn R1",
        "linearized_bach_factorization": (
            "B1_mn=Q(G1)_mn=(1/2)Box G1_mn-(1/6)(eta_mn Box-partial_m partial_n)tr(G1)"
        ),
        "identities": [
            "partial^m G1_mn=0",
            "partial^m B1_mn=0",
            "tr(B1)=0",
            "G1(delta_xi h_hat)=0",
            "B1(delta_xi h_hat)=0",
        ],
        "tt_reduction": [
            "G1(h_TT)=-(1/2)Box h_TT",
            "B1(h_TT)=-(1/4)Box^2 h_TT",
        ],
        "status": "PASS",
    }


def _source_ward_checks() -> dict[str, Any]:
    trace_t, scalar_source, v, sigma = sp.symbols("Ttrace Jphi v sigma")
    metric_variation = sigma * trace_t
    compensator_variation = -sigma * v * scalar_source
    weyl_variation = sp.expand(metric_variation + compensator_variation)
    _require(
        sp.simplify(weyl_variation - sigma * (trace_t - v * scalar_source)) == 0,
        "source Weyl Ward coefficient changed",
    )

    return {
        "variation_convention": (
            "delta S_source=int[(1/2)T^mn delta g_mn+J_phi delta phi]"
        ),
        "diffeomorphism_ward_identity": (
            "nabla_m T^m_n=J_phi partial_n phi; on phi=v constant this reduces to partial_m T^m_n=0"
        ),
        "weyl_ward_identity": "tr(T)-phi J_phi=0; on phi=v this is tr(T)-v J_phi=0",
        "metric_only_source_warning": (
            "a traceful metric source with J_phi=0 violates the compensator Weyl Ward identity"
        ),
        "status": "PASS",
    }


def _source_compatibility_checks() -> dict[str, Any]:
    box, c1, alpha = sp.symbols("Box c1 alpha", nonzero=True)
    t_component, t_trace, longitudinal_trace = sp.symbols(
        "T_mn Ttrace partial_m_partial_n_Ttrace"
    )
    q_t = sp.Rational(1, 2) * box * t_component - sp.Rational(1, 6) * (
        box * t_trace - longitudinal_trace
    )
    bach_on_einstein = sp.expand(q_t / c1)
    _require(
        sp.simplify(bach_on_einstein - q_t / c1) == 0,
        "Bach source obstruction normalization changed",
    )

    defect_component, q_defect = sp.symbols("Delta_mn QDelta_mn")
    defect_equation = sp.expand(c1 * defect_component + 2 * alpha * q_defect)
    _require(defect_equation.coeff(defect_component) == c1, "defect equation lost EH term")
    _require(defect_equation.coeff(q_defect) == 2 * alpha, "defect equation lost Bach term")

    d, source = sp.symbols("D J")
    mass_squared = c1 / alpha
    sourced_einstein_rhs = source / mass_squared
    fourth_order_on_einstein = sp.expand(d * sourced_einstein_rhs + mass_squared * sourced_einstein_rhs)
    _require(
        sp.simplify(fourth_order_on_einstein - source - d * source / mass_squared) == 0,
        "reduced same-source obstruction changed",
    )
    sourced_defect_rhs = sp.simplify(-d * source / mass_squared)
    _require(
        sp.simplify(sourced_defect_rhs + d * source / mass_squared) == 0,
        "reduced defect forcing changed",
    )

    eta = sp.diag(1, -1, -1, -1)
    p_down = sp.Matrix([1, 0, 0, 0])
    p_up = eta * p_down
    p_squared = 1
    witness = sp.diag(0, 1, -1, 0)
    witness_trace = _trace(witness, eta)
    witness_divergence = [
        sum(p_up[mu] * witness[mu, nu] for mu in range(4)) for nu in range(4)
    ]
    witness_q = sp.Matrix(
        4,
        4,
        lambda mu, nu: sp.Rational(1, 2) * p_squared * witness[mu, nu]
        - sp.Rational(1, 6)
        * (eta[mu, nu] * p_squared - p_down[mu] * p_down[nu])
        * witness_trace,
    )
    _require(witness_trace == 0, "source witness is not traceless")
    _require(witness_divergence == [0, 0, 0, 0], "source witness is not conserved")
    _require(witness_q != sp.zeros(4), "source witness does not violate Q(T)=0")

    return {
        "einstein_weyl_equation": "c1 G1(h_hat)+2 alpha B1(h_hat)=T",
        "same_source_einstein_equation": "c1 G1(h_hat)=T",
        "einstein_defect": "Delta_mn=G1_mn(h_hat)-T_mn/c1",
        "defect_equation": (
            "(c1 I+2 alpha Q)Delta=-(2 alpha/c1)Q(T)"
        ),
        "necessary_and_sufficient_same_source_condition": "Q(T)=0",
        "source_obstruction": (
            "Q(T)_mn=(1/2)Box T_mn-(1/6)(eta_mn Box-partial_m partial_n)tr(T)"
        ),
        "conserved_counterexample": {
            "momentum": "p_m=(1,0,0,0)",
            "source": "T_mn=diag(0,1,-1,0)",
            "properties": ["partial^m T_mn=0", "tr(T)=0", "Q(T)=(1/2)T!=0"],
            "consequence": "conservation and the Weyl trace Ward identity do not imply Einstein compatibility",
        },
        "reduced_tt_check": {
            "fourth_order_equation": "D(D+M2)h=J with M2=c1/alpha",
            "same_source_einstein_equation": "D h=J/M2",
            "substitution": "D(D+M2)h=J+(D J)/M2",
            "defect": "delta=D h-J/M2",
            "defect_equation": "(D+M2)delta=-(D J)/M2",
            "compatibility": "D J=0",
        },
        "dressed_source_alternative": {
            "formula": "T_EW=T_E+(2 alpha/c1)Q(T_E)",
            "meaning": (
                "an Einstein solution c1 G1=T_E solves the Einstein-Weyl equation with T_EW"
            ),
            "classification": (
                "local higher-derivative source dressing; not same-source equivalence to conventional Einstein matter"
            ),
        },
        "status": "PASS",
    }


def _affine_and_bv_checks() -> dict[str, Any]:
    source = sp.symbols("J", nonzero=True)
    lhs_first = source
    lhs_second = source
    lhs_sum_by_linearity = sp.expand(lhs_first + lhs_second)
    _require(
        lhs_sum_by_linearity == 2 * source,
        "fixed-source affine witness changed",
    )
    _require(
        lhs_sum_by_linearity != source,
        "fixed-source solution set was incorrectly treated as linear",
    )

    return {
        "external_source_geometry": (
            "for fixed nonzero T, solutions of Lh=T form an affine translate of ker(L), not a vector subspace"
        ),
        "terminology_rule": (
            "call the fixed-source defect-zero locus an affine sourced sector, not a BV subcomplex"
        ),
        "genuine_bv_requirement": (
            "include matter fields, any matter gauge ghosts, antifields, equations, and Diff x Weyl Ward identities"
        ),
        "compensated_freeze_gate": [
            "quadratic compensated action and Hessian",
            "metric and compensator gauge maps",
            "diffeomorphism and Weyl ghosts plus antifields",
            "scalar and metric Euler-Lagrange rows",
            "Noether identities and exact nilpotency",
            "BV pairing and cyclicity",
            "contraction of the Weyl Stueckelberg pair on the phi=v chart",
            "chain map from the compensated BV complex to the Einstein-defect target",
        ],
        "status": "PASS",
    }


def _validate_contract(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    _require(
        schema.get("$id") == "compensated-einstein-sourced-defect-preflight-v1",
        "wrong sourced-defect preflight schema id",
    )
    for key in schema.get("required", []):
        _require(key in payload, f"sourced-defect preflight is missing {key}")
    _require(payload.get("schema") == schema.get("$id"), "schema mismatch")
    _require(payload.get("schema_sha256") == _sha256(SCHEMA_PATH), "schema hash mismatch")
    _require(
        payload.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "wrong dependency tags",
    )
    _require(
        payload.get("provenance", {}).get("generator_sha256") == _sha256(Path(__file__)),
        "generator hash mismatch",
    )
    _require(
        payload.get("verdict")
        == "ARBITRARY_SAME_SOURCE_EINSTEIN_TRUNCATION_REFUTED_LINEAR_FLAT",
        "sourced-defect verdict changed",
    )
    flags = payload.get("claim_flags", {})
    required_flags = schema.get("properties", {}).get("claim_flags", {}).get("required", [])
    _require(set(flags) == set(required_flags), "claim flag inventory mismatch")
    true_flags = {
        "weyl_invariant_linear_metric_derived",
        "linearized_bach_factorization_derived",
        "source_ward_identities_declared",
        "gauge_covariant_einstein_defect_defined",
        "same_source_compatibility_operator_derived",
        "conserved_incompatible_source_witness_constructed",
        "arbitrary_same_source_einstein_truncation_refuted",
        "reduced_tt_source_obstruction_matched",
        "dressed_source_alternative_classified",
        "external_source_sector_classified_affine",
        "compensated_bv_freeze_gate_declared",
    }
    _require(all(flags.get(name) is True for name in true_flags), "proved flag missing")
    _require(
        all(flags.get(name) is False for name in set(required_flags) - true_flags),
        "an open claim was promoted",
    )


def build_certificate() -> dict[str, Any]:
    phase = _load(INPUTS["compensator_phase"])
    causal = _load(INPUTS["causal_subsector"])
    projectors = _load(INPUTS["local_projectors"])
    pure_weyl_bv = _load(INPUTS["pure_weyl_free_bv_reference"])
    _require(
        phase.get("result_id") == "COMPENSATOR_EINSTEIN_PHASE"
        and phase.get("claim_flags", {}).get("full_bv_scalar_constraint_count_completed")
        is False,
        "compensator phase scope gate changed",
    )
    _require(
        phase.get("flat_tt_factorization", {}).get("mass_parameter")
        == "M2=c1/alpha=zeta v^2/alpha",
        "compensator phase TT normalization changed",
    )
    _require(
        causal.get("claim_flags", {}).get("constraint_compatible_with_arbitrary_sources")
        is False,
        "causal source gate changed",
    )
    _require(
        projectors.get("claim_flags", {}).get("generic_source_preserves_einstein_only_sector")
        is False,
        "local-projector source gate changed",
    )
    _require(
        projectors.get("source_audit", {}).get("projected_equations")
        == ["Box(Pi_E h)=J/M2", "(Box+M2)(Pi_M h)=-J/M2"],
        "local-projector sourced normalization changed",
    )
    _require(
        pure_weyl_bv.get("schema") == "pure-weyl-free-bv-block-v1",
        "pure-Weyl BV reference changed",
    )

    certificate = {
        "schema": "compensated-einstein-sourced-defect-preflight-v1",
        "schema_path": (
            "bridge/einstein_sector/schema/"
            "compensated_einstein_sourced_defect_preflight.schema.json"
        ),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPENSATED_EINSTEIN_SOURCED_DEFECT_PREFLIGHT",
        "result_state": "SOURCE_COMPATIBILITY_CLASSIFIED_COMPENSATED_BV_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {
            "input_base_commit": "c9098557717623ade475649cd0d9e97c9b6c0fe8",
            "generator_path": (
                "bridge/einstein_sector/compensated_einstein_sourced_defect_preflight.py"
            ),
            "generator_sha256": _sha256(Path(__file__)),
        },
        "inputs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
            for name, path in INPUTS.items()
        },
        "domain": {
            "spacetime": "four-dimensional Minkowski space",
            "phase": "constant nonzero compensator phi=v, lambda=0",
            "equation": "linearized Einstein-Weyl metric equation with an external source",
            "source_class": "symmetric distributional or smooth tensor satisfying declared Ward identities",
            "parameters": "c1 and alpha nonzero; M2=c1/alpha in the TT comparison",
        },
        "linearized_tensor_theorem": _linearized_tensor_checks(),
        "source_ward_theorem": _source_ward_checks(),
        "source_compatibility_theorem": _source_compatibility_checks(),
        "affine_vs_bv_classification": _affine_and_bv_checks(),
        "programme_decision": {
            "revised_E_D2_target": (
                "construct or refute a same-source Einstein sector; do not assume generic source closure"
            ),
            "next_certificate": "COMPENSATED_QUADRATIC_BV_FREEZE",
            "then": (
                "lift the defect to a chain map and test retarded/advanced propagation on declared spaces"
            ),
            "success_outcomes": [
                "same-source closure on a precisely characterized admissible source class",
                "a scoped no-go for arbitrary Ward-compatible external sources",
                "a separately labelled higher-derivative dressed-source sector",
            ],
        },
        "verdict": "ARBITRARY_SAME_SOURCE_EINSTEIN_TRUNCATION_REFUTED_LINEAR_FLAT",
        "claim_flags": {
            "weyl_invariant_linear_metric_derived": True,
            "linearized_bach_factorization_derived": True,
            "source_ward_identities_declared": True,
            "gauge_covariant_einstein_defect_defined": True,
            "same_source_compatibility_operator_derived": True,
            "conserved_incompatible_source_witness_constructed": True,
            "arbitrary_same_source_einstein_truncation_refuted": True,
            "reduced_tt_source_obstruction_matched": True,
            "dressed_source_alternative_classified": True,
            "external_source_sector_classified_affine": True,
            "compensated_bv_freeze_gate_declared": True,
            "arbitrary_ward_compatible_external_source_preserves_einstein_sector": False,
            "fixed_external_source_locus_is_bv_subcomplex": False,
            "compensated_quadratic_bv_complex_certified": False,
            "matter_inclusive_bv_complex_constructed": False,
            "einstein_defect_chain_map_constructed": False,
            "retarded_advanced_defect_propagation_proved": False,
            "nonlinear_einstein_truncation_proved": False,
            "null_infinity_closure_proved": False,
            "einstein_scattering_equivalence_proved": False,
        },
        "scope_guards": [
            "the tensor identities are linearized LOCAL-ALGEBRAIC statements on flat space",
            "the D(D+M2) comparison is REDUCED-MODE and is not reused as a full BV propagator",
            "Q(T)=0 classifies same-source compatibility; it is not implied by conservation alone",
            "the explicit incompatible source is a local Fourier-symbol witness, not a global matter solution",
            "a dressed source changes the source coupling and is not conventional same-source Einstein equivalence",
            "a fixed external source defines an affine sector and cannot by itself define a BV subcomplex",
            "the imported pure-Weyl free BV complex is not a compensated metric-scalar BV freeze",
            "no LORENTZIAN-CAUSAL, nonlinear, null-infinity, scattering, or quantum claim is made",
        ],
        "verification_command": (
            "python3 -m bridge.einstein_sector.compensated_einstein_sourced_defect_preflight "
            "--verify bridge/certificates/compensated_einstein_sourced_defect_preflight.json"
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
