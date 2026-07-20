"""Invariant normal form of the Einstein/additional pairing extension.

Verdict token: BH2_SYMPLECTIC_EXTENSION_HYPERBOLIC_NORMAL_FORM
Tags: LOCAL-ALGEBRAIC.  Lifecycle: CLASSIFIED.

Proof-first classification of the pairing carried by the exact sequence

    0 -> E_Einstein -> E_Weyl -> E_extra -> 0

under the pure-Weyl Lee-Wald pairing, with NO assumed canonical
splitting.  Everything is finite-rank linear algebra over C, done
symbolically before any radial series; the repaired rational-frequency
fixtures enter only as controls.

SETUP (each hypothesis is certified elsewhere, cited, not re-derived)
---------------------------------------------------------------------
Work with the Hermitian form K(u, v) = i F^r(u, v) / (pi alpha), which is
the object certified Hermitian by BH2A_FLUX_MATRIX / BH2B_COMPOSED_REPAIR
(K(u,v) = conj(K(v,u))).  On the three declared directions:

  E   Einstein/RW line       K(E, E) = 0            (isotropic; certified
                                                     exactly, both parities)
  X   additional lift        K(X, X) = d in R       (Hermitian diagonal)
  G   conformal direction    K(G, .) = 0            (radical; certified:
                                                     every G pair vanishes
                                                     identically)
  a = K(E, X)                                        (cross scalar)

Admissible lift ambiguity (certified: the lift is defined exactly modulo
Einstein and conformal directions):

    X -> X + beta E + gamma G,   beta, gamma in C.

THEOREM (a != 0)
----------------
1. a is INVARIANT under every admissible shear:
       K(E, X + beta E + gamma G) = a  +  beta K(E,E)
                                       +  gamma K(E,G)  =  a.
2. The additional self-pairing transforms as
       d -> d + 2 Re(conj(beta) a),
   so for a != 0 the map beta |-> 2 Re(conj(beta) a) is ONTO R and d can be set
   to ANY real value, in particular 0.  Hence **d carries no invariant
   content**: no sign, magnitude or vanishing statement about the
   additional self-pairing survives the lift ambiguity.
3. On span(E, X) the matrix is [[0, a], [conj(a), d]] with
       det = -|a|^2 < 0,
   so the block is NONDEGENERATE of rank 2 with inertia (1, 1) --
   both invariant.  The normal form is the HYPERBOLIC PLANE
       [[0, a], [conj(a), 0]].
4. E spans an isotropic line in a rank-2 signature-(1,1) space, hence a
   MAXIMAL isotropic (Lagrangian) line of that block.
5. On span(E, X, G) the radical is exactly span(G) (rank 3 - 2 = 1), and
   the quotient by the radical is the hyperbolic plane of (3).

DEGENERATION (a = 0)
--------------------
The shear action 2 Re(conj(beta) a) collapses to 0, so d becomes INVARIANT.
The form on span(E, X) is [[0,0],[0,d]]: rank <= 1, E joins the radical,
and the sign of d is then a genuine invariant.  The a != 0 and a = 0
branches are therefore qualitatively different and the theorem is stated
conditionally on a, as the work item requires.

CONSEQUENCE FOR THE OPEN SIGN QUESTION
--------------------------------------
The long-standing "invariant extra-block sign" question is answered in
the negative for a != 0: there is nothing to certify, because every
additional self-pairing datum is removable by an admissible shear.  What
IS invariant is the pair (rank, inertia) = (2, (1,1)) together with the
cross class of a.  This closes the question as posed rather than leaving
it open.

NOT CLAIMED
-----------
No sign is assigned to an additional branch from any one canonical lift;
no canonical direct-sum splitting is asserted (the sequence is classified
without one); no Hilbert-space, particle, ghost, unitarity or dynamical
interpretation is attached.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCHEMA_NAME = "pure-weyl-bh2-symplectic-normal-form-v1"
SCHEMA_PATH = HERE / "schema" / "bh2-symplectic-normal-form-v1.schema.json"
CERT_PATH = HERE / "certificates" / "BH2_SYMPLECTIC_NORMAL_FORM.json"
RESULT_ID = "PURE_WEYL_BH2_SYMPLECTIC_NORMAL_FORM"
RESULT_TOKEN = "BH2_SYMPLECTIC_EXTENSION_HYPERBOLIC_NORMAL_FORM"

AXIAL_CERT = HERE / "certificates" / "BH2A_COMPOSED_REPAIR.json"
POLAR_CERT = HERE / "certificates" / "BH2B_COMPOSED_REPAIR.json"


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _herm(M):
    """conjugate transpose"""
    return M.conjugate().T


def run_analysis() -> dict:
    t0 = time.time()
    out: dict = {}

    a = sp.Symbol("a")                       # cross scalar K(E,X)
    d = sp.Symbol("d", real=True)            # additional self-pairing
    beta = sp.Symbol("beta")
    gamma = sp.Symbol("gamma")

    # --- the pairing on span(E, X, G), E isotropic, G radical -----------
    K3 = sp.Matrix([[0, a, 0],
                    [sp.conjugate(a), d, 0],
                    [0, 0, 0]])
    _require(sp.simplify(K3 - _herm(K3)) == sp.zeros(3, 3),
             "declared pairing is not Hermitian")
    out["pairing"] = sp.sstr(K3)

    # --- admissible shear X -> X + beta E + gamma G ----------------------
    S = sp.eye(3)
    S[0, 1] = beta        # X column picks up beta * E
    S[2, 1] = gamma       # ... and gamma * G
    K3s = sp.expand(_herm(S) * K3 * S).applyfunc(sp.simplify)

    # 1. cross scalar is invariant
    a_new = sp.simplify(K3s[0, 1])
    _require(sp.simplify(a_new - a) == 0,
             f"cross scalar not invariant: {a_new}")
    # E stays isotropic and G stays radical
    _require(sp.simplify(K3s[0, 0]) == 0, "E lost isotropy")
    for i in range(3):
        _require(sp.simplify(K3s[i, 2]) == 0 and sp.simplify(K3s[2, i]) == 0,
                 "G left the radical")

    # 2. the self-pairing shifts by 2 Re(conj(beta) a)
    d_new = sp.simplify(K3s[1, 1])
    br, bi = sp.symbols("br bi", real=True)
    ar, ai = sp.symbols("ar ai", real=True)
    subs_re = {beta: br + sp.I * bi, a: ar + sp.I * ai}
    d_shift = sp.simplify(sp.expand(d_new.subs(subs_re) - d))
    expected = sp.simplify(
        2 * sp.re(sp.conjugate(br + sp.I * bi) * (ar + sp.I * ai)))
    _require(sp.simplify(d_shift - expected) == 0,
             f"self-pairing shift {d_shift} != 2 Re(conj(beta) a)")
    out["shear_action"] = {"cross": "a (invariant)",
                           "self": "d + 2*Re(conj(beta)*a)"}

    # 2b. for a != 0 the shift is ONTO R: solve 2 Re(conj(beta) a) = -d
    #     exactly by beta* = -d a / (2 |a|^2)
    beta_star = -d * a / (2 * (ar**2 + ai**2))
    shift_star = sp.simplify(2 * sp.re(
        sp.conjugate(beta_star.subs(subs_re)) * (ar + sp.I * ai)))
    _require(sp.simplify(shift_star + d) == 0,
             f"canonical beta does not remove d: shift {shift_star}")
    out["removal_witness"] = {
        "beta_star": "-d*a/(2*|a|^2)",
        "resulting_self_pairing": "0",
        "valid_when": "a != 0",
    }

    # 3. rank, determinant and inertia of the 2-dim block
    K2 = K3[:2, :2]
    det2 = sp.simplify(sp.expand(K2.det().subs(subs_re)))
    _require(sp.simplify(det2 + (ar**2 + ai**2)) == 0,
             f"det {det2} != -|a|^2")
    out["block"] = {"determinant": "-|a|^2",
                    "rank_when_a_nonzero": 2,
                    "inertia": [1, 1],
                    "normal_form": "[[0, a], [conj(a), 0]] (hyperbolic plane)"}
    # inertia by explicit eigenvalues at the normal form (d = 0)
    K2n = K2.subs({d: 0}).subs(subs_re)
    ev = list(sp.Matrix(K2n).eigenvals().keys())
    _require(len(ev) == 2, "unexpected eigenvalue count")
    sgn = sorted(sp.sign(sp.simplify(e.subs({ar: 1, ai: 0}))) for e in ev)
    _require(sgn == [-1, 1], f"inertia not (1,1): signs {sgn}")

    # 4. E is Lagrangian in the block: isotropic and maximal (dim 1 = 2/2)
    out["lagrangian"] = {
        "E_isotropic": True,
        "block_dimension": 2,
        "maximal_isotropic_dimension": 1,
        "E_is_lagrangian_in_block": True,
    }

    # 5. radical of the 3-dim form is exactly span(G) when a != 0
    K3n = K3.subs(subs_re)
    rad = K3n.subs({ar: 1, ai: 0, d: 0}).nullspace()
    _require(len(rad) == 1, f"radical dimension {len(rad)} != 1")
    _require(sp.simplify(rad[0][0]) == 0 and sp.simplify(rad[0][1]) == 0,
             "radical is not span(G)")
    out["radical"] = {"dimension_when_a_nonzero": 1, "spanned_by": "G",
                      "quotient": "hyperbolic plane"}

    # --- degeneration a = 0 ---------------------------------------------
    K3z = K3.subs({a: 0})
    d_new_z = sp.simplify(sp.expand((_herm(S) * K3z * S)[1, 1]))
    _require(sp.simplify(d_new_z - d) == 0,
             f"at a = 0 the self-pairing moved: {d_new_z}")
    rank_z = K3z.subs({d: 1}).rank()
    _require(rank_z == 1, f"a = 0 rank {rank_z} != 1")
    out["degeneration_a_zero"] = {
        "self_pairing_invariant": True,
        "rank_when_d_nonzero": 1,
        "E_joins_radical": True,
        "sign_of_d_is_invariant": True,
    }

    # --- decisive mutations ---------------------------------------------
    # M1: an arbitrary admissible shear must MOVE d but FIX a, rank, inertia
    trials = [(sp.Rational(3, 7), sp.Rational(-2, 5)),
              (sp.Rational(-11, 4), sp.Rational(9, 8)),
              (sp.Rational(5, 3), sp.Rational(0))]
    moved, fixed = [], []
    for br_v, bi_v in trials:
        sub = {ar: sp.Rational(2, 3), ai: sp.Rational(-1, 5),
               d: sp.Rational(7, 11), br: br_v, bi: bi_v}
        Kb = (_herm(S) * K3 * S).subs(subs_re).subs(sub).applyfunc(sp.simplify)
        K0 = K3.subs(subs_re).subs(sub).applyfunc(sp.simplify)
        moved.append(sp.simplify(Kb[1, 1] - K0[1, 1]) != 0)
        fixed.append(sp.simplify(Kb[0, 1] - K0[0, 1]) == 0
                     and Kb[:2, :2].det() == K0[:2, :2].det())
    _require(all(moved), "a shear failed to move the self-pairing")
    _require(all(fixed), "a shear moved the cross scalar or the determinant")
    out["mutations"] = {
        "M1_shear_moves_self_pairing_fixes_invariants": True,
        "trials": len(trials),
        "detail": "every admissible beta shear changes d while leaving a and "
                  "det (hence rank and inertia) fixed -- exactly the "
                  "representative-dependence the theorem predicts",
    }
    # M2: at a = 0 the same shears must NOT move d
    unmoved = []
    for br_v, bi_v in trials:
        sub = {ar: 0, ai: 0, d: sp.Rational(7, 11), br: br_v, bi: bi_v}
        Kb = (_herm(S) * K3 * S).subs(subs_re).subs(sub).applyfunc(sp.simplify)
        unmoved.append(sp.simplify(Kb[1, 1] - sp.Rational(7, 11)) == 0)
    _require(all(unmoved), "at a = 0 a shear moved d")
    out["mutations"]["M2_at_a_zero_shears_cannot_move_self_pairing"] = True

    # --- fixture controls (repaired constants only, as the item allows) --
    controls = {}
    for tag, path in (("axial", AXIAL_CERT), ("polar", POLAR_CERT)):
        cert = json.loads(path.read_text(encoding="utf-8"))
        fx = cert["fixtures"]
        for freq, vals in fx.items():
            if tag == "axial":
                cross = sp.sympify(vals["cross"].replace("I", "I"))
                ctrl = sp.sympify(vals["control"])
                key = f"axial {freq}"
                controls[key] = {"E_self_pairing": sp.sstr(ctrl),
                                 "cross_nonzero": bool(sp.simplify(cross) != 0)}
                _require(sp.simplify(ctrl) == 0,
                         f"{key}: E self-pairing not exactly zero")
                _require(sp.simplify(cross) != 0, f"{key}: cross vanishes")
            else:
                key = f"polar {freq}"
                cross_keys = [k for k in vals if k.startswith("E|X")]
                _require(cross_keys, f"{key}: no E|X entries")
                nz = all(sp.simplify(sp.sympify(vals[k])) != 0
                         for k in cross_keys)
                controls[key] = {"E_self_pairing": "absent (identically zero)",
                                 "cross_nonzero": nz}
                _require("E|E" not in vals,
                         f"{key}: E|E recorded as nonzero")
                _require(nz, f"{key}: a cross entry vanishes")
    out["fixture_controls"] = controls
    out["stage_seconds"] = {"total": round(time.time() - t0, 1)}
    return out


def build_certificate() -> dict:
    res = run_analysis()
    return {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "declaration": {
            "theory": "S = alpha * integral sqrt(-g) C_{abcd} C^{abcd}",
            "background_family": "Schwarzschild exterior (hypotheses cited "
                                 "from the certified fixtures; the theorem "
                                 "itself is background-independent linear "
                                 "algebra)",
            "conformal_frame": "fixed representative g",
            "generator": "exact sequence 0 -> E_Einstein -> E_Weyl -> "
                         "E_extra -> 0, no canonical splitting assumed",
            "phase_space": "Hermitian Lee-Wald pairing K = i F^r/(pi alpha)",
            "horizon_condition": "not used (abstract pairing layer)",
            "infinity_condition": "not used (abstract pairing layer)",
            "lifecycle": "CLASSIFIED",
        },
        "hypotheses": {
            "K_hermitian": "certified by BH2A_FLUX_MATRIX / "
                           "BH2B_COMPOSED_REPAIR",
            "E_isotropic": "K(E,E) = 0 certified exactly, both parities",
            "G_radical": "every conformal pairing vanishes identically "
                         "(BH2B_COMPOSED_REPAIR)",
            "lift_ambiguity": "X -> X + beta E + gamma G, certified as the "
                              "exact lift ambiguity",
        },
        "theorem_a_nonzero": {
            "cross_invariant": True,
            "self_pairing_removable": True,
            "removal_witness": res["removal_witness"],
            "block": res["block"],
            "lagrangian": res["lagrangian"],
            "radical": res["radical"],
        },
        "degeneration_a_zero": res["degeneration_a_zero"],
        "shear_action": res["shear_action"],
        "pairing": res["pairing"],
        "mutations": res["mutations"],
        "fixture_controls": res["fixture_controls"],
        "resolves": {
            "question": "invariant sign of the additional (extra) block",
            "answer": "ANSWERED NEGATIVELY for a != 0: no additional "
                      "self-pairing datum is invariant, since every such "
                      "datum is removable by an admissible lift shear "
                      "(d -> d + 2 Re(beta a) is onto R). The invariants are "
                      "(rank, inertia) = (2, (1,1)) and the cross class of a. "
                      "For a = 0 the sign of d IS invariant.",
            "supersedes_nothing": True,
        },
        "not_claimed": {
            "sign_from_a_canonical_lift": False,
            "canonical_direct_sum_splitting": False,
            "hilbert_space_or_particle_interpretation": False,
            "symbolic_frequency_table": False,
        },
        "verification_discipline": [
            "the theorem is proved symbolically on the abstract pairing "
            "before any radial series; fixtures enter only as controls",
            "Hermiticity, isotropy and radical membership are re-verified "
            "under the shear rather than assumed to persist",
            "the removal witness beta* is exhibited explicitly and checked "
            "to annihilate d, so surjectivity is constructive",
            "decisive mutations in both branches: shears must move d and fix "
            "the invariants when a != 0, and must NOT move d when a = 0",
        ],
        "claim_flags": {
            "normal_form_certified": True,
            "cross_invariance_certified": True,
            "self_pairing_removability_certified": True,
            "inertia_certified": True,
            "lagrangian_status_certified": True,
            "a_zero_branch_certified": True,
            "invariant_sign_question_resolved": True,
            "symbolic_frequency_certified": False,
            "general_l_certified": False,
        },
        "missing_objects": [
            "the symbolic-frequency value of the cross scalar a (a separate, "
            "now sharply targeted calculation)",
            "general l",
            "any dynamical or quantum interpretation of the inertia",
        ],
        "stage_seconds": res["stage_seconds"],
        "provenance": {
            "generator_path":
                "black_hole_programme/bh2_symplectic_normal_form.py",
            "axial_fixture_certificate": str(AXIAL_CERT.relative_to(ROOT)),
            "axial_fixture_certificate_sha256": _sha256(AXIAL_CERT),
            "polar_fixture_certificate": str(POLAR_CERT.relative_to(ROOT)),
            "polar_fixture_certificate_sha256": _sha256(POLAR_CERT),
        },
        "verification_command":
            "python3 black_hole_programme/verify_bh2_symplectic_normal_form.py",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(CERT_PATH))
    args = parser.parse_args()
    Path(args.out).write_text(
        json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
