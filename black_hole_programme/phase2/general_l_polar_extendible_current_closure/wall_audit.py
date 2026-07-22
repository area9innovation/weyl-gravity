"""Exact exclusion of canonical-pivot determinant walls on the physical set."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

PKG = Path(__file__).resolve().parent
ART = PKG / "current_artifacts"
OUT = ART / "canonical-pivot-wall-certificate.json"
L, W, X = sp.symbols("Lambda omega x", real=True)


def from_terms(rows, variables):
    return sp.Poly.from_dict(
        {tuple(monomial): sp.Integer(coefficient) for monomial, coefficient in rows},
        variables,
        domain=sp.QQ,
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    matrix = json.loads((ART / "oscillatory-matrix-filtration.json").read_text())
    factors = matrix["leading_p0"]["factorization"]["factors"]
    polys = [
        sp.Poly.from_dict(
            {tuple(m): sp.sympify(c, locals={"I": sp.I}) for m, c in item["polynomial"]["terms"]},
            (L, W),
            extension=sp.I,
        )
        for item in factors
    ]
    p6 = next(poly for poly in polys if poly.total_degree() == 12)
    p20 = next(poly for poly in polys if poly.total_degree() == 42)

    delta = (
        L**3 - 24*L**2*W**2 - 5*L**2 + 48*L*W**2 + 12*sp.I*L*W
        + 6*L + 2048*W**6 - 1536*sp.I*W**5 - 256*W**4
        - 288*sp.I*W**3 - 36*sp.I*W
    )
    delta_norm = sp.Poly(
        sp.expand(delta * sp.conjugate(delta)), L, W, extension=sp.I
    )
    if p6 != delta_norm:
        raise RuntimeError("P6 is not the exact Delta norm")
    forced_real = sp.Poly(
        128*X**2*(16384*X**4 + 6144*X**3 + 1088*X**2 + 112*X + 1),
        X,
        domain=sp.QQ,
    )

    sos_path = ART / "p20-sos-witness.json"
    sos = json.loads(sos_path.read_text())
    a = from_terms(sos["A_terms"], (L, X))
    b = from_terms(sos["B_terms"], (L, X))
    p20_x = sp.Poly(
        sum(c * L**m[0] * X**(m[1] // 2) for m, c in p20.terms()),
        L,
        X,
        domain=sp.QQ,
    )
    if p20_x != a*a + sp.Poly(X, L, X) * b*b:
        raise RuntimeError("P20 sum-of-squares identity failed")

    resultant = sp.Poly(sp.resultant(a.as_expr(), b.as_expr(), X), L, domain=sp.QQ)
    resultant_path = ART / "p20-resultant-witness.json"
    result_data = json.loads(resultant_path.read_text())
    product = sp.Poly(sp.Integer(result_data["unit"]), L, domain=sp.QQ)
    r87 = None
    for item in result_data["factors"]:
        factor = from_terms(item["terms"], (L, X))
        factor_l = sp.Poly(factor.as_expr().subs(X, 1), L, domain=sp.QQ)
        product *= factor_l ** int(item["exp"])
        if factor_l.degree() == 87:
            r87 = factor_l
    if resultant != product or r87 is None:
        raise RuntimeError("P20 resultant factor ledger failed")
    residues = [int(r87.eval(n*(n+1))) % 23 for n in range(23)]
    if 0 in residues:
        raise RuntimeError("R87 triangular residue vanishes modulo 23")

    finite_data = matrix["first_finite_p_minus_2"]["induced_form_on_filtered_line"]
    finite = sp.Poly.from_dict(
        {tuple(m): sp.sympify(c, locals={"I": sp.I}) for m, c in finite_data["terms"]},
        (L, W),
        extension=sp.I,
    )
    q21_path = ART / "q21-finite-line-factor.json"
    q21_data = json.loads(q21_path.read_text())
    q21 = sp.Poly.from_dict(
        {tuple(m): sp.Integer(c) for m, c in q21_data["terms"]},
        (L, W),
        domain=sp.QQ,
    )
    base = (
        sp.Poly(W**51 * L**3 * (L-2)**5, L, W, extension=sp.I)
        * p6**2 * p20 * q21
    )
    quotient = finite.exquo(base)
    if quotient.total_degree() != 0:
        raise RuntimeError("finite-line factorization left a nonconstant quotient")
    q21_x = sp.Poly(
        sum(c * L**m[0] * X**(m[1] // 2) for m, c in q21.terms()),
        L,
        X,
        domain=sp.QQ,
    )
    leading_x = sp.factor(q21_x.as_poly(X).LC())
    leading_quotient = sp.cancel(leading_x / ((5*L+8)*(L+2)))
    if L in leading_quotient.free_symbols:
        raise RuntimeError("Q21 leading x coefficient has an unclassified physical zero")

    output = {
        "schema_version": "polar-canonical-pivot-wall-v1",
        "input_hashes": {
            "matrix": sha(ART / "oscillatory-matrix-filtration.json"),
            "p20_sos": sha(sos_path),
            "p20_resultant": sha(resultant_path),
            "q21": sha(q21_path),
        },
        "p6": {
            "identity": "P6=Delta*conjugate(Delta)",
            "identity_verified": True,
            "imaginary_zero_condition": "Lambda=128*x^2+24*x+3",
            "real_part_on_imaginary_zero_locus": sp.sstr(forced_real.as_expr()),
            "positive_for_x_gt_0": True,
        },
        "p20": {
            "identity": "P20=A^2+x*B^2",
            "identity_verified": True,
            "A_term_count": len(a.terms()),
            "B_term_count": len(b.terms()),
            "resultant_identity_verified": True,
            "resultant_factorization": "unit*Lambda^3*(Lambda-2)^3*R87(Lambda)",
            "R87_degree": r87.degree(),
            "R87_triangular_residues_mod_23": residues,
            "nonzero_for_Lambda_ell_ell_plus_1_ell_ge_2_x_gt_0": True,
        },
        "disposition": "EMPTY_CANONICAL_PIVOT_WALL_ON_PHYSICAL_DOMAIN",
        "invariance_boundary": "The chosen extra-complement pivot is nonzero everywhere physical, but detK itself is lift-sensitive; only the full current rank and filtered radical are congruence invariants.",
        "finite_line": {
            "factorization": "C*omega^51*Lambda^3*(Lambda-2)^5*P6^2*P20*Q21(Lambda,omega^2)",
            "constant_C": sp.sstr(quotient.as_expr()),
            "identity_verified": True,
            "Q21_term_count": len(q21.terms()),
            "Q21_bidegree": [q21_x.degree(L), q21_x.degree(X)],
            "generic_disposition": "NONRADICAL_AWAY_FROM_Q21_ZERO_LOCUS",
            "exact_exceptional_locus": "Q21(ell*(ell+1),omega^2)=0",
            "leading_x_coefficient": sp.sstr(leading_x),
            "leading_x_coefficient_nonzero_for_Lambda_ge_6": True,
            "real_exceptional_set_disposition": "For each physical ell the exceptional set is the finite set of positive real roots of the serialized Q21 polynomial.",
            "claim_boundary": "The full 282-term algebraic exceptional locus and its finiteness at each ell are certified. No uniform count of positive roots across ell is claimed.",
        },
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
