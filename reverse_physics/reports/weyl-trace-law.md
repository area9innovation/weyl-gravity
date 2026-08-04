# N2 — the trace law, and the bridge between the two ledgers

**Certificate** `REVERSE_PHYSICS_WEYL_TRACE_LAW_V1`
**Rail** `reverse_physics/weyl_trace_law.py` — 3 metrics, 19 checks,
4/4 negative controls rejected
**Closes** the last open entry of the geometry column
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. The result

For a general quadratic curvature action over the coordinate space of the
classification,

```text
S[a,b,c] = ∫ √−g ( a·Riem² + b·Ric² + c·R² )
```

the trace of the metric variation is, at every metric tested,

```text
g^mn E_mn  =  2 (a + b + 3c) □R
```

and `a + b + 3c = 0` is **exactly** the single linear equation that the action
classification already proves cuts out the Weyl-invariant subspace
([`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md) §3.3).

So N2 is sharper than the ledger stated. It is not merely *"the trace of the
variation is a nonzero multiple of the anomaly"* — the multiple is **2**, and
the anomaly **factorises** into the Weyl-invariance functional times `□R`.

## 2. Why this is the bridge

§3.2b of the separation ledger proves the same theory has six assumptions
written as an action and five written as field equations. The move that carries
`RP-WEYL` across is

```text
RP-WEYL (the action is Weyl invariant)  ⟺  RP-TRACELESS (field equations traceless)
```

The forward direction is cheap. **The reverse direction is what needs N2**: a
vanishing multiple would make every action come out traceless and the
equivalence would be vacuous. The trace law supplies it:

| | |
|---|---|
| the multiple is `2` | **nonzero** |
| `□R ≢ 0` | **G5**, already discharged — matter-dominated FRW has `□R = −8/(3t⁴)` |
| ⟹ kernel of the trace map | `{a + b + 3c = 0}` = `span{C², E₄}` |

That kernel statement *is* `RP-WEYL ⟺ RP-TRACELESS`, with both directions.

Note what this means for the ledger's shape: **N2 and G5 need the same
witness.** A ledger that lost `G5` would silently lose `N2` too, which is a
concrete instance of why the middle column has to be visible.

## 3. The variational link is now derived, not cited

The work item recorded that

```text
δ∫√−g C² = 4∫√−g B_mn δg^mn
```

was **cited** to the Nariai product-family check and not re-derived. Here the
`C²` field-equation tensor is assembled from the quadratic pieces and compared
against this repository's **own** Bach tensor, computed independently by the
curvature engine:

```text
E^(C²)_mn = 4 B_mn          exactly, on every nonzero component
```

on a metric that is neither Einstein nor conformally flat. **The factor 4 is
computed here, not assumed** — and it agrees with the cited value. That upgrades
the field-equation layer from *characterized by definition* to *characterized by
variation*.

## 4. What is imported, and how it is validated

The closed forms of the two quadratic field-equation tensors are textbook and
are **not** derived here. They are middle-column objects, which is the point of
having a middle column. With `δS = ∫√−g E_mn δg^mn`:

```text
E^(R²)_mn   = 2R R_mn − ½g_mn R² + 2g_mn □R − 2∇_m∇_n R
E^(Ric²)_mn = −½g_mn Ric² − ∇_m∇_n R + □R_mn + ½g_mn □R + 2R_manb R^ab
```

They are validated **three independent ways** against the engine rather than
trusted:

1. **Divergence-freedom.** `∇^m E_mn = 0` for each, exactly. This is the
   Noether/diff content (`N1`'s analogue), and a wrong formula generically
   fails it. It is not decoration — **it is what fixes the sign of the Riemann
   coupling term**, whose convention differs across sources. The opposite sign
   is carried as a negative control and does fail.
2. **The Bach cross-check.** §3.
3. **The trace law itself**, holding with the *same* coefficients at metrics of
   different symmetry.

### The Lanczos step is cited

`E^(Riem²)` is not implemented independently. In `D = 4` the Gauss–Bonnet
density has identically vanishing variation, so

```text
E^(Riem²) = 4 E^(Ric²) − E^(R²)
```

~~Same content as `G4`/`N3`, already cited to `EULER_TRANSGRESSION_CERTIFICATE`'s
`delta_E4_minus_dTheta`.~~ **Now discharged** ([report](einstein-classification.md)):
that identity is exactly *"the Lanczos tensor vanishes in `D = 4`"*, and the
Lanczos tensor is there derived from the forced head plus divergence-freedom and
checked to vanish identically. The citation is upgraded.
It was in any case **not circular**: the `C²` combination built
*through* this identity is what matches `4 B_mn` against an independently
computed tensor, so the identity is cross-validated rather than assumed into the
answer. And the trace law is separately checked on the `{Ric², R²}` subspace,
where **no Lanczos input is needed at all** — that Lanczos-free part is reported
on its own row.

## 5. Degeneracy — where this kind of check dies

No single metric can see everything, so three are used and each reports what it
can and cannot witness.

| metric | `□R ≠ 0` | `B ≠ 0` | carries |
|---|---|---|---|
| `frw_matter` | ✅ | ❌ conformally flat | the trace law |
| `non_einstein_static` | ✅ | ✅ | the trace law **and** the Bach cross-check |
| `schwarzschild` | ❌ | ❌ Einstein | **nothing** |

Schwarzschild is included *precisely because it witnesses nothing*: it is
Ricci-flat so `R = 0`, `□R = 0` and both field-equation tensors vanish, and it
is Einstein so its Bach tensor vanishes too. Every check passes on it
**vacuously**, and the certificate says so with a `witnesses_nothing` flag.
Recording that is the point — it is the same trap the work item flags for the
`R²`/`Ric²` coefficients, and the one that made the first `G6` attempt look
successful when it was not.

## 6. Negative controls

| control | must break |
|---|---|
| `riemann_coupling_sign_flipped` | divergence-freedom — this is what *fixes* the convention |
| `multiple_3_instead_of_2` | the trace law |
| `weyl_functional_a_b_2c` | the trace law — if it passed, the kernel would not be the Weyl-invariant subspace |
| `C2_direction_has_nonzero_trace` | the tracelessness of the Weyl-invariant directions |

4/4 rejected.

## 7. The geometry column is now closed

| | entry | status |
|---|---|---|
| `G1` `G2` `G3` `G5` | | discharged |
| `G4` `G7` `N3` | topological | **cited**, each with its source's boundary |
| `G6` | `P = C·C̃` | **discharged** (computable clause); spanning clause cited |
| `G8` | `W±²` | **discharged, both signatures** |
| `N1` | `∇^a B_ab = 0` | discharged |
| `N2` | trace law | **discharged** — this report |

Every entry is now discharged or explicitly cited to an existing certificate
with a stated boundary. That is the first clause of the work item's stop
condition.

## 8. What this is, and is not

Exact sympy rational arithmetic, no floating point, at specific metrics. A
**discharge, not a proof** — strictly stronger than an unverified import,
strictly weaker than a theorem for all metrics.

**It is not a quantum statement.** N2 is often phrased as being about the *trace
anomaly*; what is established here is the **classical variational identity**.
Determinants, literature coefficients, beta functions, background trace
anomalies and BV master-equation breakings are distinct objects, and none of
them is this one.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.weyl_trace_law --check
# 3 metrics; 19/19 checks; 4/4 controls rejected; PASS
```

Needs the mise Python (sympy):
`~/.local/share/mise/installs/python/3.12.13/bin/python3`. Takes several
minutes, so the fast invariant rail is
`reverse_physics/tests/test_weyl_trace_law.py`.
