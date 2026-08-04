# The ghost, the black hole, and why there is no contradiction

**Proof** `rocq/WeylGhostDipole.v` — zero axioms, 11/11 closed
**Gate** `rocq/run.sh` — `RESULT: 26 green (0 red)`, 26 fail-closed negative controls
**Joins** `REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1` (`LOCAL-ALGEBRAIC`)
with `black_hole_programme/phase4/axial_local_nonlocal_positivity_v1`
and `.../axial_all_ell_threshold_structure_v1` (`LOCAL-ALGEBRAIC`, `REDUCED-MODE`)

---

## The question

The reverse-physics line just concluded that **the ghost is forced**: the same
five assumptions that make the Weyl action unique also guarantee a negative-norm
direction, in every dimension where the theory is non-trivial.

The black-hole programme has spent a long time doing hard scattering analysis on
the Schwarzschild exterior in Weyl gravity, and it *works*. There is a
well-defined scattering map, certified invertibility of the connection matrices,
an exact all-`ℓ` threshold structure. That does not look like a theory being
destroyed by a ghost.

So which is it?

**Both, and they are the same statement seen from two ends.** The resolution is
worth stating precisely, because it is the most informative thing this line has
produced and neither programme says it alone.

## 1. What the black-hole programme actually found

Three results, all with their own certificates, quoted rather than paraphrased.

**The ghost is there, and it is populated.** The incoming null, outgoing null and
future-horizon Lee–Wald forms are each nondegenerate Hermitian with

```
inertia = (1, 2, 0)      i.e.   J = diag(1, −1, −1)
```

Three-channel **Krein** spaces. And not formally: *"the negative classical flux
directions are genuinely populated; they are not merely formal endpoint
directions"* — because both connection matrices `T±` are certified invertible on
an exact common cell.

**No local metric can fix it.** The dynamically compatible commutant of the
spin-two flux structure is

```
η = a·I + b·N,     N² = 0
G·η = [[0, g·a], [g·a, g·b]],     det = −g²·a²
```

so it is indefinite when `a ≠ 0` and degenerate when `a = 0`. The package's own
conclusion: *"no rational local dynamically compatible metric operator makes the
spin-two form positive definite."*

**But a nonlocal one exists.** *"A compatible fundamental symmetry always exists
on the combined future space"* — construct `C` on `ran(S)` by transport and
extend by orthogonal direct sum. Whether it factorises over `ℐ⁺ ⊕ ℋ⁺` is a
*separate* scattering condition, and is explicitly not claimed.

## 2. The two lines converge on the same assumption

| | reverse physics | black-hole programme |
|---|---|---|
| **object** | the space of actions | on-shell scattering data on Schwarzschild |
| **method** | conformal weight law + residue signs | Lee–Wald flux forms, connection matrices |
| **tags** | `LOCAL-ALGEBRAIC` | `LOCAL-ALGEBRAIC`, `REDUCED-MODE` |
| **conclusion** | the ghost is forced; **only `RP-LOCAL` and `RP-METRIC` can remove it** | **no *local* positive metric exists** — but a nonlocal `C` does |

The assumption lattice *predicted which of the five assumptions had to give*. The
scattering analysis, computed independently on a real background with entirely
different machinery, found **exactly that one giving**.

That is not a coincidence to be admired, it is a check. An assumption ledger is
worth something only if its "load-bearing" verdicts survive contact with hard
analysis. Here one did.

> **The tags are not merged.** Neither result is promoted by the other. The
> black-hole certificates carry `REDUCED-MODE`, and per the programme's claim
> boundary a `REDUCED-MODE` computation is never evidence for a
> `LORENTZIAN-CAUSAL` claim. What is recorded is a *convergence*: evidence about
> where to look, not a theorem about the Lorentzian theory.

## 3. My "next gate" had already been done — better

`WeylGhostForced.v` closed with an honest gap. The theorems covered two *distinct*
simple poles, but Weyl gravity's actual kinetic operator is `□²` — a **double**
pole. That the degenerate case is no better was cited to Riegert, not proved, and
I flagged it as the load-bearing citation, with the successor gate:

> prove the Jordan block admits no positive-definite inner product — exact
> linear algebra on a 2×2 nilpotent block over ℚ.

That computation was already in this repository, done on Schwarzschild in the
odd-parity spin-two sector, with the physics attached. `WeylGhostDipole.v` now
abstracts it into the reverse-physics chain as a machine-checked theorem, so the
citation is discharged:

- the commutant of a rank-two Jordan block is `a·I + b·N` — **two** parameters,
  not four, which is why the obstruction cannot be evaded;
- `det(G·η) = −g²a²`, never positive;
- `a ≠ 0` → indefinite, with explicit ℚ-vectors giving `+1` and `−1`;
- `a = 0` → degenerate, with the first basis vector in the radical;
- and the first basis vector is null for **every** admissible `η`, which kills
  definiteness of either sign before any case analysis.

**The mathematics is the black-hole programme's.** What is added is that it now
sits in the chain as a theorem rather than a reference, and that its abstract
form is visibly the same object the assumption lattice pointed at.

## 4. Why the resonance structure survives anyway

This is the part that looks paradoxical and is not.

An indefinite metric makes *norms* indefinite. It does not make the *dynamics*
ill-posed. The black-hole analysis is about invertibility, analyticity and
transport — none of which care about the sign of a Gram form. Concretely, at
`ω = 0`, for **every** `ℓ ≥ 2` and spins 1 and 2:

> *"no nonzero solution is both horizon regular and bounded/decaying at
> infinity"*

— **no zero-energy resonance**, proved exactly by reducing the static equation to
the Gauss hypergeometric equation with `(a,b,c) = (s−ℓ, −s−ℓ, −2ℓ)` and
`z = 2/r`, with the regular solution in closed form and horizon normalisation
`φ(2) = 1` by Chu–Vandermonde. The second solution is logarithmically singular at
the horizon; a decaying choice at infinity behaves as `r^{−ℓ}`; they cannot be
the same solution.

The threshold behaviour is clean, for all `ℓ`, *in a theory with a certified
ghost sector*. So:

> **The ghost is unavoidable and locally incurable, and it is not fatal to the
> dynamics. What it costs is that positivity becomes nonlocal.**

That is a coherent physical picture, and it is exactly what the assumption
lattice says it should be: the theory is fine except along `RP-LOCAL`, and
`RP-LOCAL` is where the price is paid.

## 5. So is any of this new?

Being straight about it, because the honest answer is what makes the rest worth
reading.

- **The Weyl-action classification: not new.** Textbook. The value was the ledger.
- **"Fourth order implies a ghost": not new.** Ostrogradsky, Stelle.
- **The dipole computation: not new to this repository** — the black-hole
  programme had it. New only in being abstracted and machine-checked here.
- **The all-`ℓ` nonresonance and the Krein structure: the black-hole
  programme's**, already certified.

What *is* new is the **join**, and it is the kind of thing that becomes visible
only once the assumptions are laid out:

1. an assumption lattice that names `RP-LOCAL` as the load-bearing assumption for
   the ghost, **before** looking at the scattering data;
2. an independent, background-specific analysis that finds precisely that: no
   local positive metric, a nonlocal one available;
3. the observation that these are the same statement, with the abstract side now
   discharging its one citation using the concrete side's computation;
4. and the consequent picture — ghost forced, locally incurable, dynamically
   survivable, positivity nonlocal — which neither programme states.

That is not a theorem. It is an orientation, and it said where the next theorem
should be: **whether the nonlocal `C` factorises over `ℐ⁺ ⊕ ℋ⁺`.**

> **That question has since been reduced to a finite test** —
> [`scattering-c-factorisation.md`](scattering-c-factorisation.md). It is a 3×3
> generalised eigenvalue problem; the single missing input is explicit `T₊`; and
> two witnesses matching every certified inertia answer oppositely, so nothing
> weaker can settle it. Which is the orientation paying off.

## What this does not establish

- **No Lorentzian claim.** The black-hole certificates are `REDUCED-MODE`; this
  document records a convergence and promotes nothing. None of the five objects
  the quantum claim boundary lists as non-existent are asserted here.
- **The Jordan structure is not derived from Weyl gravity** in
  `WeylGhostDipole.v`. That a dipole *is* a rank-two Jordan block is the standing
  input; the black-hole package is where it was computed for a real background.
- **Nothing about whether the nonlocal `C` is physical.** Its existence is an
  extension-by-direct-sum argument. Factorisation is open, and the package says
  so.
- **Nothing about the BV–BFV complex, the residual classes, the physical
  spectrum, or the quantum theory.** The two scoped Lorentzian no-go theorems are
  neither used nor affected.
- **The nonresonance result is `ω = 0`, spins 1 and 2, `M = 1`.** It is not a
  decay statement, and the package's own `does_not_establish` lists the
  uniform low-frequency Jost asymptotics as not certified.
- **Re-running the black-hole verifiers is reproduction, not verification.**
  They pass, and their content is hash-pinned here, but a producer agreeing with
  itself establishes nothing new. This document inherits whatever those
  certificates got wrong; what it adds is an independent route to the same
  conclusion on the abstract side.

## Provenance of the imported side

The black-hole certificates are hashed, quoted **and independently re-run.**
Their verifiers need `sympy`, which lives under the mise Python 3.12 toolchain
rather than the system interpreter — the first attempt used `/usr/bin/python3`
(3.14, no `sympy`) and failed, which is worth recording because it is the kind of
thing that quietly becomes "not verified" in a report.

```
EXACT_LOCAL_NONLOCAL_POSITIVITY_DICHOTOMY_VERIFIED      (0.4 s)
PASS: independent all-ell threshold verification
AXIAL_QNM_CONSERVED_SOURCE_OVERLAP_VERIFIED
```

Content hashes are recorded as well, so the provenance record fails closed if the
black-hole side drifts under this document's reading of it:

```
29cd53300a892424ec5b901ba08c994efc7d66a27cea5447e8d8200fe67c9356
    black_hole_programme/phase4/axial_local_nonlocal_positivity_v1/certificate.json
4c0ef500671231ddf8501d061921c3fc37f46c70d4d08bc2f5e80f915c560c4d
    black_hole_programme/phase4/axial_all_ell_threshold_structure_v1/certificate.json
914312759dfb77c59c188a4e2c1d7d75357993fc7f18e9d76d8afa8aeb3b99fc
    black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/certificate.json
cbe6aa1cf769e1db10e38b91506f4e37c369ee8f35e50b4b7456298fc4c707bf
    black_hole_programme/phase3/axial_global_finite_flux_channel_classification_v3/report.md
```

Producing commit for the positivity dichotomy: `e72fd8b3`.

Every quotation in §1 and §4 is verbatim from those files. If a hash no longer
matches, this document's reading of the black-hole side is stale and must be
re-checked before being relied on — `weyl_ghost_dipole.py --check` enforces that.

Re-running their verifiers is *reproduction*, not independent verification, and
is recorded as such. The independent check on this side is the Rocq module, which
reaches the same conclusion by a different route.

## Verification

```bash
cd rocq && ./run.sh                                   # 26 green (0 red), 198/198 closed

# the imported side, re-hashed (needs no sympy):
sha256sum black_hole_programme/phase4/axial_local_nonlocal_positivity_v1/certificate.json           black_hole_programme/phase4/axial_all_ell_threshold_structure_v1/certificate.json

# and re-run properly, in an environment that has sympy:
python3 -m black_hole_programme.phase4.axial_local_nonlocal_positivity_v1.verify
python3 -m black_hole_programme.phase4.axial_all_ell_threshold_structure_v1.verify
```
