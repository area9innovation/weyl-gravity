"""Independent verifier for the Sobolev linearization-stability gate.

This rail does not import the producer.  It independently derives the
Fourier multiplier and normalized approximate-kernel estimate for the
certified ell=2, k=0 p-primary shell.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1.json"
ATLAS = ROOT / "residual_atlas/einstein-weyl-sobolev-linearization-stability-gate-fragment-v1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-sobolev-linearization-stability-gate-v1.schema.json"

EXPECTED_INPUTS = {
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json": "935a3c264858c4f425025f2f1adf50886739bb84cdc86331120058c9ce7bd545",
    "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json": "c80967db8cce02594a346bef3ec6a0f1d6863c85167aec7b661d2d102a248065",
    "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json": "d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd",
    "bridge/certificates/einstein_maxwell_weyl_harmonic_sign_resonance_join.json": "723083a24436059f19ae70f53287e6141c58f54b27eae50064896fd12eba7fbb",
    "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json": "26fae23935261735385d6a7796d5f10db3404f863d2bdf85c7b5d0869afd0006",
}


class IndependentSobolevGateVerificationError(RuntimeError):
    """Raised when the independent closed-range audit fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentSobolevGateVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _independent_multiplier_audit(payload: dict[str, Any]) -> None:
    xi = sp.symbols("xi", real=True)
    n = sp.symbols("n", integer=True, positive=True)

    # Independently specialize the imported p-primary dispersion relation.
    lam = sp.Integer(2) * (sp.Integer(2) + 1)
    k = sp.Integer(0)
    omega_squared = k**2 + lam - sp.Rational(2, 3)
    _require(omega_squared == sp.Rational(16, 3), "p-primary shell changed")
    omega = sp.sqrt(omega_squared)

    # Bessel-potential conjugation H^(s+2)->H^s removes s.
    multiplier = sp.factor((omega_squared - xi**2) / (1 + xi**2))
    recorded = sp.sympify(payload["closed_range_obstruction"]["fourier_multiplier"], locals={"xi": xi})
    _require(sp.factor(recorded - multiplier) == 0, "Fourier multiplier changed")
    _require(sp.factor(multiplier.subs(xi, omega)) == 0, "real characteristic zero missing")
    _require(sp.factor(multiplier.subs(xi, -omega)) == 0, "negative characteristic zero missing")

    # On I_n=[omega,omega+1/n], |omega^2-xi^2| is bounded by
    # 2*omega/n+1/n^2 and the denominator is at least 1+omega^2.
    bound = sp.factor((2 * omega / n + 1 / n**2) / (1 + omega_squared))
    recorded_bound = sp.sympify(
        payload["closed_range_obstruction"]["approximate_kernel"]["upper_bound"],
        locals={"n": n},
    )
    _require(sp.factor(recorded_bound - bound) == 0, "approximate-kernel bound changed")
    _require(sp.limit(recorded_bound, n, sp.oo) == 0, "approximate kernel does not converge")

    # A multiplier which is nonzero almost everywhere has zero kernel and
    # dense range.  The normalized approximate kernel rules out a lower
    # bound, hence rules out closed range for this injective operator.
    consequences = payload["functional_analytic_consequences"]
    _require(consequences["closed_range"] is False, "closed range was promoted")
    _require(consequences["fredholm"] is False, "Fredholmness was promoted")
    _require(consequences["bounded_generalized_inverse"] is False, "bounded inverse was promoted")

    mutated = sp.factor((omega_squared + 1 - xi**2) / (1 + xi**2))
    recorded_mutation = sp.sympify(
        payload["closed_range_obstruction"]["mutation_control"]["mutated_multiplier"],
        locals={"xi": xi},
    )
    _require(sp.factor(recorded_mutation - mutated) == 0, "mutation multiplier changed")
    _require(sp.factor(mutated.subs(xi, omega)) == sp.Rational(3, 19), "mutation did not lift shell zero")


def verify_certificate(certificate_path: Path = CERTIFICATE, atlas_path: Path = ATLAS) -> None:
    payload = _load(certificate_path)
    jsonschema.Draft202012Validator(_load(SCHEMA)).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")

    imports = {row["path"]: row["sha256"] for row in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED_INPUTS, "input ledger changed")
    for relative, digest in EXPECTED_INPUTS.items():
        _require(_sha256(ROOT / relative) == digest, f"input drift: {relative}")

    finite = _load(ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json")
    _require(finite["lifecycle_state"] == "THEOREM_FROZEN", "finite theorem not frozen")
    _require(finite["classification"]["five_and_only_five_EP_cokernel_covectors"] is True, "finite cokernel changed")
    _require(finite["correction_classes"]["finite_exponential_polynomial"]["status"] == "THEOREM_FROZEN", "EP theorem changed")
    _require(
        _load(ROOT / "bridge/certificates/einstein_maxwell_weyl_harmonic_taub_sign_classification.json")
        ["harmonic_sign_ledger"]["generic_extra_p_primary"]["frequency_squared"]
        == "k^2+lambda-2/3>0",
        "p-primary dispersion input changed",
    )

    _independent_multiplier_audit(payload)
    classification = payload["classification"]
    for key in (
        "closed_range_certified",
        "fredholm_certified",
        "five_dimensional_sobolev_adjoint_cokernel_certified",
        "sobolev_linearization_stability_promoted",
        "compact_cauchy_constraint_problem_closed",
        "global_nonlinear_or_stability_claim",
        "lorentzian_causal_claim",
        "quantum_claim",
    ):
        _require(classification[key] is False, f"forbidden promotion: {key}")
    _require(classification["first_failed_hypothesis_certified"] is True, "failed-hypothesis witness missing")
    _require(payload["cauchy_constraint_gate"]["status"] == "OPEN_SEPARATE_PROBLEM", "Cauchy gate was silently closed")

    atlas = _load(atlas_path)
    _require(atlas["schema"] == "pure-weyl-residual-atlas-fragment-v1", "atlas schema changed")
    _require(len(atlas["entries"]) == 1, "atlas entry count changed")
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(certificate_path), "atlas evidence hash drift")
    _require(
        entry["descriptions"]
        == {
            "causal": "NO_CERTIFIED_MAP",
            "symplectic": "NO_CERTIFIED_MAP",
            "nonlinear": "OBSTRUCTED",
            "observational": "NO_CERTIFIED_MAP",
            "quantum": "NO_CERTIFIED_MAP",
        },
        "atlas fail-closed statuses changed",
    )


def main() -> int:
    verify_certificate()
    print("independent Sobolev linearization-stability gate verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
