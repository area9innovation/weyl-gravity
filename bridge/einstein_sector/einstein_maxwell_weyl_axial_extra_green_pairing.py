"""Exact reduced-Green pairing on the generic axial extra module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
GREEN_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_green_current.json"
OPERATOR_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_extra_green_pairing.schema.json"


class AxialExtraGreenPairingError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialExtraGreenPairingError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _shell_reduce(expression: sp.Expr, frequency: sp.Symbol, momentum: sp.Symbol, eigenvalue: sp.Symbol) -> sp.Expr:
    shell = sp.Poly(frequency**2 - momentum**2 - eigenvalue + sp.Rational(2, 3), frequency)
    return sp.factor(sp.rem(sp.Poly(sp.expand(expression), frequency), shell).as_expr())


def _pairing() -> dict[str, Any]:
    green = json.loads(GREEN_CERTIFICATE.read_text(encoding="utf-8"))
    eigenvalue, momentum, frequency = sp.symbols("lambda k omega", real=True)
    local_symbols = {"lam": eigenvalue, "k": momentum, "omega": frequency, "I": sp.I}
    representatives = [
        sp.Matrix([-(momentum**2 + eigenvalue), momentum * frequency, eigenvalue, 0]),
        sp.Matrix([-momentum * frequency, momentum**2 - sp.Rational(2, 3), 0, eigenvalue]),
    ]

    def coefficient(value: str) -> sp.Expr:
        return sp.sympify(value.replace("lambda", "lam"), locals=local_symbols)

    def current(first: sp.Matrix, second: sp.Matrix) -> sp.Expr:
        result = sp.S.Zero
        for term in green["reduced_current"]["time_current_terms"]:
            result += (
                coefficient(term["coefficient"])
                * (-sp.I * frequency) ** term["u_t_order"]
                * (sp.I * momentum) ** term["u_x_order"]
                * (sp.I * frequency) ** term["v_t_order"]
                * (-sp.I * momentum) ** term["v_x_order"]
                * first[term["u_component"]]
                * second[term["v_component"]]
            )
        return _shell_reduce(result, frequency, momentum, eigenvalue)

    coordinate_gram = sp.Matrix(
        2, 2, lambda left, right: current(representatives[left], representatives[right])
    ).applyfunc(sp.factor)
    _require(coordinate_gram == coordinate_gram.T, "extra current Gram matrix is not symmetric")
    expected = sp.Matrix(
        [
            [
                eigenvalue
                * (momentum**2 * (3 * eigenvalue - 2) ** 2 + 9 * eigenvalue**2 * (eigenvalue - 2))
                / 6,
                momentum * eigenvalue * (3 * eigenvalue - 2) ** 2 * frequency / 6,
            ],
            [
                momentum * eigenvalue * (3 * eigenvalue - 2) ** 2 * frequency / 6,
                eigenvalue
                * (3 * momentum**2 * (3 * eigenvalue - 2) ** 2 + 4 * (9 * eigenvalue - 2))
                / 18,
            ],
        ]
    )
    normalized = expected.applyfunc(sp.factor)
    normalization_remainder = (
        coordinate_gram - (-sp.I * frequency) * normalized
    ).applyfunc(lambda value: _shell_reduce(value, frequency, momentum, eigenvalue))
    _require(normalization_remainder == sp.zeros(2), "normalized extra Gram matrix changed")
    determinant = _shell_reduce(normalized.det(), frequency, momentum, eigenvalue)
    expected_determinant = eigenvalue**4 * (eigenvalue - 2) * (9 * eigenvalue - 2) / 3
    _require(sp.factor(determinant - expected_determinant) == 0, "extra Gram determinant changed")
    leading_minor = sp.factor(normalized[0, 0])
    return {
        "extra_representative_order": ["e_1", "e_2"],
        "coefficient_order": ["H_t", "H_x", "Q_t", "Q_x"],
        "representatives": [[str(value) for value in vector] for vector in representatives],
        "shell": "omega^2=k^2+lambda-2/3",
        "coordinate_Jt_Gram": [[str(sp.factor(value)) for value in coordinate_gram.row(row)] for row in range(2)],
        "normalization": "N_extra=Jt_extra/(-I*omega) for positive omega, before the positive spherical harmonic norm and circle volume",
        "normalized_Gram": [[str(sp.factor(value)) for value in normalized.row(row)] for row in range(2)],
        "first_principal_minor": str(leading_minor),
        "determinant": str(sp.factor(determinant)),
        "physical_sign_check": {
            "domain": "lambda=ell(ell+1)>=6, real k, positive omega",
            "first_principal_minor_positive": True,
            "determinant_positive": True,
            "signature": [2, 0],
        },
        "nondegenerate_for_all_physical_ell_ge_2": True,
    }


def build_certificate() -> dict[str, Any]:
    green = json.loads(GREEN_CERTIFICATE.read_text(encoding="utf-8"))
    operator = json.loads(OPERATOR_CERTIFICATE.read_text(encoding="utf-8"))
    _require(green["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT", "Green-current input changed")
    _require(operator["result_id"] == "EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR", "operator input changed")
    return {
        "schema": "einstein-maxwell-weyl-axial-extra-green-pairing-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING",
        "result_state": "GENERIC_AXIAL_EXTRA_MODULE_NONRADICAL_POSITIVE_IN_REDUCED_HESSIAN_GREEN_CONVENTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G2_GENERIC_AXIAL_EXTRA_REDUCED_GREEN_PAIRING",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                str(path.relative_to(ROOT)): _sha256(path)
                for path in (GREEN_CERTIFICATE, OPERATOR_CERTIFICATE)
            },
        },
        "domain": "the two-summand generic axial extra solution module at lambda=ell(ell+1)>=6 and real compact momentum k, paired by the certified reduced-Hessian local Green current",
        "pairing": _pairing(),
        "classification": {
            "extra_module_nonradical_for_reduced_Green_current": True,
            "reduced_Green_signature_positive_two": True,
            "direct_four_dimensional_Lee_Wald_match": False,
            "physical_norm_or_ghost_claim": False,
            "particle_claim": False,
            "Lorentzian_causal_claim": False,
        },
        "interpretation": "The two generic axial extra solution summands survive the reduced-Hessian Green pairing: their Gram matrix is nondegenerate and positive in the declared positive-frequency convention for every physical ell>=2. This rules out a reduced-current radical explanation of the extra module. Until the current is matched to the direct four-dimensional Lee-Wald normalization, it is not a physical positive-norm, negative-norm, ghost, or particle theorem.",
        "next_gate": "evaluate the direct four-dimensional Weyl-Maxwell Lee-Wald current on the same two representatives and prove its relation to the reduced Green current, including all harmonic norms and improvement terms",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE result concerns the exact local reduced-Hessian Green pairing. It does not certify the covariant Lee-Wald phase space, a positive-frequency Hilbert space, causal boundary admissibility, scattering, or quantum unitarity.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_green_pairing --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_green_pairing.json",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_green_pairing",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(json.loads(path.read_text(encoding="utf-8")) == build_certificate(), f"stale extra Green pairing: {path}")


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
