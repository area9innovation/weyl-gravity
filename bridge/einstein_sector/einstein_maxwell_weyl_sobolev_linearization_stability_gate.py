"""Exact closed-range obstruction to a spacetime-Sobolev promotion.

The finite exponential-polynomial theorem inverts nonzero scalar factors by
allowing secular primitives.  On unweighted spacetime Sobolev spaces the same
real characteristic factors instead have dense nonclosed range.  A single
certified p-primary extra-mode block therefore obstructs Fredholmness before
any nonlinear momentum-map normal form can be invoked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/einstein-weyl-sobolev-linearization-stability-gate-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-sobolev-linearization-stability-gate-v1.schema.json"
PRODUCER_PATH = ROOT / "bridge/einstein_sector/einstein_maxwell_weyl_sobolev_linearization_stability_gate.py"

INPUTS = {
    "finite_harmonic_structural_freeze": (
        "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
        "43b212dafc623909ce76ff31bcb1b3fab7054a9fa7a2ff1b757e630f26cf1740",
        "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1",
    ),
    "abstract_finite_block": (
        "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
        "c80967db8cce02594a346bef3ec6a0f1d6863c85167aec7b661d2d102a248065",
        None,
    ),
    "complete_finite_smooth_global": (
        "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
        "d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd",
        None,
    ),
    "sign_resonance_join": (
        "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json",
        "723083a24436059f19ae70f53287e6141c58f54b27eae50064896fd12eba7fbb",
        None,
    ),
    "harmonic_taub_sign": (
        "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json",
        "26fae23935261735385d6a7796d5f10db3404f863d2bdf85c7b5d0869afd0006",
        "EINSTEIN_MAXWELL_WEYL_HARMONIC_TAUB_SIGN_CLASSIFICATION",
    ),
}


class SobolevCompletionGateError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SobolevCompletionGateError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _imports() -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    ledger: list[dict[str, str]] = []
    payloads: dict[str, dict[str, Any]] = {}
    for name, (relative, expected_hash, expected_id) in INPUTS.items():
        path = ROOT / relative
        _require(path.exists(), f"missing input: {relative}")
        actual = _sha256(path)
        _require(actual == expected_hash, f"input hash drift: {name}")
        payload = _load(path)
        if expected_id is not None:
            _require(payload.get("result_id") == expected_id, f"result id drift: {name}")
        payloads[name] = payload
        ledger.append({"name": name, "path": relative, "sha256": actual, "result_id": payload.get("result_id", payload.get("schema", "NO_RESULT_ID"))})
    return ledger, payloads


def _audit_finite_theorem(data: dict[str, dict[str, Any]]) -> None:
    structural = data["finite_harmonic_structural_freeze"]
    _require(structural["lifecycle_state"] == "THEOREM_FROZEN", "finite theorem not frozen")
    _require(structural["classification"]["five_and_only_five_EP_cokernel_covectors"] is True, "finite cokernel count changed")
    _require(structural["correction_classes"]["finite_exponential_polynomial"]["status"] == "THEOREM_FROZEN", "EP sufficiency changed")
    generic = structural["output_strata"][0]
    _require(generic["invariant_factors"] == ["1", "1", "p", "p*q"] and generic["zero_factors"] == 0, "generic Smith factors changed")
    zero_counts = [row["zero_factors"] for row in structural["output_strata"] if row["zero_factors"]]
    _require(zero_counts == [2, 3], "global zero-factor ledger changed")
    signs = data["harmonic_taub_sign"]
    _require(signs["harmonic_sign_ledger"]["generic_extra_p_primary"]["frequency_squared"] == "k^2+lambda-2/3>0", "p frequency changed")


def _closed_range_witness() -> dict[str, Any]:
    n = sp.symbols("n", integer=True, positive=True)
    xi = sp.symbols("xi", real=True)
    omega_squared = sp.Rational(16, 3)
    omega = sp.sqrt(omega_squared)
    multiplier = sp.factor((omega_squared - xi**2) / (1 + xi**2))
    _require(sp.factor(multiplier.subs(xi, omega)) == 0, "characteristic zero changed")
    bound = sp.factor((2 * omega / n + 1 / n**2) / (1 + omega_squared))
    _require(sp.limit(bound, n, sp.oo) == 0, "approximate-kernel bound does not vanish")
    mutated = sp.factor((omega_squared + 1 - xi**2) / (1 + xi**2))
    _require(sp.factor(mutated.subs(xi, omega)) == sp.Rational(3, 19), "decisive shell mutation changed")
    return {
        "spatial_fixture": {"ell": 2, "lambda": 6, "k": 0, "parity": "either", "extra_p_polarization": "one certified p-primary coordinate"},
        "frequency_squared": "16/3",
        "scalar_operator": "P_e=partial_t^2+16/3",
        "sobolev_map": "P_e:H^(s+2)(R_t)->H^s(R_t), any real s",
        "unitary_conjugate": "A_s=P_e*(1-partial_t^2)^(-1):L2(R)->L2(R)",
        "fourier_multiplier": str(multiplier),
        "approximate_kernel": {
            "fourier_support": "I_n=[omega_e,omega_e+1/n]",
            "normalization": "u_n has L2 norm 1",
            "upper_bound": str(bound),
            "limit": "0",
        },
        "kernel": "ker(A_s)=ker(A_s^*)={0}, because the multiplier vanishes only at two measure-zero frequencies",
        "range_closure": "closure ran(A_s)=L2, because ker(A_s^*)={0}",
        "range": "DENSE_NOT_CLOSED",
        "proof": "If ran(A_s) were closed, the injective multiplication operator would be bounded below on L2; the normalized u_n contradict that bound.",
        "mutation_control": {"mutated_multiplier": str(mutated), "value_at_original_shell": "3/19", "original_approximate_kernel_rejected": True},
    }


def build_certificate() -> dict[str, Any]:
    imported, data = _imports()
    _audit_finite_theorem(data)
    witness = _closed_range_witness()
    return {
        "schema": "einstein-maxwell-weyl-sobolev-linearization-stability-gate-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1",
        "result_state": "UNWEIGHTED_SPACETIME_SOBOLEV_CLOSED_RANGE_OBSTRUCTED_CAUCHY_CONSTRAINT_GATE_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "provenance": {"input_commit": "414853ed8", "producer": str(PRODUCER_PATH.relative_to(ROOT)), "producer_sha256": _sha256(PRODUCER_PATH), "imported_artifacts": imported},
        "declared_completion": {
            "spacetime": "R_t x S1_L x S2 on the fixed magnetic bundle P_N, N=2",
            "boundaries": "closed spatial Cauchy surface; unweighted full real time axis",
            "charge_sector": "fixed magnetic Chern component; no continuous magnetic-flux variation",
            "gauge_slice": "one complemented local-gauge-reduced p-primary harmonic master block; no global covariant Sobolev gauge slice is claimed",
            "correction_category": "unweighted spacetime Sobolev H^(s+2)->H^s on the scalar p block, equivalently the corresponding component of the mixed-order full operator",
            "regularity": "any real s for the linear obstruction; s>2 would be required for four-dimensional Sobolev-algebra estimates on local quadratic coefficients",
        },
        "closed_range_obstruction": witness,
        "functional_analytic_consequences": {
            "closed_range": False,
            "fredholm": False,
            "bounded_generalized_inverse": False,
            "implicit_function_or_momentum_map_normal_form_hypothesis": "FAILED_BEFORE_NONLINEAR_STEP",
            "full_operator_consequence": "The harmonic master block is reducing under the stationary product operator. A closed-range full realization would induce closed range on this complemented block, contradicting the witness.",
            "hilbert_adjoint_cokernel": "zero orthogonal cokernel but nonclosed range on the witnessed block",
            "five_taub_covector_comparison": "TYPE_MISMATCH: the five finite exponential-polynomial/Cauchy constraint covectors are not the Hilbert cokernel of this spacetime realization",
        },
        "surviving_finite_harmonic_statements": {
            "finite_exponential_polynomial_surjectivity": "CERTIFIED_UNCHANGED",
            "five_EP_zero_factors": "CERTIFIED_UNCHANGED",
            "finite_support_taub_necessity": "CERTIFIED_UNCHANGED_IN_ITS_DECLARED_CATEGORY",
            "density_implies_sobolev_surjectivity": False,
            "EP_secular_inverse_is_bounded_sobolev_inverse": False,
            "sobolev_sufficiency": False,
        },
        "cauchy_constraint_gate": {
            "status": "OPEN_SEPARATE_PROBLEM",
            "reason": "Arms--Marsden--Moncrief/Fischer--Marsden linearization stability is formulated for an elliptic constraint map on compact Cauchy data, not the unweighted full-time hyperbolic operator used in this obstruction.",
            "missing_objects": [
                "a complete Weyl-Maxwell Cauchy constraint map on a declared Sobolev gauge slice",
                "Douglis--Nirenberg ellipticity and closed range for its linearization",
                "identification of its full adjoint kernel with exactly the five lifted stabilizers",
                "smooth/tame nonlinear constraint-map estimates and a slice theorem on fixed P_N",
            ],
            "not_refuted": "A future compact-Cauchy constraint theorem may recover a five-dimensional adjoint cokernel; it is not implied by the finite EP theorem and is not disproved by the spacetime nonclosed-range result.",
        },
        "scope": {
            "theory": "Weyl-Maxwell target with Einstein-Maxwell image",
            "background": "compactified magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L x S2 spatial slice, unweighted R time",
            "charge_sector": "fixed magnetic U(1) bundle P_N, N=2",
            "carrier": "one complemented generic ell=2,k=0 p-primary master block inside the candidate Sobolev completion",
            "degree": "linear closed-range gate; quadratic consequences only as failed prerequisites",
            "parity": "either certified generic parity; one block suffices",
            "ell": 2,
            "m": "any fixed certified m",
            "k": 0,
            "omega": "real shell omega^2=16/3",
        },
        "classification": {
            "finite_harmonic_structural_theorem_imported": True,
            "explicit_sobolev_realization_declared": True,
            "closed_range_certified": False,
            "fredholm_certified": False,
            "five_dimensional_sobolev_adjoint_cokernel_certified": False,
            "sobolev_linearization_stability_promoted": False,
            "first_failed_hypothesis_certified": True,
            "compact_cauchy_constraint_problem_closed": False,
            "global_nonlinear_or_stability_claim": False,
            "lorentzian_causal_claim": False,
            "quantum_claim": False,
        },
        "claim_boundary": "This exact functional-analytic result proves dense nonclosed range for one real-characteristic p-primary block in every unweighted full-time Sobolev realization H^(s+2)(R)->H^s(R), hence obstructs Fredholm and implicit-function promotion of the finite exponential-polynomial theorem in that category. It does not analyze weighted/radiation spaces, finite time slabs, a compact-Cauchy elliptic constraint map, causal/retarded solutions, nonlinear existence, stability, observables, particles, scattering, positivity or quantum theory.",
        "verification_commands": [
            "PYTHONPATH=. python3 -m bridge.einstein_sector.einstein_maxwell_weyl_sobolev_linearization_stability_gate --check",
            "PYTHONPATH=. python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_sobolev_linearization_stability_gate",
            "PYTHONPATH=. python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_sobolev_linearization_stability_gate",
            "python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-sobolev-linearization-stability-gate-fragment-v1.json",
        ],
    }


def build_atlas(certificate: dict[str, Any], certificate_path: Path) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1", "schema_version": "1.0.0", "team": "einstein_nonlinear",
        "generated_by": str(PRODUCER_PATH.relative_to(ROOT)), "generated_by_sha256": _sha256(PRODUCER_PATH),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [{
            "id": "einstein.ph.wm.sobolev.full_time.closed_range_gate",
            "scope": certificate["scope"],
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": {"status": "CERTIFIED", "statement": "The witness uses the exact p shell omega^2=16/3."},
                "lee_wald": {"status": "NO_CERTIFIED_MAP", "statement": "No continuous Sobolev completion of the Lee-Wald form is certified here."},
                "taub_maps": {"status": "OPEN", "statement": "Finite EP Taub covectors remain certified; their compact-Cauchy Sobolev adjoint realization is open."},
                "resonance": {"status": "CERTIFIED", "statement": "The real characteristic zero creates the normalized approximate kernel."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OBSTRUCTED", "statement": "Unweighted spacetime Sobolev closed range fails before a bounded inverse can be defined."},
                    "smooth_secular": {"status": "NOT_APPLICABLE", "statement": "The finite exponential-polynomial theorem remains separate and certified."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No weighted or retarded realization is analyzed."},
                },
            },
            "evidence": [{"path": str(certificate_path.relative_to(ROOT)), "result_id": certificate["result_id"], "sha256": _sha256(certificate_path)}],
            "claim_boundary": certificate["claim_boundary"],
        }],
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
        expected = build_atlas(certificate, args.output)
        _require(args.atlas.exists() and _load(args.atlas) == expected, "atlas drift or missing")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    atlas = build_atlas(certificate, args.output)
    args.atlas.parent.mkdir(parents=True, exist_ok=True)
    args.atlas.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
