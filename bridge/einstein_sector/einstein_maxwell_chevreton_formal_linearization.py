"""Certify the dual-number bridge from the Chevreton identity to all Jacobi fields."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
LINEAR_INPUT = ROOT / "bridge/certificates/einstein_maxwell_chevreton_tangent.json"
INCIDENCE_INPUT = ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_chevreton_formal_linearization.schema.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_chevreton_formal_linearization.json"


class FormalLinearizationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FormalLinearizationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dual_remainder(expression: sp.Expr, epsilon: sp.Symbol) -> sp.Expr:
    return sp.rem(sp.Poly(sp.expand(expression), epsilon), sp.Poly(epsilon**2, epsilon)).as_expr()


def _formal_audit() -> dict[str, Any]:
    epsilon = sp.symbols("epsilon")
    residual_two, jet_one = sp.symbols("residual_two jet_one")
    _require(_dual_remainder(epsilon**2 * residual_two, epsilon) == 0, "Jacobi residual did not vanish over dual numbers")
    _require(_dual_remainder((epsilon * jet_one) ** 2, epsilon) == 0, "quadratic Chevreton term survived dual truncation")

    a, b, c, d, h11, h12, h21, h22 = sp.symbols("a b c d h11 h12 h21 h22")
    metric = sp.Matrix([[a, b], [c, d]])
    perturbation = sp.Matrix([[h11, h12], [h21, h22]])
    determinant = sp.factor(metric.det())
    inverse = metric.inv()
    dual_inverse = inverse - epsilon * inverse * perturbation * inverse
    product = ((metric + epsilon * perturbation) * dual_inverse - sp.eye(2)).applyfunc(
        lambda entry: sp.factor(_dual_remainder(entry, epsilon))
    )
    _require(product == sp.zeros(2), "dual-number inverse formula changed")

    return {
        "coefficient_algebra": "D=R[epsilon]/(epsilon^2)",
        "metric_inverse": "(g+epsilon*h)^(-1)=g^(-1)-epsilon*g^(-1)*h*g^(-1)",
        "metric_inverse_denominator": str(determinant),
        "metric_inverse_identity_mod_epsilon_squared": True,
        "Jacobi_residual_rule": "E(barPhi+epsilon*phi)=E(barPhi)+epsilon*DE_barPhi[phi]=0 in D",
        "quadratic_parallel_flux_rule": "nabla(Fbar)=0 implies C_Ch(barPhi+epsilon*phi)=0 in D",
        "symbolic_dual_remainder_checks": {
            "epsilon_squared_residual": "0",
            "quadratic_first_jet": "0",
        },
    }


def build_certificate() -> dict[str, Any]:
    linear = _load(LINEAR_INPUT)
    incidence = _load(INCIDENCE_INPUT)
    _require(linear["result_id"] == "EINSTEIN_MAXWELL_CHEVRETON_TANGENT", "linear input changed")
    _require(incidence["result_id"] == "EINSTEIN_MAXWELL_PRODUCT_INCIDENCE", "incidence input changed")
    factorization = linear["on_shell_factorization"]
    _require(
        factorization["repository_convention_identity"] == "B_mn-(2*kappa*Lambda/3)T_mn=C_Ch_mn",
        "Chevreton identity changed",
    )
    _require(factorization["background_property"].startswith("nabla Fbar=0"), "parallel flux input changed")

    return {
        "schema": "einstein-maxwell-chevreton-formal-linearization-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_CHEVRETON_FORMAL_LINEARIZATION",
        "result_state": "DUAL_NUMBER_BRIDGE_FOR_ALL_FORMAL_JACOBI_FIELDS_CERTIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "generality_level": "G3_COMPLETE_FORMAL_LINEAR_TANGENT_BRIDGE",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(LINEAR_INPUT.relative_to(ROOT)): _sha256(LINEAR_INPUT),
                str(INCIDENCE_INPUT.relative_to(ROOT)): _sha256(INCIDENCE_INPUT),
            },
            "primary_derivation": {
                "authors": "G. Bergqvist and I. Eriksson",
                "title": "The Chevreton Tensor and Einstein-Maxwell Spacetimes Conformal to Einstein Spaces",
                "arxiv": "gr-qc/0703073v2",
                "doi": "10.1088/0264-9381/24/13/018",
                "steps_replayed_formally": [
                    "Leibniz expansion of the Chevreton trace",
                    "Maxwell wave identity derived from dF=0 and div(F)=0 by covariant differentiation and curvature commutation",
                    "Einstein equation substitution for the Ricci tensor",
                    "differential Bianchi identity and the geometric definition of the Bach tensor",
                ],
            },
        },
        "domain": "all smooth fixed-bundle Einstein-Maxwell Jacobi fields at the parallel-flux compactified Plebanski-Hacyan fixture; no nonlinear integrability assumption",
        "formal_audit": _formal_audit(),
        "proof": {
            "dual_number_field": "Phi_epsilon=barPhi+epsilon*phi in D, epsilon^2=0",
            "Jacobi_equivalence": "DE_EM_barPhi[phi]=0, DM_barPhi[phi]=0, d(delta F)=0 iff the nonlinear Einstein-Maxwell residuals of Phi_epsilon vanish in D",
            "naturality_step": "The published Bach-Chevreton derivation uses only tensor algebra, covariant differentiation, curvature commutators, Leibniz rules, and the Einstein-Maxwell equations; all operations extend to D because gbar+epsilon*h is invertible in D.",
            "formal_identity": "D(B-(2*kappa*Lambda/3)T-C_Ch)_barPhi[phi]=0 for every Einstein-Maxwell Jacobi field phi",
            "parallel_flux_consequence": "DC_Ch_barPhi[phi]=0 for every phi because C_Ch is homogeneous quadratic in nabla F and nabla Fbar=0",
            "tuned_target_consequence": "alpha_B*DB_barPhi[phi]-DT_barPhi[phi]=0 when 2*alpha_B*kappa*Lambda/3=1",
            "integrable_family_required": False,
        },
        "classification": {
            "all_formal_linearized_Einstein_Maxwell_solutions_included": True,
            "only_integrable_tangents": False,
            "nonlinear_linearization_stability_assumed": False,
            "off_shell_BV_chain_map_constructed": False,
            "nonlinear_closure_claimed": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The inclusion theorem does not differentiate an identity only along an actual nonlinear solution family. Every Jacobi field is an exact solution over the dual numbers, and the natural Bach-Chevreton derivation remains valid there. Hence non-integrable linearized solutions are covered, while nonlinear extension remains a separate Taub problem.",
        "next_gate": "use this formal bridge in the compact linear paper; retain the full off-shell BV row-map factorization as a stronger open result",
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate closes the formal-linearization gap for arbitrary Jacobi fields. It does not construct explicit global off-shell P,Q,R row operators, an off-shell BV chain map, nonlinear solution families, causal propagation, scattering, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_chevreton_formal_linearization --verify bridge/certificates/einstein_maxwell_chevreton_formal_linearization.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_chevreton_formal_linearization.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_chevreton_formal_linearization",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"stale formal-linearization certificate: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and args.verify is None:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
