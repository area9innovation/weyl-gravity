# Inertia `(1,2)`: "harmless" does not mean "no ghost"

**Certificate** `REVERSE_PHYSICS_GHOST_SIGNATURE_V1`
**Rail** `reverse_physics/ghost_signature.py` — 8/8 checks
**Extends** [`ghost-harmless.md`](ghost-harmless.md) past its stated boundary
**Dependency tag** `LOCAL-ALGEBRAIC` — imports **nothing**

---

## 1. Why this inertia

[`ghost-harmless.md`](ghost-harmless.md) showed that on the minimal ghost —
inertia `(1,1)` — three escape routes collapse to one condition. Its own boundary
said *"not higher inertia"*.

`(1,2)` is not an arbitrary next case. It is **where this repository's
black-hole programme actually works**: `lh_assembly` records
`inertia(G₋) = inertia(H_out) = (1,2,0)`, and `scattering_c_factorisation` states
the pencil criterion there. So the question is whether the `(1,1)` finding was a
small-dimension accident.

## 2. The parameterisation is supplied by the structure

With `η = diag(1,−1,−1)`, `η`-pseudo-Hermiticity `H†η = ηH` says exactly that
`ηH` is Hermitian. So

```
H = ηM,    M Hermitian
```

covers every case with no further conditions. At `(1,1)` the family had to be
written by hand; here the structure gives it.

## 3. The criterion survives

| case | real spectrum | diagonalizable | harmless |
|---|---|---|---|
| `diagonalizable_real` | ✅ | ✅ | ✅ |
| `complex_pair` | ❌ | ✅ | ❌ |
| `degenerate` | ✅ | ❌ | ❌ |

A positive-definite `J` with `H†J = JH` makes `ρ = J^½` conjugate `H` to a
Hermitian operator, so `H` is diagonalizable with real spectrum — **the same
one-line argument as at `(1,1)`, and it does not know the dimension.** The
`(1,1)` result was not an accident.

## 4. What is new, and it is the point

In the **harmless** case, the `η`-norms of the eigenvectors are

```
[ +1, −1, −1 ]
```

**Two negative-norm directions survive.** The inertia is preserved in the
eigenbasis — it must be, being an invariant of `η` — and the criterion cannot see
it.

Quasi-Hermiticity says **a positive inner product exists**. It says nothing about
how many directions were negative in the *original* one. So:

> **"Harmless" means a positive-definite inner product exists.
> It does not mean the ghost is gone.**

At `(1,1)` the distinction was invisible, because *"a ghost"* and *"one ghost"*
coincide. At `(1,2)` they come apart, and the ghost **count** is an `η`-invariant
that no amount of quasi-Hermiticity removes.

This sharpens the earlier result rather than overturning it: the three routes
really do collapse to one condition, and that condition really is weaker than
"no ghost".

## 5. What this does not establish

- **Whether replacing `η` by `J` is physically legitimate.** That is the
  Bender–Mannheim question, it is a *physics* question, and this does not answer
  it — but it is now **visibly** the question, rather than hidden by a dimension
  in which it could not be asked.
- **Nothing about Weyl gravity.** Still finite-dimensional linear algebra, now on
  a 3-dimensional Krein space. `C-GHOST-DYNAMICS` stays `OPEN`.
- **The negative direction is not by exhaustion.** A positive `J` is *exhibited*
  where one exists — constructive. Where none exists, the argument is the
  similarity argument above; the grid search is corroboration, not proof.
- **Not inertia beyond `(1,2)`**, and not the infinite-dimensional case, where
  quasi-Hermiticity additionally needs the metric bounded with bounded inverse.

---

```bash
PYTHONPATH=. python3 -m reverse_physics.ghost_signature --check
```
