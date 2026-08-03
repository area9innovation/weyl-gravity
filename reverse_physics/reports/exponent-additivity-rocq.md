# Their independence assumption survives the loss of the count

**Certificate** `REVERSE_PHYSICS_EXPONENT_ADDITIVITY_ROCQ_V1`
**Proof** `rocq/ReversePhysicsExponentAdditivity.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 18 green (0 red)`
**Closes** `REVERSE_PHYSICS_EXPONENT_ADDITIVITY`

## What was stated but not proved

The relational certificate claimed, in prose, that Carcassi–Aidala's
`#states = ∏ #confDOF` should transpose to **additivity of the exponent**. It is
now proved.

## Stating additivity without logarithms

"Exponent" suggests a logarithm, which would leave the rationals and break the
exactness this whole stream depends on. It isn't needed.

If `g_A = 2^{d_A}` and `g_B = 2^{d_B}`, then

```
exponents add     ⟺     g_AB = g_A · g_B
```

because `2^{d_A + d_B} = 2^{d_A}·2^{d_B}`. **The multiplicative statement about
generating numbers *is* the additive statement about exponents**, and it is
exactly rational. `Qpower_plus` supplies the last step over `ℤ` exponents.

## The proof

Composite regions are products, the composite dilation acts diagonally, and the
relative count factorises across independent subsystems — that last hypothesis
being precisely the translation of their independence assumption. Then

```
f_AB(t) = f_A(t) · f_B(t)        hence      g_AB = g_A · g_B
```

and `independent_subsystems_add_their_exponents` assembles it: the composite of
two independent subsystems carries the **sum** of their exponents.

The gate carries a control asserting the composite keeps only *one* subsystem's
exponent; it is rejected. So independence genuinely **adds** rather than
inheriting.

## What it settles

`#states = ∏ #confDOF` is a product of **counts**, and counts do not exist in a
conformally invariant theory. The assumption doesn't die with them — it
transposes. The relative count factorises, so the single number generating each
subsystem's scaling multiplies, which is to say **the exponents add**.

## The arc is complete

Five certificates now form one argument about their DOF-counting conjecture:

| | result |
|---|---|
| density branch | closed by **parity** in odd dimension |
| counting branch | invariant but **uninformative** |
| non-additive branch | **refuted** — every ball ties, additivity never used |
| what replaces it | a **single scaling exponent** |
| their assumption | **transposed** — independence becomes exponent additivity |

## What this does not establish

- **The factorisation itself is a hypothesis.** That the relative count
  factorises across independent subsystems is what is being *transposed*, not
  what is being proved. Deriving it would be a different result.
- **Integer exponents on dyadic scales only.** A real exponent needs a
  regularity argument this stream doesn't have.
- **The exponent is still not shown positive or equal to a dimension.**
  Monotonicity remains unassumed.
- Nothing about curved configurations, non-constant conformal factors, or extra
  structure.
- No claim about GR or its dynamics; not a reproduction or refutation of
  Carcassi–Aidala's derivation.

## Next gate

**None declared.** The arc from their trilemma to the transposed assumption is
complete. What remains — real-valued exponents, monotonicity, curved carriers —
are refinements rather than findings.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.exponent_additivity_rocq --check
```

## Tier receipt

- **Tier 0/1** — thirteen modules compile; gate 18 green / 0 red from a clean
  tree; `coqchk` empty axiom section; thirteen provenance records hash-verified;
  30-test Python suite green.
- **Tier 2/3 — not run, and not required.**
