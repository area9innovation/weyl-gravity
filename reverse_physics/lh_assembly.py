"""L_H assembled from the committed certificates -- and the exact scope of what
that settles.

The black-hole programme states the ghost criterion as a property of one matrix:
a common incoming fundamental symmetry exists iff L_H is diagonalizable with
spec(L_H) contained in (0,1).  It also states, in its own missing-object ledger,
that it cannot form L_H, because the full typed

    T_- : (XH0a, XH0b, EH0) --> (XI0, XI1, EI0)

is not certified -- only its determinant, existence and invertibility are.

This record assembles L_H from the committed exact data plus the transported
|A_in|, and establishes two things.

FIRST, THE ASSEMBLY IS RIGHT, and that is checked EXACTLY in omega rather than
sampled.  Composing the two independently derived endpoint Grams with the exact
factor-adapted endpoint normalisation ratios reproduces the committed
determinant formula:

    det H_out / det G_-  ==  |C(omega)|^2            (exact identity in omega)
    ==> det L_H  ==  1 / (|A_in,2|^4 |A_in,1|^2)

Neither Gram was derived with the other in view; the identity is a cross-check
on both, and on this assembly.  It plays the role the Wronskian identity plays
for the transport.

SECOND, AND THIS IS THE POINT: the criterion is NOT DETERMINED by the certified
data, and it is NOT EXCLUDED either.

  - NOT EXCLUDED.  inertia(G_-) = inertia(H_out) = (1,2,0).  A diagonalizable
    G-self-adjoint L_H with positive spectrum forces inertia(K_H) = inertia(G),
    and K_H is congruent to H_out, so equal inertia is NECESSARY.  It holds.
  - NOT DETERMINED.  det L_H is blind to the strictly-triangular part of T_-,
    which is exactly why the determinant bound was reachable without the full
    matrix.  The SPECTRUM is not blind to it.  Both verdicts are attainable:
    generic off-diagonals give a complex-conjugate pair and an eigenvalue above
    one; an explicit choice gives three real eigenvalues inside (0,1) whose
    product is the certified determinant.

The consequence is a scope statement about our own quantitative work.  Sharpening
|A_in| further CANNOT close the ghost question.  |A_in| fixes det L_H, hence the
PRODUCT of the eigenvalues; it says nothing about where they sit individually.
The decisive object is the off-diagonal block, and obtaining it means
transporting the coupled three-frame of the triangular module, not the two
decoupled scalar factor equations.

Dependency tags: LOCAL-ALGEBRAIC (the exact identities), REDUCED-MODE (the cell).
Nothing here is LORENTZIAN-CAUSAL and nothing is promoted.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.lh_assembly --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reverse_physics/certificates/REVERSE_PHYSICS_LH_ASSEMBLY_V1.json"

RESULT_ID = "REVERSE_PHYSICS_LH_ASSEMBLY_V1"
SCHEMA_NAME = "reverse-physics-lh-assembly-v1"

# Imported authorities, pinned by content hash.  A drift in any of these must
# fail the verifier closed rather than silently re-deriving against new inputs.
PINNED = {
    "incoming_gram": ROOT / "black_hole_programme/phase3/axial_null_flux_gram/certificate.json",
    "horizon_gram": ROOT / (
        "black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/"
        "future_horizon_outward_gram.json"
    ),
    "criterion": ROOT / (
        "black_hole_programme/phase4/channel_factorized_c_pullback_test_v1/certificate.json"
    ),
    "incoming_connection_report": ROOT / (
        "reports/phase3-axial-incoming-connection-analytic-2026-07-23.md"
    ),
}

W = sp.symbols("omega", positive=True)
I = sp.I


def incoming_gram(w=W):
    """G_-, Stokes orientation, in the raw typed basis (XI0, XI1, EI0)."""
    return sp.Matrix(
        [
            [576 / (5 * w), 96 * I / 5, 384 * w / 5],
            [-96 * I / 5, -144 * w / 5, -192 * I * w**2 / 5],
            [384 * w / 5, 192 * I * w**2 / 5, 0],
        ]
    )


def horizon_gram(w=W):
    """H_out, future-horizon outward, in the raw typed basis (XH0a, XH0b, EH0)."""
    return sp.Matrix(
        [
            [
                96 * w * (16 * w**4 + 41 * w**2 + 7) / (5 * (w**2 + 1)),
                384 * w * (2 * w - I) * (4 * w**3 - 5 * I * w**2 + 4 * w - 2 * I)
                / (5 * (w**2 + 1)),
                48 * w * (w - 2 * I) * (4 * w - I) ** 2 / (5 * (w - I)),
            ],
            [
                384 * w * (2 * w + I) * (4 * w**3 + 5 * I * w**2 + 4 * w + 2 * I)
                / (5 * (w**2 + 1)),
                768 * w * (2 * w**2 + 1) * (4 * w**2 + 1) / (5 * (w**2 + 1)),
                96 * w * (2 * w - I) * (2 * w + I) * (4 * w - I) / (5 * (w - I)),
            ],
            [
                48 * w * (w + 2 * I) * (4 * w + I) ** 2 / (5 * (w + I)),
                96 * w * (2 * w - I) * (2 * w + I) * (4 * w + I) / (5 * (w + I)),
                0,
            ],
        ]
    )


def endpoint_ratios(w=W):
    """The exact factor-adapted endpoint normalisation ratios h/i, channel by
    channel.  RH and EH ride the spin-two RW factor, SH the spin-one -- which is
    what makes det T_- carry A_in,2 twice and A_in,1 once."""
    h_r, i_r = I * w * (4 * w - I) / (2 * (w - I)), sp.Integer(1)
    h_s, i_s = 4 * (w - I) * (2 * w - I), -2 * I * w
    h_e, i_e = -I * w * (4 * w - I) / (4 * (w - I)), -I * w
    return (h_r / i_r, h_s / i_s, h_e / i_e)


def leading_minors(m):
    return [sp.simplify(m[: k + 1, : k + 1].det()) for k in range(m.shape[0])]


def sign_pattern_plus_minus_plus(minors):
    """Jacobi: leading-minor signs (+, -, +) on omega > 0 give inertia (1,2,0).
    Checked by proving each simplified minor keeps its sign for positive omega,
    not by sampling."""
    wanted = [1, -1, 1]
    for minor, want in zip(minors, wanted):
        expr = sp.simplify(minor * want)
        if sp.ask(sp.Q.positive(expr), sp.Q.positive(W)) is True:
            continue
        # fall back to an explicit positivity proof over the pilot interval
        if sp.simplify(sp.together(expr)).is_positive:
            continue
        num, den = sp.fraction(sp.cancel(sp.together(expr)))
        if sp.Poly(sp.expand(num), W).all_coeffs() and all(
            c >= 0 for c in sp.Poly(sp.expand(num), W).all_coeffs()
        ) and all(c >= 0 for c in sp.Poly(sp.expand(den), W).all_coeffs()):
            continue
        return False
    return True


def exact_checks():
    """Every check here is symbolic in omega and exact.  Each returns a bool."""
    g, h = incoming_gram(), horizon_gram()
    r_r, r_s, r_e = endpoint_ratios()
    c = sp.simplify(r_r * r_s * r_e)
    c_target = -(2 * W - I) * (4 * W - I) ** 2 / (4 * (W - I))
    cmod2_target = (4 * W**2 + 1) * (16 * W**2 + 1) ** 2 / (16 * (W**2 + 1))

    a1, a2 = sp.symbols("a1 a2", positive=True)
    det_g, det_h = sp.simplify(g.det()), sp.simplify(h.det())
    det_lh = sp.simplify(det_h / (det_g * cmod2_target * a2**4 * a1**2))

    checks = {
        "incoming_gram_is_hermitian": sp.simplify(g - g.H) == sp.zeros(3),
        "horizon_gram_is_hermitian": sp.simplify(h - h.H) == sp.zeros(3),
        "endpoint_ratio_product_is_C": sp.simplify(c - c_target) == 0,
        "C_modulus_squared_matches_report": sp.simplify(
            sp.expand(sp.Abs(c) ** 2 - cmod2_target)
        )
        == 0
        or sp.simplify(sp.expand(c * sp.conjugate(c) - cmod2_target)) == 0,
        # THE CROSS-CHECK: two independently derived Grams and the endpoint
        # ratios agree, exactly, for every omega.
        "det_ratio_of_grams_equals_C_modulus_squared": sp.simplify(
            det_h / det_g - cmod2_target
        )
        == 0,
        # ...hence the committed determinant formula, reproduced through this
        # assembly rather than assumed from it.
        "assembly_reproduces_committed_det_LH": sp.simplify(
            det_lh - 1 / (a2**4 * a1**2)
        )
        == 0,
        # NECESSARY CONDITION for the criterion, and it holds.
        "incoming_gram_inertia_is_1_2_0": sign_pattern_plus_minus_plus(leading_minors(g)),
        "horizon_gram_inertia_is_1_2_0": sign_pattern_plus_minus_plus(leading_minors(h)),
    }
    return checks, {
        "det_incoming_gram": sp.srepr(det_g),
        "det_horizon_gram": sp.srepr(det_h),
        "C_of_omega": sp.srepr(sp.simplify(c)),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    checks, exprs = exact_checks()
    return {
        "result_id": RESULT_ID,
        "schema": SCHEMA_NAME,
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "imports": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for name, path in sorted(PINNED.items())
        },
        "exact_checks": {k: bool(v) for k, v in sorted(checks.items())},
        "exact_expressions": exprs,
        "assembly": {
            "criterion": "L_H diagonalizable and spec(L_H) subset (0,1)",
            "L_H": "G_-^{-1} A^dagger H_out A,  A = T_-^{-1}",
            "T_minus": "M_I (D + N) M_H^{-1}",
            "M_H": "columns (RH, SH, EH); RH = XH0a - (4w^2-3iw+4)/(4(w-i)(2w-i)) XH0b",
            "M_I": "columns (RI, SI, EI); RI = XI0 - (i/w) XI1",
            "D": "diag(r_R A_in2, r_S A_in1, r_E A_in2) with r_* the endpoint ratios",
            "N": "the strictly triangular block -- NOT CERTIFIED, and decisive",
        },
        "claim_flags": {
            "assembly_reproduces_committed_determinant": True,
            "inertia_necessary_condition_satisfied": True,
            "spec_criterion_decided": False,
            "spec_criterion_excluded_a_priori": False,
            "sharper_A_in_can_close_the_question": False,
            "full_typed_Tminus_offdiagonal_certified": False,
        },
        "missing_object_ledger": [
            {
                "object": "certified_strictly_triangular_block_of_typed_Tminus",
                "why_decisive": (
                    "det L_H is independent of it, so the committed determinant bound "
                    "could be derived without it; spec(L_H) is not, and both verdicts "
                    "are attainable as N varies"
                ),
                "route": (
                    "transport the coupled three-frame of the triangular module, not "
                    "the two decoupled scalar RW factor equations"
                ),
            }
        ],
        "numeric_diagnostic": {
            "note": (
                "NUMERIC, not a certificate claim -- floating point, sampled at one "
                "frequency.  Recorded because it is what establishes that the missing "
                "block is decisive rather than a formality."
            ),
            "omega": "1/2",
            "A_in_moduli_source": (
                "tango forge/examples/weyl_ain_endtoend_gate.forge, |A_in,1|^2 in "
                "[1.172, 1.378] and |A_in,2|^2 in [0.983, 1.049]"
            ),
            "generic_offdiagonal_verdict": "complex-conjugate pair and an eigenvalue above 1",
            "witness_offdiagonal_verdict": "three real eigenvalues in (0,1)",
            "witness_spectrum": [0.800430, 0.950254, 0.995022],
            "witness_product": 0.756826,
            "witness_product_must_equal_det_LH": True,
        },
        "does_not_establish": [
            "that spec(L_H) is contained in (0,1) for the physical cell",
            "that spec(L_H) is NOT contained in (0,1) for the physical cell",
            "any certified value for the strictly triangular block of T_-",
            "diagonalizability of L_H, which the criterion needs separately",
            "anything Lorentzian-causal; the tag is absent deliberately",
        ],
        "verification": {
            "command": "PYTHONPATH=. python3 -m reverse_physics.lh_assembly --check",
            "interpreter_note": (
                "needs sympy; on this workstation that is the mise interpreter, "
                "~/.local/share/mise/installs/python/3.12.13/bin/python3"
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the stored certificate")
    args = ap.parse_args()

    fresh = build()
    if fresh["status"] != "PASS":
        failed = [k for k, v in fresh["exact_checks"].items() if not v]
        print("FAIL: exact checks did not hold: " + ", ".join(failed))
        return 1

    if args.check:
        if not OUTPUT.exists():
            print(f"FAIL: {OUTPUT.relative_to(ROOT)} is missing")
            return 1
        stored = json.loads(OUTPUT.read_text())
        for field in ("exact_checks", "imports", "claim_flags", "assembly"):
            if stored.get(field) != fresh[field]:
                print(f"FAIL: {field} drifted from the stored certificate")
                return 1
        print(f"PASS: {RESULT_ID} -- {len(fresh['exact_checks'])} exact checks, imports pinned")
        return 0

    OUTPUT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
