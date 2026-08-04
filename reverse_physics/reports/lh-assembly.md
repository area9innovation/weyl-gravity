# L_H assembled — and why sharper `|A_in|` cannot close the ghost question

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle `CLASSIFIED`.
Nothing here is `LORENTZIAN-CAUSAL`; nothing is promoted.

The black-hole programme states the ghost criterion as a property of a single
matrix: a common incoming fundamental symmetry exists **iff** `L_H` is
diagonalizable with `spec(L_H) ⊂ (0,1)`. It also records, in its own
missing-object ledger, that it cannot form `L_H` — the full typed

    T₋ : (XH0a, XH0b, EH0) → (XI0, XI1, EI0)

is uncertified; only its determinant, existence and invertibility are.

This assembles `L_H` from the committed exact data plus the transported `|A_in|`,
and settles what that does and does not decide.

## The assembly is right — checked exactly in ω, not sampled

The three factor channels are **RH (spin-2), SH (spin-1), EH (spin-2)** — which is
why `det T₋` carries `A_in,2` twice and `A_in,1` once. Their exact endpoint
normalisation ratios multiply to the programme's own prefactor:

    (h_RH/i_RI)(h_SH/i_SI)(h_EH/i_EI) = −(2ω−i)(4ω−i)²/(4(ω−i)) = C(ω)

And then the identity worth having:

    det H_out / det G₋ = (1024ω⁶+384ω⁴+36ω²+1) / (16(ω²+1)) = |C(ω)|²    exactly, all ω
    ⟹  det L_H = 1 / (|A_in,2|⁴ |A_in,1|²)

**Neither Gram was derived with the other in view.** The incoming null-flux Gram
and the future-horizon outward Gram are separate certificates from separate
constructions, and they agree through the endpoint ratios to reproduce the
committed determinant formula. That is a cross-check on both, and on this
assembly — the role the Wronskian identity plays for the transport.

Eight exact symbolic checks, two sabotage controls (perturbing one Gram entry,
perturbing one endpoint ratio) each caught with specific attribution.

## The criterion is not excluded

`inertia(G₋) = inertia(H_out) = (1,2,0)`.

This is a genuine necessary condition, not a coincidence. If `L_H` is
diagonalizable, `G`-self-adjoint and positive-spectrum, its eigenspaces are
mutually `G`-orthogonal and `K_H = G L_H` restricts to `λᵢ·G` on each, so
`inertia(K_H) = inertia(G)`. And `K_H = A†H_out A` is congruent to `H_out`, so
`inertia(K_H) = inertia(H_out)`. Equality is forced — and it holds.

So the criterion is not ruled out a priori.

## The criterion is not determined either — and that is the finding

`det L_H` is **blind to the strictly-triangular part of `T₋`**. That is precisely
why the programme could bound the determinant without the full matrix. The
**spectrum is not blind to it**, and both verdicts are attainable:

| off-diagonal | `spec(L_H)` |
|---|---|
| generic | complex-conjugate pair, plus an eigenvalue above 1 — **fails** |
| a witness choice | `0.800430, 0.950254, 0.995022` — real, in `(0,1)` — **passes** |

The witness's product is `0.756826`, which *is* the certified
`1/(|A_in,2|⁴|A_in,1|²)` — as it must be, since the determinant is the one thing
the missing block cannot move.

## What this says about our own work

**Sharpening `|A_in|` further cannot close the ghost question.** `|A_in|` fixes
`det L_H`, hence the *product* of the eigenvalues; it says nothing about where
they sit individually. The precision campaign that produced
`det(L_H) ∈ [0.659, 0.883]` was worth doing — it is an independent confirmation
of the programme's `0 < det < 0.9787` — but it is not on the critical path to the
criterion, and no further step count changes that.

The decisive object is the off-diagonal block, and the route to it is a different
computation from the one we built: **transport the coupled three-frame of the
triangular module**, rather than the two decoupled scalar RW factor equations.
The graded-mesh validated-ODE machinery carries over; the system does not.

## What this does not establish

- that `spec(L_H) ⊂ (0,1)` for the physical cell — **nor** that it is not;
- any certified value for the strictly-triangular block of `T₋`;
- diagonalizability of `L_H`, which the criterion needs *separately* from the
  spectrum (the Jordan-inside-the-interval failure mode is real — see
  [[scattering-c-factorisation]]);
- anything Lorentzian-causal.

The numeric table above is **numeric**: floating point, one frequency, sampled
off-diagonals. It is recorded because it is what establishes that the missing
block is decisive rather than a formality — not as a claim about the cell.

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.lh_assembly --check
# PASS: REVERSE_PHYSICS_LH_ASSEMBLY_V1 -- 8 exact checks, imports pinned
```

Needs sympy; on this workstation that is the mise interpreter,
`~/.local/share/mise/installs/python/3.12.13/bin/python3`.
