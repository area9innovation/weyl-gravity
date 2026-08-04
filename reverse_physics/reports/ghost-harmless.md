# What makes a ghost harmless — three routes, one condition

**Certificate** `REVERSE_PHYSICS_GHOST_HARMLESS_V1`
**Rail** `reverse_physics/ghost_harmless.py` — 10/10 checks, 1014-point scan,
0 mismatches
**Dependency tag** `LOCAL-ALGEBRAIC` — and it imports **nothing**

> **This does not close `C-GHOST-DYNAMICS`.** It says what *harmless* requires
> structurally. Whether Weyl gravity's actual ghost satisfies it is a different
> question and stays open. §5.

---

## 1. Asking a different question

The comparison ledger's last `OPEN` row is whether the Ostrogradsky ghost
destabilises the physical sector. This stream has lost to that question twice:
it published a dynamical reading of a ghost obstruction and **retracted it with
proof**, and the successor `GHOST_MODEL_OBSTRUCTION` then showed the coprime
obstruction decides it in **neither** direction.

So don't ask it a third time. Ask the reverse-physics question:

> **What is the minimal assumption set under which a negative-norm sector is
> harmless?**

That is answerable in this stream's currency — and the answer collapses three
things usually offered as *alternatives*.

## 2. The three routes

| | route | where it appears |
|---|---|---|
| **1** | a conserved **positive charge** bounds occupations | the *surviving* half of this stream's retraction: the coprime obstruction conserves `J = p·n̂₁ + q·n̂₂`, which is positive and therefore **bounds** both occupations regardless of any ghost sign |
| **2** | **quasi-Hermiticity / PT** — `H` similar to Hermitian, so a positive-definite inner product exists | Bender–Mannheim, argued in the literature for conformal gravity specifically |
| **3** | a **positive invariant subspace** to superselect | standard Krein-space practice |

**They are the same condition.** The collapse is one line, and it's worth writing
out because it is the whole finding:

> If `H†J = JH` with `J > 0`, put `ρ = J^½`. Then `h = ρHρ⁻¹` satisfies
> `h† = ρ⁻¹H†ρ = ρ⁻¹JHJ⁻¹ρ = ρHρ⁻¹ = h`.

**A positive-definite conserved charge *is* a metric operator**, and conversely.
And a quasi-Hermitian operator is diagonalizable with real spectrum, because a
Hermitian one is. So all three reduce to

```text
DIAGONALIZABLE   AND   REAL SPECTRUM
```

## 3. The computation

The minimal ghost: a two-dimensional Krein space of inertia `(1,1)` — one
positive-norm and one negative-norm direction — with `η = diag(1,−1)`. The
`η`-pseudo-Hermitian operators are exactly

```text
H(a,d,b) = [[a, b], [−b, d]]        a, d, b real
```

`b` is the **coupling** between the two sectors. For `b ≠ 0`, everything is
decided by

```text
Δ = (a − d)² − 4b²
```

| `Δ` | spectrum | diagonalizable | positive charge | harmless |
|---|---|---|---|---|
| `> 0` | real, distinct | ✅ | **exists** | ✅ |
| `= 0` | real, repeated — Jordan | ❌ | `det J = −(j₂₂ − x)² ≤ 0` | ❌ |
| `< 0` | complex pair | ✅ | `det J` negative definite | ❌ |

Established by a **scan over 1014 rational couplings with `b ≠ 0`, zero
mismatches**, plus four explicit cases — the harmless one carrying its charge
explicitly (`j₂₂ = x = 1`, minors `3/2` and `1/2`), the others carrying their
obstruction.

**Both conditions are independent**, each witnessed inside the family:

- `H(2,0,1)` — real spectrum `{1,1}`, **Jordan**, not harmless. Witnesses
  diagonalizability.
- `H(1,0,1)` — diagonalizable, spectrum `(1 ± i√3)/2`, not harmless. Witnesses
  real spectrum.

`Δ = 0` is exactly the **PT-breaking transition** — the exceptional point where
the two eigenvectors collide.

### The edge case, carried as a case rather than a caveat

`H(3,3,0)` has `Δ = 0` yet **is** harmless: with `b = 0` the sectors decouple,
`H` is a multiple of the identity, every Hermitian `J` intertwines, and `J = I`
works. So the *discriminant* form of the criterion needs `b ≠ 0`; the
*diagonalizable-and-real-spectrum* form holds everywhere. Since `b` is the
coupling, `b = 0` is the case where there's nothing to be harmless about.

### A tempting statement that is not claimed

It looks as though `det J` is a binary quadratic form whose **own** discriminant
*is* `Δ` up to a positive factor — which would make one number decide the
spectrum and the charge by algebra rather than by scan. The ratio computed on
the symbolic branch does not reproduce the one computed at numeric points,
because sympy parameterizes the solution space differently there. **So the
identity is recorded as `not_claimed`.** The scan and the cases establish the
criterion without it.

## 4. This is the criterion the repository already uses

Not a new one — a reason for two things already known here.

`scattering_c_factorisation` records the pencil criterion as *"`L_H`
diagonalizable with `spec(L_H) ⊂ (0,1)`"* — **the same two conditions** — and its
report records that a **Jordan failure mode had been missed**, where the spectrum
lies inside the interval but the operator is not diagonalizable. That missed mode
is `Δ = 0`.

`weyl_ghost_dipole` computed the degenerate case directly: a dipole's commutant
is only `a·I + b·N`, so `det(Gη) = −g²a²` is never positive. This module gives
the reason, and shows the two are one statement.

Both are cited as context. **This module imports nothing.**

## 5. What this does not establish

Stated first in the certificate, because the gap is larger than the result.

- **Nothing about Weyl gravity's actual field-theoretic ghost.** This is
  finite-dimensional linear algebra on a two-dimensional Krein space. It says
  what "harmless" *requires*; it does not say whether the theory satisfies it.
  **`C-GHOST-DYNAMICS` stays `OPEN`.**
- **No Lorentzian quantum theory** in which the question could even be posed —
  the programme's claim boundary says one does not exist here.
- **Not the infinite-dimensional case.** Quasi-Hermiticity there needs the metric
  operator bounded with bounded inverse, a genuine analytic condition with no
  finite-dimensional counterpart.
- ~~**Not higher inertia.**~~ **`(1,2)` is now done**
  ([report](ghost-signature.md)) — the criterion survives, and the extension
  sharpens what it means: in the harmless case the `η`-norms of the eigenvectors
  are `[+1,−1,−1]`, so **two negative-norm directions survive**. "Harmless" means
  a positive-definite inner product *exists*, **not** that the ghost is gone.
  Inertia beyond `(1,2)` is still not computed.
- **Showing the three routes coincide is not showing the condition holds.**

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.ghost_harmless --check
# 1014 scan points, 0 mismatches; 4 cases; 10/10; PASS
```

Needs the mise Python (sympy).
