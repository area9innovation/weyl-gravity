# Conformal P4b: energy-six intermediate-state certificate

## Scope and result

The executable certificate is
`symbolic/verify_conformal_quartic_intermediates.py`.  It concerns the
parity-reduced energy-six target in the common

```text
SO(4) = SU(2)_L x SU(2)_R irrep (2,2),
```

or `(4,4)` in doubled-spin notation, with reduced channels

```text
AA = A3+ A3-,
EA = E2+ A4- + parity,
EL = E2+ L4- + parity.
```

Their inherited oscillator-Fock signs are `(+,-,-)`.  The certificate uses
the normalizable local gauge-reduced oscillator towers

```text
E: Delta=n,   (2j_L,2j_R)=(n+2 chi,n-2 chi), sign +,
A: Delta=n+1, (2j_L,2j_R)=(n+chi,n-chi),   sign -,
L: Delta=n+2, (2j_L,2j_R)=(n+2 chi,n-2 chi), sign -,
```

where `n=2J>=2` and `chi=+/-1`.  These towers are not yet certified as the
full compact-cylinder BRST cohomology: the global conformal/Taub reduction
may exclude, dress, or combine them.  Contractible gauge, lapse, shift and
Weyl representatives are discussed separately below.

The answer has three layers:

1. **There is no one-particle `E/A/L` oscillator candidate** in the selected
   `(2,2)` block.
2. **The raw three-particle image of the cubic Hamiltonian is infinite.**
   It consists of finitely many affine spin families, each of which has an
   unbounded spin parameter.
3. **The connected one-internal-line tree subset is finite after the final
   target projection.**  The remaining infinite high-pair families are
   loop/self-energy or reducible external-state contractions.

Thus a finite bordered Green-function archive can certify the connected
tree exchange only after that convention is stated.  It is not the complete
unqualified quantum operator `P V3 Q (H0-6)^(-1) Q V3 P`.

## Cubic particle-number sectors

A normal-ordered cubic Hamiltonian acting on a two-particle state has
particle-number changes `-1,+1,+3`, giving one-, three- and five-particle
states.  At second order:

* the one-particle sector contains the old-fashioned `s` ordering;
* the three-particle sector contains the old-fashioned `t/u` orderings as
  well as two-internal-line self-energy/loop contractions;
* the five-particle sector comes from creating three particles while both
  initial particles remain spectators.  Its return graph is a disconnected
  vacuum bubble multiplying the external state and is absent from the
  normalized connected four-point operator.

It is therefore incorrect either to omit the three-particle sector or to
identify every three-particle state with a loop.  The final `P` projection
and the Wick-contraction topology make the distinction.

## No one-particle oscillator candidate

Every one-particle `E` or `L` irrep has

```text
abs(2j_L-2j_R)=4,
```

and every `A` irrep has difference two.  The selected target irrep `(4,4)`
has difference zero.  Consequently no state in the enumerated `E/A/L`
oscillator towers at any compact energy can carry the target quantum numbers:

```text
Q_1,osc = empty.
```

In particular there is no enumerated energy-six one-particle oscillator to move
from `Q` to `P`.  This does **not** say that the full gauge-fixed metric
Hessian has no component in `(2,2)`: constrained or BRST-contractible field
components can occur and are retained by the bordered Green function.

## Exact classification of the raw three-particle image

Fix a constituent

```text
X=(branch x, n_x, chi_x)
```

and replace it at one cubic vertex by

```text
B=(b,N,chi_b),   C=(c,N+delta,chi_c).
```

Let `d_E=d_L=2`, `d_A=1`, and write

```text
r_L=n_x+chi_x d_x,   r_R=n_x-chi_x d_x,
a=chi_b d_b,         c0=chi_c d_c.
```

The two lower triangle inequalities are exactly

```text
abs(a-c0-delta) <= r_L,
abs(-a+c0-delta) <= r_R.
```

They put `delta` in a finite interval.  The two parity/integrality
conditions are

```text
delta+a+c0-r_L = 0 mod 2,
delta-a-c0-r_R = 0 mod 2.
```

For every surviving `delta`, the upper triangle inequalities only impose

```text
N >= max(
  2, 2-delta,
  ceil((r_L-delta-a-c0)/2),
  ceil((r_R-delta+a+c0)/2)
).
```

Hence each row is an **infinite affine tail**, not a finite list.  The
script also applies bosonic symmetric-square parity and removes `EEE/EEX`
vertices using the exact Einstein-subsector selection rule.  An exhaustive
brute enumeration through `n=12` agrees exactly with the closed affine
classification; the cutoff check is a regression, while the inequalities
above are the all-spin proof.

For one chirality representative of each target route, the complete tail
counts are:

| target incidence | affine tails | branch-pair counts | intermediate Fock signs `(+,-)` | minimum `Delta_Q` |
| --- | ---: | --- | --- | ---: |
| `AA`, split `A3` | 17 | `EA:4, EL:4, AA:3, AL:4, LL:2` | `(8,9)` | 8 |
| `EA`, split `E2` | 7 | `AA:3, AL:2, LL:2` | `(0,7)` | 10 |
| `EA`, split `A4` | 28 | `EA:8, EL:6, AA:4, AL:8, LL:2` | `(14,14)` | 8 |
| `EL`, split `E2` | 7 | `AA:3, AL:2, LL:2` | `(0,7)` | 10 |
| `EL`, split `L4` | 11 | `EA:2, EL:2, AA:3, AL:2, LL:2` | `(7,4)` | 8 |

The four naive additional identical-pair entries in the `A4` row lie in an
antisymmetric square and are absent for bosonic creation operators.  Parity
maps every displayed tail to its conjugate and leaves its compact energy and
Fock sign unchanged.  A fixed parity target uses the corresponding parity
combination rather than doubling the reduced multiplicity.

Running

```bash
python3 symbolic/verify_conformal_quartic_intermediates.py --show-families
```

prints every branch, chirality, `delta`, exact lower bound, Fock sign and
semisimple denominator.

## Explicit all-spin witnesses

The infinity is not inferred from cutoff growth.  For every integer `N>=2`
the following exact SO(4) containments give intermediate states.  Mode
subscripts here are compact energies.

| route | exact split and spectator | `Delta_Q` | sign | `Delta_Q-6` |
| --- | --- | ---: | ---: | ---: |
| `AA` | spectator `A3-`; `A3+ -> E_N+ A_(N+1)+` | `2N+4` | `+` | `2N-2` |
| `EA/E` | spectator `A4-`; `E2+ -> A_(N+1)+ A_(N+1)+` | `2N+6` | `-` | `2N` |
| `EA/A` | spectator `E2+`; `A4- -> E_N- A_(N+2)-` | `2N+4` | `-` | `2N-2` |
| `EL/E` | spectator `L4-`; `E2+ -> A_(N+1)+ A_(N+1)+` | `2N+6` | `-` | `2N` |
| `EL/L` | spectator `E2+`; `L4- -> A_(N+1)- A_(N+1)-` | `2N+4` | `+` | `2N-2` |

The conjugate five families follow by parity.  Since all their compact
energies exceed six, compact `D` is semisimple on these oscillator towers and
their exact
resolvents are ordinary numbers

```text
1/(Delta_Q-6).
```

No flat-space `P_0` Jordan nilpotent belongs in these denominators.

## The energy-six `P`, not `Q`, incidence

Before the Einstein selection rule is imposed, there is exactly one
representation-allowed on-shell three-particle incidence in the chosen
chirality component:

```text
EL / split L4-:
E2+ spectator,   L4- -> E2- E2-,   Delta_Q=2+2+2=6.
```

Parity supplies its conjugate.  This state belongs to the `E2^3` portion of
the complete `P6` shell and must be projected into `P` before any inverse is
formed.  Its cubic current vanishes because `LEE` contains exactly one
non-Einstein direction, but that zero does not license the denominator
`1/(6-6)`.

After Einstein selection every oscillator-candidate affine tail starts at
energy eight or ten.  Thus all retained candidate `Q` denominators are
nonzero.

## Finite connected tree subset

Consider initial particles `(a,b)` and final particles `(c,d)`.  One `t/u`
old-fashioned ordering has

```text
a -> c + q,       b spectator,
b + q -> d,       c spectator,
```

so its three-particle intermediate is `(b,c,q)`.  The internal oscillator mode
must satisfy simultaneously

```text
rep(a) in rep(c) tensor rep(q),
rep(d) in rep(b) tensor rep(q).
```

Both tensor products involve fixed external irreps.  In particular every
doubled component of `q` is at most the sum of two external components,
which is at most eight here.  The final `P` projection therefore selects a
finite subset of the raw infinite image.

After parity completion and the Einstein selection rule, the exact oscillator-
candidate counts are:

| reduced direction | candidates | energy multiplicities | sign multiplicities |
| --- | ---: | --- | --- |
| `AA -> AA` | 4 | `10:4` | `-:4` |
| `AA <-> EA` | 8 in each direction | `8:2, 10:4, 12:2` | `+:4, -:4` |
| `EA -> EA` | 8 | `8:2, 10:2, 12:2, 14:2` | `-:8` |
| every direction involving `EL` | 0 oscillator candidates | -- | -- |

The nonempty candidate triples, one representative plus parity where
appropriate, are:

```text
AA -> AA:
  A3+ A3+ A4+/-                         Delta=10, sign -

AA <-> EA:
  A3- A3+ E2+                           Delta= 8, sign +
  A3+ A3+ A4-                           Delta=10, sign -
  A3+ A5+ E2+                           Delta=10, sign +
  A3+ A4+ A5-                           Delta=12, sign -

EA -> EA:
  A4- E2+ E2+                           Delta= 8, sign -
  A6+ E2+ E2+                           Delta=10, sign -
  A4- A4- A4-                           Delta=12, sign -
  A4+ A4+ A6-                           Delta=14, sign -
```

These are representation-level oscillator candidates.  A reduced `6j`
coefficient or the dynamical Weyl vertex may still set an entry to zero.
The absence of an oscillator candidate in an `EL` direction does not imply
that the full gauge-fixed exchange vanishes: constrained and contractible
components can mediate it.

## Why the raw tower is infinite but a bordered tree graph is finite

The explicit high-spin families split one low external particle into two
high particles and later fuse the same two particles back.  Between the two
vertices there are two internal lines.  They are one-loop self-energy or
external-state-reducible contractions, with the other external particle as
a spectator.  They genuinely occur in the full quantum Feshbach operator

```text
P V3 Q (Q H0 Q-6)^(-1) Q V3 P,
```

but they are not a connected one-internal-line tree exchange.

By contrast, the covariant four-wave tree construction forms a cubic
current from a fixed pair of external harmonics and contracts two currents
with one gauge-bordered quadratic Green function.  Each external harmonic
belongs to a finite SO(4) irrep, so its pair current has a finite harmonic
decomposition.  The bordered inverse then includes, in one calculation,

* the finite oscillator-candidate one-line exchanges;
* their positive/negative-frequency old-fashioned orderings;
* lapse, shift, longitudinal and Weyl-constraint components;
* the compensation needed for external Ward and internal-gauge
  independence.

It does not include the two-line one-loop self-energy tower merely by being
a gauge-complete one-line propagator.

Accordingly there are two honest specifications:

### Connected tree-level P4 certificate

State explicitly that the cubic Hamiltonian is normal ordered; retain only
connected Wick contractions with one internal line; cancel the five-particle
vacuum bubble; and subtract/LSZ-normalize external self-energy and reducible
terms.  Then the contact plus gauge-bordered one-line Green calculation is
the correct finite object.  The finite oscillator-candidate list above is a
completeness cross-check, not a replacement for the contractible sectors of
the bordered solve.

### Full order-coupling-squared quantum effective Hamiltonian

Do not use a finite intermediate archive.  The exchange must be represented
as the regulated spectral series

```text
sum_family sum_N sum_magnetic
  <f|V3|Q_family,N><Q_family,N|J_Q V3|i>
  / (Delta_family(N)-6),
```

with the appropriate inverse Gram matrix, parity/Bose factors and exact
cubic reduced coefficients.  The one-loop tails require a convergence
prescription, regularization, counterterms and external-state
renormalization.  Equivalently they require the covariant two-propagator
self-energy kernels, not the single bordered propagator used for tree
exchange.

The quartic obstruction claim must say which of these two objects it tests.
The current P4 design is a **tree-level contact-plus-one-line-exchange**
calculation, so its archive should record the connected/normal-ordering and
external-state-subtraction convention explicitly.

## Certificate boundary

This result is exact representation and Fock-space bookkeeping.  It proves
the infinity/finiteness statements and the semisimple denominators, but it
does not compute a Weyl quartic contact, a cubic reduced current, a bordered
inverse, or a metric-deformation cokernel.  In particular, it prevents a
finite oscillator-candidate intermediate table from being mistaken for a complete
quantum archive while preserving the viability of the finite connected
tree calculation.
