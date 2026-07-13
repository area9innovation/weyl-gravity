#!/usr/bin/env python3
"""C2i: exact cyclic homological-perturbation isometry fixture.

The fixture uses the suspended even-pairing convention

    q^sharp=-q,  s^sharp=-s,  Delta^sharp=-Delta

and the repository contraction convention

    j p = 1-q s-s q,  p j=1.

Consequently the Basic Perturbation Lemma uses

    I=(1+s Delta)^-1 j,
    P=p(1+Delta s)^-1.

An eight-dimensional exact Krein complex is constructed by mixing a
four-dimensional cohomology block with a four-dimensional contractible block
through a rational G-unitary rotation.  The dressing is genuinely nontrivial
and the transferred differential is nonzero.  The script verifies cyclicity,
I^sharp=P, P I=1, I^sharp I=1, and skew-adjointness of the transferred
differential.  It also checks that the wrong minus-sign BPL convention fails
the chain-map identities.

This is an algebraic fixture, not a construction of the pure-Weyl local BV
pairing or contraction.
"""

from __future__ import annotations

import argparse

import sympy as sp


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def sharp(
    operator: sp.Matrix,
    source_form: sp.Matrix,
    target_form: sp.Matrix,
) -> sp.Matrix:
    """Adjoint of ``operator: source -> target`` for exact Hermitian forms."""

    return sp.simplify(
        source_form.inv() * operator.conjugate().T * target_form
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-pure-weyl-bv",
        action="store_true",
        help="fail closed: this finite fixture is not the pure-Weyl BV retract",
    )
    args = parser.parse_args()
    if args.claim_pure_weyl_bv:
        raise SystemExit(
            "pure-Weyl fields, antifields, pairing, zero modes, and Hodge data are not encoded"
        )

    # A four-dimensional split form.  N maps the first isotropic plane to the
    # second, while S is its contracting inverse on the image.  Both are
    # exactly skew-adjoint for G4.
    symplectic_two = sp.Matrix([[0, 1], [-1, 0]])
    form_four = sp.zeros(4)
    form_four[:2, 2:] = symplectic_two
    form_four[2:, :2] = -symplectic_two
    nilpotent = sp.zeros(4)
    nilpotent[2, 0] = 1
    nilpotent[3, 1] = 1
    inverse_on_image = sp.zeros(4)
    inverse_on_image[0, 2] = 1
    inverse_on_image[1, 3] = 1
    zero_four = sp.zeros(4)
    identity_four = sp.eye(4)

    check(
        "C2i-F1: reduced and contractible forms are exact nondegenerate involutions",
        form_four == form_four.conjugate().T
        and form_four**2 == identity_four
        and form_four.det() != 0,
    )
    check(
        "C2i-F1: contractible differential and homotopy are skew-adjoint",
        sharp(nilpotent, form_four, form_four) == -nilpotent
        and sharp(inverse_on_image, form_four, form_four) == -inverse_on_image,
    )

    form_full = sp.diag(form_four, form_four)
    q = sp.diag(zero_four, nilpotent)
    s = sp.diag(zero_four, inverse_on_image)
    inclusion = sp.Matrix.vstack(identity_four, zero_four)
    projection = sp.Matrix.hstack(identity_four, zero_four)
    identity_full = sp.eye(8)

    check(
        "C2i-F2: base cyclic SDR obeys j^sharp=p",
        sharp(inclusion, form_four, form_full) == projection,
    )
    check(
        "C2i-F2: base differential and homotopy are skew-adjoint",
        sharp(q, form_full, form_full) == -q
        and sharp(s, form_full, form_full) == -s,
    )
    check(
        "C2i-F2: base data obey p j=1 and j p=1-q s-s q",
        projection * inclusion == identity_four
        and inclusion * projection == identity_full - q * s - s * q,
    )
    check(
        "C2i-F2: normalized SDR side conditions hold exactly",
        s**2 == sp.zeros(8)
        and s * inclusion == sp.zeros(8, 4)
        and projection * s == sp.zeros(4, 8),
    )

    # Rational G-unitary mixing makes the perturbation and its HPL dressing
    # nontrivial.  The conjugated total differential is nilpotent and cyclic.
    cosine = sp.Rational(3, 5)
    sine = sp.Rational(4, 5)
    rotation = sp.Matrix.vstack(
        sp.Matrix.hstack(cosine * identity_four, sine * identity_four),
        sp.Matrix.hstack(-sine * identity_four, cosine * identity_four),
    )
    target_diagonal = sp.diag(-nilpotent, nilpotent)
    total_q = sp.simplify(rotation * target_diagonal * rotation.conjugate().T)
    perturbation = sp.simplify(total_q - q)
    check(
        "C2i-F3: mixing is exactly G-unitary",
        rotation.conjugate().T * form_full * rotation == form_full,
    )
    check(
        "C2i-F3: total differential is nonzero, nilpotent, and skew-adjoint",
        total_q != sp.zeros(8)
        and total_q**2 == sp.zeros(8)
        and sharp(total_q, form_full, form_full) == -total_q,
    )
    check(
        "C2i-F3: cyclic perturbation satisfies Delta^sharp=-Delta",
        perturbation != sp.zeros(8)
        and sharp(perturbation, form_full, form_full) == -perturbation,
    )
    check(
        "C2i-F3: cyclic factors obey (s Delta)^sharp=Delta s",
        sharp(s * perturbation, form_full, form_full) == perturbation * s,
    )

    left_inverse = identity_full + s * perturbation
    right_inverse = identity_full + perturbation * s
    dressed_inclusion = sp.simplify(left_inverse.inv() * inclusion)
    dressed_projection = sp.simplify(projection * right_inverse.inv())
    transferred_q = sp.simplify(projection * perturbation * dressed_inclusion)
    check(
        "C2i-F4: plus-sign BPL dressing is genuinely nontrivial",
        left_inverse.det() == sp.Rational(49, 625)
        and right_inverse.det() == sp.Rational(49, 625)
        and dressed_inclusion != inclusion
        and transferred_q != sp.zeros(4),
    )
    check(
        "C2i-F4: dressed maps are exact chain maps",
        total_q * dressed_inclusion == dressed_inclusion * transferred_q
        and dressed_projection * total_q == transferred_q * dressed_projection,
    )
    check(
        "C2i-F4: cyclic dressing gives I^sharp=P and P^sharp=I",
        sharp(dressed_inclusion, form_four, form_full) == dressed_projection
        and sharp(dressed_projection, form_full, form_four) == dressed_inclusion,
    )
    check(
        "C2i-F4: P I=1 and hence I^sharp I=1 exactly",
        dressed_projection * dressed_inclusion == identity_four
        and sharp(dressed_inclusion, form_four, form_full)
        * dressed_inclusion
        == identity_four
        and dressed_inclusion.conjugate().T
        * form_full
        * dressed_inclusion
        == form_four,
    )
    check(
        "C2i-F4: transferred differential is nilpotent and skew-adjoint",
        transferred_q**2 == sp.zeros(4)
        and sharp(transferred_q, form_four, form_four) == -transferred_q,
    )
    check(
        "C2i-F4: transferred differential also equals P Q I",
        transferred_q
        == sp.simplify(dressed_projection * total_q * dressed_inclusion),
    )

    # Negative control: with jp=1-qs-sq, substituting the opposite BPL signs
    # leaves inverses and PI well defined here but destroys both chain maps.
    wrong_inclusion = sp.simplify(
        (identity_full - s * perturbation).inv() * inclusion
    )
    wrong_projection = sp.simplify(
        projection * (identity_full - perturbation * s).inv()
    )
    wrong_q = sp.simplify(projection * perturbation * wrong_inclusion)
    check(
        "C2i-F5: wrong minus-sign convention fails both chain-map identities",
        total_q * wrong_inclusion != wrong_inclusion * wrong_q
        and wrong_projection * total_q != wrong_q * wrong_projection,
    )

    print("full/reduced dimensions: 8 4")
    print("plus-sign inverse determinant:", left_inverse.det())
    print("transferred differential:", transferred_q)
    print("transferred Gram:", dressed_inclusion.conjugate().T * form_full * dressed_inclusion)
    print("CONFORMAL C2i CYCLIC HPL ISOMETRY: ALL PASS")


if __name__ == "__main__":
    main()
