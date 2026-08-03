# The fourth desideratum lands: a parity obstruction

**Certificate** `REVERSE_PHYSICS_CONFORMAL_COUNT_ROCQ_V1`
**Proof** `rocq/ReversePhysicsConformalCount.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 15 green (0 red)`

## What it engages

Carcassi and Aidala's degree-of-freedom counting trilemma
([*Reverse Physics for GR*](https://assumptionsofphysics.org/presentations/20241116-UMichRelativity.pdf), 16 Nov 2024):

> 1. every point is a single DOF · 2. finite volume carries finitely many ·
> 3. the count is additive — **"Pick two!"**

Their resolutions: drop 1 → a density measure; drop 2 → the counting measure;
drop 3 → a non-additive "quantum measure". They drop 3 for quantum mechanics and
conjecture quantum gravity does the same for the DOF count.

## The correction to our own earlier framing

We previously said conformal invariance "kills desideratum 2". **That was
wrong.** Conformal invariance is not a fourth item in the trilemma at all — it is
a **filter on which resolutions are admissible**. Getting that right is what
turned an observation into a theorem.

## The theorem

Under `g → Ω²g` with constant `Ω`, a local scalar built polynomially from the
metric, its inverse, the Riemann tensor and covariant derivatives is fixed — *for
weight purposes* — by `m` curvature factors and `D` derivative indices. Every
index is contracted in a pair, so `D` is even, and

```
weight = 2m − 2·(4m+D)/2 = −(2m + D)      — always even
```

The volume element on a `d`-manifold has weight `+d`. A density is conformally
invariant exactly when the weights cancel:

```
2m + D = d
```

**For odd `d` there is no solution.** A Cauchy surface is three-dimensional.

`no_conformal_dof_density_on_a_cauchy_surface`. The gate carries a control
asserting such a density exists; it is rejected.

So the failure of `∫√h d³x` is not a bad choice of density. **No choice works** —
and it fails by parity, not by accident.

## The filter, applied

| branch | conformally invariant? | informative? |
|---|---|---|
| drop 1 → density measure | **no** — the theorem | yes |
| drop 2 → counting measure | yes (never sees the metric) | **no** — every infinite region alike |
| drop 3 → non-additive | not excluded | not excluded |

**An informative, conformally invariant DOF count must be non-additive.**

And that is a *convergence, not a collision*: it is the same branch quantum
mechanics forced them onto, reached here by a purely classical symmetry with no
quantum input. Their talk asks whether a DOF-count bound requires revisiting
spacetime; this says the revisitation is forced twice over, and one of the two
reasons is not quantum.

## The Weyl connection

In dimension four the balance **is** achievable: `2m + D = 4` admits
`(m, D) = (2, 0)` — a quadratic curvature invariant. That is exactly the weight
carried by `C_{abcd}C^{abcd}`, the conformally invariant action of Weyl gravity.

So conformal gravity is the even-dimensional case where a conformal density
exists, and a Cauchy surface is the odd-dimensional case where it cannot. The
theory this repository studies sits on the other side of the same parity.

## What this does not establish

- **The non-additive branch is neither constructed nor ruled out.** The density
  branch is closed; the constructive half is open.
- **Extra structure evades it.** A compensator or dilaton of nonzero weight
  breaks the parity argument — but only by choosing a scale, which is what
  conformal invariance forbids. That fork is stated, not resolved.
- **Realisability is not addressed.** The arithmetic says which weights are
  available, not which `(m, D)` are realised by an actual invariant. The negative
  result needs only the necessary condition and is unaffected; the
  dimension-four statement is about weights, not a constructed invariant.
- **Constant `Ω` only.** A full treatment carries derivative-of-`Ω` terms.
- **No claim about GR or its dynamics.** Conformal weights are kinematic.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.

## Next gate

`REVERSE_PHYSICS_NONADDITIVE_CONFORMAL_COUNT` — construct or refute a
non-additive conformally invariant DOF count. The density branch is closed and
the counting branch is uninformative, so that is where the answer must be.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.conformal_count_rocq --check
```

## Tier receipt

- **Tier 0/1** — ten modules compile; gate 15 green / 0 red from a clean tree;
  `coqchk` empty axiom section; ten provenance records hash-verified; 30-test
  Python suite green.
- **Tier 2/3 — not run, and not required.** Nothing outside `reverse_physics/`
  and `rocq/` imports or is imported by this work; no freeze, tag or promotion.
