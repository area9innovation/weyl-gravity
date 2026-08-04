# G6 and G8 — the Weyl dual, in both signatures

**Certificate** `REVERSE_PHYSICS_WEYL_DUAL_DISCHARGE_V1`
**Rail** `reverse_physics/weyl_dual_discharge.py` — 4 metric/signature rows,
14 checks, 3/3 negative controls rejected
**Closes** the two entries left `BLOCKED` by
[`weyl-geometry-discharge.md`](weyl-geometry-discharge.md)
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. What was blocked, and why the first attempt failed

The geometry column discharged `G1`, `G2`, `G3`, `G5` and `N1` against this
repository's exact curvature engine and left two entries blocked:

| | |
|---|---|
| `G6` | the parity-odd quadratic invariants are spanned by `P`; `P = C·C̃` in `D = 4` |
| `G8` | `W±² = (C² ± P)/2` — the link to the certified residual classes |

A first attempt got the split *algebra* exactly right on Lorentzian Taub-NUT —
`W₊² − W₋² = P` and `W₊² + W₋² = (C² + C̃²)/2` both held at an exact algebraic
point — but `C̃² ≠ −C²`, so the ε index placement was wrong. The work item
recorded the fix as *express the dual in `quantum-weyl/local_bv/hodge.py`'s
conventions, not repair the ε by trial*.

**That instruction turned out to be half of the answer.** `hodge.py` is a formal
two-dimensional algebra on the ordered basis `(F, ⋆F)`. It fixes

```text
star_square_sign = +1 (EUCLIDEAN),  −1 (LORENTZIAN)
eigenvalues      = ±1 (EUCLIDEAN),  ±i (LORENTZIAN)
projectors       P± = (I + ⋆/λ)/2
```

and **nothing else** — in particular it never fixes the ε index placement on a
rank-four tensor, which is exactly where the error lived. So "use hodge.py's
conventions" resolves to two separate instructions: pick the index placement
that *reproduces* `star_square_sign`, and then take the projectors seriously,
**including the fact that the Lorentzian ones are complex**.

The placement that works:

```text
ε_abcd      = √|det g| · [abcd],  all indices DOWN
(⋆T)_abcd   = ½ ε_ab^ef T_efcd,   ε_ab^ef raised by g
contraction  raise ALL FOUR indices with g before summing
```

The earlier attempt raised the Weyl tensor's last two indices *before* applying
ε and then raised all four again, double-raising two slots.

The reproduction of `star_square_sign` is a **checked row**, not an assumption:

```text
(⋆C)·(⋆C) = star_square_sign · C²
```

holds on every row. That is the single check the previous attempt failed, and
everything else here depends on it.

## 2. G8 is two different statements, and one of them is not the textbook one

This is the substantive finding, and it is what the work item's `forbid`
required be stated rather than waved at.

| signature | `⋆²` | projectors | `W±` | `W±²` |
|---|---|---|---|---|
| **Euclidean** | `+1` | real | `(C ± ⋆C)/2` | `(C² ± P)/2` |
| **Lorentzian** | `−1` | **complex**, eigenvalues `±i` | `(C ∓ i⋆C)/2`, complex conjugates | `(C² ∓ iP)/2` |

Both are verified exactly, each in its own signature. And the Lorentzian row
carries an extra check that is not a remark but a computation:

```text
G8_euclidean_form_is_false_in_lorentzian_signature   →  confirmed false
```

So `W±² = (C² ± P)/2` **is a Euclidean statement**, and quoting it without the
qualification is an error, not a shorthand. The repository's claim boundary
already said the Lorentzian star squares to `−1` on two-forms so `W±` are
complex conjugates there; this discharges the consequence.

## 3. G6 — and the metric that makes it non-vacuous

The computable clause of `G6` is that the Pontryagin density depends only on
the Weyl tensor:

```text
Riem · ⋆Riem  =  C · ⋆C
```

i.e. the Ricci parts drop out of the parity-odd contraction.

**On a Ricci-flat metric this check is vacuous**, because `Riem = C`
identically — there are no Ricci parts to drop. Lorentzian Taub-NUT is a vacuum
solution, so however cleanly it passes, it establishes nothing about `G6`. This
is the same trap the work item flags for the `R²`/`Ric²` coefficients on
Schwarzschild, and the certificate records `ricci_is_nonzero` per row so a
reader can see which rows can and cannot support the claim.

`G6` is therefore carried by a **deformed Taub-NUT** — the θθ component
rescaled by `6/5`, which breaks Ricci-flatness while keeping the NUT twist that
makes `P ≠ 0`. It solves nothing, and it does not have to: a discharge needs
metrics that are non-degenerate *for the identity under test*, not metrics that
are physical.

The Euclidean member of the Taub-NUT pair also carries `G6`, for a reason worth
recording: imposing signature by flipping the twist block's sign does **not**
preserve the vacuum condition, so that metric is not Ricci-flat either.

```text
non-vacuous G6 on: taub_nut/EUCLIDEAN, deformed_taub_nut/LORENTZIAN,
                   deformed_taub_nut/EUCLIDEAN
```

**Honest limitation.** The deformed metric is a deformation of the Taub-NUT
form, not a structurally independent family. It was chosen because it keeps the
`(r, θ)` coordinate dependence that makes the exact computation cheap. A
Bianchi IX family with three distinct scale factors would be genuinely
independent; it did not finish in usable time and is not included.

## 4. Negative controls

A check that cannot fail is not a check. Each control perturbs exactly one
convention and must be **rejected**:

| control | must break |
|---|---|
| `eps_without_volume_factor` | the star square |
| `dual_prefactor_one_instead_of_one_half` | the star square |
| `real_split_in_lorentzian_signature` | the Euclidean `G8` form, in Lorentzian signature |

3/3 rejected. The third is the one that matters most: it is precisely the
mistake one makes by ignoring `hodge.py`'s complex Lorentzian eigenvalues, and
it is the shape of the original failure.

## 5. What is cited rather than discharged

Citations are sufficient when they are trustworthy, and each is carried with the
boundary its own source states.

**`G6`, spanning clause** — *the parity-odd quadratic invariants are spanned by
`P`*. A representation-theory dimension count, not a pointwise identity, so no
evaluation at metrics can establish it. Cited. The computable half is
discharged above; the spanning half is not.

**`G4`** — `∫√−g E₄` is topological.
Cited to `quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json`
(`INTRINSIC_EULER_TOWER_VERIFIED`, `LOCAL-ALGEBRAIC`), specifically its
`delta_E4_minus_dTheta` and `closed_manifold_integrated_variation` checks.
**Boundary:** this supplies the *variational* content the classification
actually uses — the integrated variation vanishes, so `E₄` contributes nothing
to the field equations. It is **not** an index theorem and **not** a global
triviality claim. The source's own `not_computed` list includes the
antifield/Koszul–Tate completion and relative cohomology nontriviality of the
Euler anomaly.

**`G7`** — `∫√−g P` is topological.
Cited to `symbolic/verify_conformal_dynamical_topological.py`, which proves the
Chern–Weil transgression `Tr(R∧R) = d Tr(ΓdΓ + ⅔Γ³)`.
**Boundary, quoted verbatim from that module:** *"Global triviality of the
Pontryagin class is explicitly not claimed."* The transgression is **local**, so
`G7` is available only in the local form the classification uses — `P`
contributes no field equations — and **not** as a statement about topological
sectors.

**`N3`** — a topological term has identically vanishing variation. This is the
*same content* as `G4`'s variational check, so it is discharged by the same
citation rather than by separate work. This is why `RP-TOPO-INERT` disappears on
the field-equation side of the ledger (§3.2b of the separation ledger).

## 6. Where the geometry column now stands

| | entry | status |
|---|---|---|
| `G1` | `C² = Riem² − 2Ric² + R²/3` | discharged |
| `G2` | conformal law for `R` | discharged |
| `G3` | Weyl conformal weight | discharged |
| `G4` | `∫√−g E₄` topological | **cited**, variational content only |
| `G5` | non-degeneracy witness | discharged |
| `G6` | `P = C·C̃` | **discharged** (computable clause) |
| `G6` | spanning | **cited** |
| `G7` | `∫√−g P` topological | **cited**, local transgression only |
| `G8` | `W±² = (C² ± P)/2` | **discharged, both signatures** |
| `N1` | `∇^a B_ab = 0` | discharged |
| `N2` | trace of the variation is a nonzero multiple of the anomaly | **discharged** ([report](weyl-trace-law.md)) |
| `N3` | topological ⟹ vanishing variation | **cited** |

~~**`N2` is the one entry still genuinely open.**~~ **`N2` is now discharged**
([`weyl-trace-law.md`](weyl-trace-law.md)) as a trace law,
`g^mn E_mn = 2(a + b + 3c)□R`, closing the geometry column: every entry is
discharged or explicitly cited to an existing certificate with a stated
boundary.

## 7. What this is, and is not

Every identity is verified **exactly** — sympy rationals, radicals and `I`, no
floating point — at **specific metrics and specific points**. That is strictly
stronger than an unverified import and strictly weaker than a theorem for all
metrics. It is a **discharge, not a proof**.

It establishes nothing about the residual classes `[W₊²]` and `[W₋²]` beyond
the algebraic split; their cohomological status is a separate result kind, and
the certified classes are centered deformation/vertex classes, not one-particle
graviton states.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.weyl_dual_discharge --check
# 4 rows OK; 3/3 controls rejected; non-vacuous G6 on 3 rows; PASS
```

Needs the mise Python (sympy): `~/.local/share/mise/installs/python/3.12.13/bin/python3`.
