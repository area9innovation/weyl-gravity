# The obstruction was the safe channel: a retraction, with proof

**Certificate** `REVERSE_PHYSICS_COPRIME_CHARGE_BOUND_ROCQ_V1`
**Proof** `rocq/CoprimeHierarchyChargeBound.v` — zero axioms, 11/11 closed
**Gate** `rocq/run.sh` — `RESULT: 21 green (0 red)`
**Upstream** tango `forge/tools/physics-moyal/ghost_channel_gate.forge` — 56/56,
2 s, `verify -full`: `c==native`, ASan-clean on both backends
**Audits** `REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1` §5 — the interpretation,
not the mathematics

---

## What was claimed

The report accompanying the coprime-ratio order law read the obstruction as the
ghost's escape route:

> An obstruction at a `p:q` resonance means the cubic interaction **cannot** be
> removed by a canonical transformation: there is a genuine on-shell `q ↔ p`
> quanta conversion between the modes. That conversion is the channel through
> which the ghost sector talks to the healthy one — the perturbative mechanism
> of the instability. On that reading, the result says: **the ghost-conversion
> channel is closed at every even-`p` resonance.**

It was flagged as interpretation. It is still wrong, and it is wrong in the
direction that flatters the result — which is the kind worth catching.

## Ground 1 — the model has no ghost

`moyal.model(w1, w2)` returns

```
h0 = ½( w1·w2·p² + (w1/w2)·x² + (w2/w1)·q² + w1·w2·y² )
```

Four **pure squares** with four **positive** coefficients whenever `w1 > w2 > 0`
— and `w1 > w2` is not an assumption, it is forced by the model's own
`disc = w1² − w2² > 0`. The Forge gate certifies exactly this: term count 4, no
cross terms, every coefficient real with sign `+1`.

In mode variables it is exactly

```
to_modes(h0)  =  w1·a1·a1b  +  w2·a2·a2b
```

checked as an exact polynomial identity, both frequencies entering with a plus
sign. That is also what `ker_split` encodes when it calls a term resonant at
`Ω = (a−b)w1 + (c−d)w2 = 0`.

Whatever this model is a deformation *of*, the object in which the obstruction
is computed is bounded below. There is no ghost mode in it to protect.

## Ground 2 — the obstruction carries a positive conserved charge

This one would hold even if there were a ghost, which is what makes it the real
argument.

Write `n̂ⱼ = aⱼ·aⱼb` for the occupation of mode `j` and

```
J  =  p·n̂₁  +  q·n̂₂
```

Then for any monomial `M = a1^{n₁} a1b^{m₁} a2^{n₂} a2b^{m₂}`,

```
{ J , M }  =  i [ (n₁−m₁)·p + (n₂−m₂)·q ] · M
```

The bracket eigenvalue **is** the resonance frequency at ratio `p:q`. So:

> **`J`'s commutant is exactly the resonant sector.**

The obstruction is the kernel projection — it lives in that sector by
construction. It conserves `J` for free, and so does every other candidate: the
order law's classification says a nonnegative resonant monomial at the critical
degree is diagonal, the conversion kernel, or its conjugate, and
`every_critical_obstruction_conserves_charge` shows all three do. There is no
`J`-breaking object the obstruction could have been.

And `J` is a **positive** combination of **nonnegative** occupations, so
conserving it bounds them:

```
n₁ ≤ J/p        n₂ ≤ J/q
```

for all time, at any coupling, non-perturbatively. Nothing in that derivation
refers to the sign of either frequency in the Hamiltonian — the bracket identity
is kinematic — so **flipping mode 2 to a ghost cannot break it.**

## The contrast, which is where the intuition went wrong

The runaway structure is not conversion, it is **pair creation** `a1^q·a2^p`,
charge `(+q, +p)`. Its two contributions *add*:

| structure | charge | conserves | bounds? |
|---|---|---|---|
| conversion `a1^q·a2b^p` — **the obstruction** | `(+q, −p)` | `p·n₁ + q·n₂` | **yes** |
| pair creation `a1^q·a2^p` | `(+q, +p)` | `p·n₁ − q·n₂` | **no** |

Both facts are proved, and so is the unboundedness that makes the second row
matter: the level set of `p·n₁ − q·n₂` contains physical states with `n₁` above
any bound. The two structures conserve each other's broken charge — they are
exchanged by `a2 ↔ a2b`, which is exactly the relabelling that turns a
positive-frequency mode into a ghost.

That last observation is the sharp version of the mistake. The intuition
"conversion between a healthy mode and a ghost is how the instability
propagates" is not baseless — but it applies to the *pair-creation* channel,
and in the both-positive model that channel is never resonant. Reading the
resonant kernel as the dangerous one inverted it.

## What survives

Everything mathematical. The order law, the selection rule, the kernel-parity
clause, the even-`p` refutation, the four new instances at 5:2, 7:2, 7:3 and 9:1
— all stand exactly as certified. "The channel is closed at even `p`" remains a
true statement about the obstruction; it simply does not mean a ghost sector is
protected.

## What this does *not* establish

- **That the full Hamiltonian conserves `J`.** It does not. The raw cubic vertex
  has non-resonant terms, and those are precisely the ones `J` fails to commute
  with. The conservation statement is about the resonant sector — where the
  normal form and the obstruction live.
- **Stability of the interacting model.** A cubic potential is unbounded below
  at large amplitude regardless of any charge. What is refuted is the specific
  claim that the *obstruction* is the destabilising channel.
- **Anything about a genuine Pais–Uhlenbeck ghost Hamiltonian.** Ground 1 says
  the coded model does not have one. Analysing one is the successor gate.
- **The bracket action from the implementation.** In Rocq, `{J,M} = i·freq·M` is
  the *definition* of `freq`; the Forge gate certifies it as a polynomial
  identity on all 70 monomials of total degree ≤ 4 at four loci. That is a
  check, not a derivation from `mpoly`.
- **Anything about Weyl gravity**, the BV–BFV complex, or the residual classes.

## The successor question

`GHOST_MODEL_OBSTRUCTION` — redo the deformation with a genuinely indefinite free
Hamiltonian `h0 = w1·n̂₁ − w2·n̂₂` and ask whether the obstruction structure
changes. Under `a2 ↔ a2b` the conversion kernel becomes pair creation, so the
two models plausibly see **mirror-image obstruction loci**. If that is right, the
coprime hierarchy is a statement about *which channel is resonant* — not about
stability at all, in either model.

## Verification

```bash
cd rocq && ./run.sh                                   # 21 green (0 red)
PYTHONPATH=. python3 -m reverse_physics.charge_bound_rocq --check

# upstream, in tango:
cd forge && FORGE_LIB=$PWD/lib forge -run -I tools/physics-moyal \
    tools/physics-moyal/ghost_channel_gate.forge      # exit 56, ~2 s
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    tools/physics-moyal/ghost_channel_gate.forge      # c==native, asan clean
```

## A note on method

The first attempt at this audit was a numerical integration of the equations of
motion. It ran for ten minutes without finishing and produced two spurious
"runaways" that were integrator artefacts, visible only because the drift of `J`
had blown up to `3×10⁻¹` while the converged runs held it at `10⁻¹³`.

Rewritten as an exact polynomial identity in Forge it runs in **two seconds**,
certifies a strictly stronger statement, and cannot produce an artefact at all.
The Science Forge law that exact and numeric are distinct types is not
bookkeeping — here the numeric rail was actively misleading, and the exact one
was faster.

## Tier receipt

- **Tier 0/1** — sixteen Rocq modules compile; gate 21 green / 0 red; `coqchk`
  axiom section `<none>`; 126/126 `Print Assumptions` closed; seventeen
  fail-closed negative controls, two of them new for this result; fifteen
  provenance records hash-verified.
- **Upstream** — `ghost_channel_gate.forge` 56/56 in 2 s, `verify -full`
  `c==native`, ASan-clean on both backends.
- **Tier 2/3 — not run, and not required.** This adds a module and a gate; it
  changes no shared operator, schema, or generated artifact that another
  certificate chain consumes. The two certificates it touches are both
  re-derived and hash-checked above.
